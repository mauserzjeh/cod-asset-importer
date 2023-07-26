fn unpack_565(color: u32) -> [u32; 3] {
    let mut r = (color & 0xF800) >> 8;
    let mut g = (color & 0x07E0) >> 3;
    let mut b = (color & 0x001F) << 3;
    r |= r >> 5;
    g |= g >> 6;
    b |= b >> 5;

    [r, g, b]
}

fn pack_rgba(r: u32, g: u32, b: u32, a: u32) -> u32 {
    (r << 16) | (g << 8) | b | (a << 24)
}

fn unpack_rgba(color: u32) -> [u32; 4] {
    let b = color & 0xFF;
    let g = (color >> 8) & 0xFF;
    let r = (color >> 16) & 0xFF;
    let a = (color >> 24) & 0xFF;

    [r, g, b, a]
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

pub fn decode_dxt1(data: Vec<u8>, width: u16, height: u16) -> Vec<u8> {
    let offset: u32 = 0;
    let block_count_x = (width + 3) / 4;
    let block_count_y = (width + 3) / 4;
    let length_last = (width + 3) % 4 + 1;
    let mut buffer = vec![0u8; 64];
    let mut colors = vec![0u32; 4];
    let mut output = vec![0u8; (width*height*4) as usize];

    todo!();

    output
}
pub fn decode_dxt3(data: Vec<u8>, width: u16, height: u16) -> Vec<u8> {
    let offset: u32 = 0;
    let block_count_x = (width + 3) / 4;
    let block_count_y = (width + 3) / 4;
    let length_last = (width + 3) % 4 + 1;
    let mut buffer = vec![0u8; 64];
    let mut colors = vec![0u32; 4];
    let mut alphas = vec![0u32; 16];
    let mut output = vec![0u8; (width*height*4) as usize];

    todo!();

    output
}
pub fn decode_dxt5(data: Vec<u8>, width: u16, height: u16) -> Vec<u8> {
    let offset: u32 = 0;
    let block_count_x = (width + 3) / 4;
    let block_count_y = (width + 3) / 4;
    let length_last = (width + 3) % 4 + 1;
    let mut buffer = vec![0u8; 64];
    let mut colors = vec![0u32; 4];
    let mut alphas = vec![0u32; 16];
    let mut output = vec![0u8; (width*height*4) as usize];

    todo!();

    output
}
