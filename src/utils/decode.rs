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

pub fn decode_dxt1(input: Vec<u8>, width: u16, height: u16) -> Vec<u8> {
    let mut offset: usize = 0;
    let block_count_x = (width + 3) / 4;
    let block_count_y = (width + 3) / 4;
    let length_last = (width + 3) % 4 + 1;
    let mut buffer = vec![0u8; 64];
    let mut colors = vec![0u32; 4];
    let mut output = vec![0u8; (width * height * 4) as usize];

    for y in 0..block_count_y {
        for x in 0..block_count_x {
            let c0 = (input[offset + 0] | input[offset + 1] << 8) as u32;
            let c1 = (input[offset + 2] | input[offset + 3] << 8) as u32;

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

            let mut bitcode = (input[offset + 4]
                | input[offset + 5] << 8
                | input[offset + 6] << 16
                | input[offset + 7] << 24) as u32;

            for i in 0..16 {
                let idx = i * 4;
                let (r, g, b, a) = unpack_rgba(colors[(bitcode & 0x3) as usize]);
                buffer[idx + 0] = r as u8;
                buffer[idx + 1] = g as u8;
                buffer[idx + 2] = b as u8;
                buffer[idx + 3] = a as u8;

                bitcode >>= 2;
            }

            let mut length = length_last * 4;
            if x < block_count_x - 1 {
                length = 4 * 4;
            }

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
pub fn decode_dxt3(input: Vec<u8>, width: u16, height: u16) -> Vec<u8> {
    let offset: u32 = 0;
    let block_count_x = (width + 3) / 4;
    let block_count_y = (width + 3) / 4;
    let length_last = (width + 3) % 4 + 1;
    let mut buffer = vec![0u8; 64];
    let mut colors = vec![0u32; 4];
    let mut alphas = vec![0u32; 16];
    let mut output = vec![0u8; (width * height * 4) as usize];

    todo!();

    output
}
pub fn decode_dxt5(input: Vec<u8>, width: u16, height: u16) -> Vec<u8> {
    let offset: u32 = 0;
    let block_count_x = (width + 3) / 4;
    let block_count_y = (width + 3) / 4;
    let length_last = (width + 3) % 4 + 1;
    let mut buffer = vec![0u8; 64];
    let mut colors = vec![0u32; 4];
    let mut alphas = vec![0u32; 16];
    let mut output = vec![0u8; (width * height * 4) as usize];

    todo!();

    output
}
