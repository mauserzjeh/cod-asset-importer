fn unpack_565(color: u32) -> (u32, u32, u32) {
    let mut r = (color & 0xF800) >> 8;
    let mut g = (color & 0x07E0) >> 3;
    let mut b = (color & 0x001F) << 3;
    r |= r >> 5;
    g |= g >> 6;
    b |= b >> 5;

    (r, g, b)
}

fn pack_rgba(r: u32, g: u32, b: u32, a: u32) -> u32 {
    (r << 16) | (g << 8) | b | (a << 24)
}

fn unpack_rgba(color: u32) -> (u32, u32, u32, u32) {
    let b = color & 0xFF;
    let g = (color >> 8) & 0xFF;
    let r = (color >> 16) & 0xFF;
    let a = (color >> 24) & 0xFF;

    (r, g, b, a)
}

fn c2(c0: u32, c1: u32, color0: u32, color1: u32) -> u32 {
    if color0 > color1 {
        return (2 * c0 + c1) / 3;
    }

    (c0 + c1) / 2
}

fn c3(c0: u32, c1: u32) -> u32 {
    (c0 + 2 * c1) / 3
}

pub fn decode_dxt1(input: Vec<u8>, width: usize, height: usize) -> Vec<u8> {
    let mut offset: usize = 0;
    let block_count_x = (width + 3) / 4;
    let block_count_y = (height + 3) / 4;
    let length_last = (width + 3) % 4 + 1;
    let mut buffer = vec![0u8; 64];
    let mut colors = vec![0u32; 4];
    let mut output = vec![0u8; width * height * 4];

    for y in 0..block_count_y {
        for x in 0..block_count_x {
            let c0 = (input[offset + 0] as u32) | (input[offset + 1] as u32) << 8;
            let c1 = (input[offset + 2] as u32) | (input[offset + 3] as u32) << 8;

            let (r0, g0, b0) = unpack_565(c0 as u32);
            let (r1, g1, b1) = unpack_565(c1 as u32);

            colors[0] = pack_rgba(r0, g0, b0, 255);
            colors[1] = pack_rgba(r1, g1, b1, 255);
            colors[2] = pack_rgba(
                c2(r0, r1, c0, c1),
                c2(g0, g1, c0, c1),
                c2(b0, b1, c0, c1),
                255,
            );
            colors[3] = pack_rgba(c3(r0, r1), c3(g0, g1), c3(b0, b1), 255);

            let mut bitcode = (input[offset + 4] as u32)
                | (input[offset + 5] as u32) << 8
                | (input[offset + 6] as u32) << 16
                | (input[offset + 7] as u32) << 24;

            for i in 0..16 {
                let idx = i * 4;
                let (r, g, b, a) = unpack_rgba(colors[(bitcode & 0x3) as usize]);
                buffer[idx + 0] = r as u8;
                buffer[idx + 1] = g as u8;
                buffer[idx + 2] = b as u8;
                buffer[idx + 3] = a as u8;

                bitcode >>= 2;
            }

            let length = if x < block_count_x - 1 {
                4 * 4
            } else {
                length_last * 4
            };

            let mut i = 0;
            let mut j = y * 4;
            while i < 4 && j < height {
                let bidx = (i * 4 * 4) as usize;
                let oidx = ((j * width + x * 4) * 4) as usize;

                for k in 0..length as usize {
                    output[oidx + k] = buffer[bidx + k];
                }

                i += 1;
                j += 1;
            }

            offset += 8;
        }
    }

    output
}
pub fn decode_dxt3(input: Vec<u8>, width: usize, height: usize) -> Vec<u8> {
    let mut offset: usize = 0;
    let block_count_x = (width + 3) / 4;
    let block_count_y = (height + 3) / 4;
    let length_last = (width + 3) % 4 + 1;
    let mut buffer = vec![0u8; 64];
    let mut colors = vec![0u32; 4];
    let mut alphas = vec![0u32; 16];
    let mut output = vec![0u8; width * height * 4];

    for y in 0..block_count_y {
        for x in 00..block_count_x {
            for i in 0..4 {
                let alpha =
                    (input[offset + i * 2] as u32) | (input[offset + i * 2 + 1] as u32) << 8;
                alphas[i * 4 + 0] = (((alpha >> 0) & 0xF) * 0x11) << 24;
                alphas[i * 4 + 1] = (((alpha >> 4) & 0xF) * 0x11) << 24;
                alphas[i * 4 + 2] = (((alpha >> 8) & 0xF) * 0x11) << 24;
                alphas[i * 4 + 3] = (((alpha >> 12) & 0xF) * 0x11) << 24;
            }

            let c0 = (input[offset + 8] as u32) | (input[offset + 9] as u32) << 8;
            let c1 = (input[offset + 10] as u32) | (input[offset + 11] as u32) << 8;

            let (r0, g0, b0) = unpack_565(c0);
            let (r1, g1, b1) = unpack_565(c1);

            colors[0] = pack_rgba(r0, g0, b0, 0);
            colors[1] = pack_rgba(r1, g1, b1, 0);
            colors[2] = pack_rgba(
                c2(r0, r1, c0, c1),
                c2(g0, g1, c0, c1),
                c2(b0, b1, c0, c1),
                0,
            );
            colors[3] = pack_rgba(c3(r0, r1), c3(g0, g1), c3(b0, b1), 0);

            let mut bitcode = (input[offset + 12] as u32)
                | (input[offset + 13] as u32) << 8
                | (input[offset + 14] as u32) << 16
                | (input[offset + 15] as u32) << 24;
            for i in 0..16 {
                let idx = i * 4;
                let (r, g, b, a) = unpack_rgba(colors[(bitcode & 0x3) as usize] | alphas[i]);
                buffer[idx + 0] = r as u8;
                buffer[idx + 1] = g as u8;
                buffer[idx + 2] = b as u8;
                buffer[idx + 3] = a as u8;

                bitcode >>= 2;
            }

            let length = if x < block_count_x - 1 {
                4 * 4
            } else {
                length_last * 4
            };

            let mut i = 0;
            let mut j = y * 4;
            while i < 4 && j < height {
                let bidx = (i * 4 * 4) as usize;
                let oidx = ((j * width + x * 4) * 4) as usize;

                for k in 0..length as usize {
                    output[oidx + k] = buffer[bidx + k];
                }

                i += 1;
                j += 1;
            }

            offset += 16;
        }
    }

    output
}
pub fn decode_dxt5(input: Vec<u8>, width: usize, height: usize) -> Vec<u8> {
    let mut offset: usize = 0;
    let block_count_x = (width + 3) / 4;
    let block_count_y = (height + 3) / 4;
    let length_last = (width + 3) % 4 + 1;
    let mut buffer = vec![0u8; 64];
    let mut colors = vec![0u32; 4];
    let mut alphas = vec![0u32; 8];
    let mut output = vec![0u8; width * height * 4];

    for y in 0..block_count_y {
        for x in 0..block_count_x {
            alphas[0] = input[offset + 0] as u32;
            alphas[1] = input[offset + 1] as u32;

            if alphas[0] > alphas[1] {
                alphas[2] = (alphas[0] * 6 + alphas[1]) / 7;
                alphas[3] = (alphas[0] * 5 + alphas[1] * 2) / 7;
                alphas[4] = (alphas[0] * 4 + alphas[1] * 3) / 7;
                alphas[5] = (alphas[0] * 3 + alphas[1] * 4) / 7;
                alphas[6] = (alphas[0] * 2 + alphas[1] * 5) / 7;
                alphas[7] = (alphas[0] + alphas[1] * 6) / 7;
            } else {
                alphas[2] = (alphas[0] * 4 + alphas[1]) / 5;
                alphas[3] = (alphas[0] * 3 + alphas[1] * 2) / 5;
                alphas[4] = (alphas[0] * 2 + alphas[1] * 3) / 5;
                alphas[5] = (alphas[0] + alphas[1] * 4) / 5;
                alphas[7] = 255;
            }

            for i in 0..8 {
                alphas[i] <<= 24;
            }

            let c0 = (input[offset + 8] as u32) | (input[offset + 9] as u32) << 8;
            let c1 = (input[offset + 10] as u32) | (input[offset + 11] as u32) << 8;

            let (r0, g0, b0) = unpack_565(c0);
            let (r1, g1, b1) = unpack_565(c1);

            colors[0] = pack_rgba(r0, g0, b0, 0);
            colors[1] = pack_rgba(r1, g1, b1, 0);
            colors[2] = pack_rgba(
                c2(r0, r1, c0, c1),
                c2(g0, g1, c0, c1),
                c2(b0, b1, c0, c1),
                0,
            );
            colors[3] = pack_rgba(c3(r0, r1), c3(g0, g1), c3(b0, b1), 0);

            let mut bitcode_a = (input[offset] as u64)
                | (input[offset + 1] as u64) << 8
                | (input[offset + 2] as u64) << 16
                | (input[offset + 3] as u64) << 24
                | (input[offset + 4] as u64) << 32
                | (input[offset + 5] as u64) << 40
                | (input[offset + 6] as u64) << 48
                | (input[offset + 7] as u64) << 56;
            let mut bitcode_c = (input[offset + 12] as u32)
                | (input[offset + 13] as u32) << 8
                | (input[offset + 14] as u32) << 16
                | (input[offset + 15] as u32) << 24;

            for i in 0..16 {
                let idx = i * 4;
                let (r, g, b, a) = unpack_rgba(
                    alphas[(bitcode_a & 0x08) as usize] | colors[(bitcode_c & 0x03) as usize],
                );
                buffer[idx + 0] = r as u8;
                buffer[idx + 1] = g as u8;
                buffer[idx + 2] = b as u8;
                buffer[idx + 3] = a as u8;

                bitcode_a >>= 3;
                bitcode_c >>= 2;
            }

            let length = if x < block_count_x - 1 {
                4 * 4
            } else {
                length_last * 4
            };

            let mut i = 0;
            let mut j = y * 4;
            while i < 4 && j < height {
                let bidx = (i * 4 * 4) as usize;
                let oidx = ((j * width + x * 4) * 4) as usize;

                for k in 0..length as usize {
                    output[oidx + k] = buffer[bidx + k];
                }

                i += 1;
                j += 1;
            }

            offset += 16;
        }
    }

    output
}
