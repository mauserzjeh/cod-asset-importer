use super::Result;
use std::{
    fs::File,
    io::{Read, Seek, SeekFrom},
};

pub fn read_i8(f: &mut File) -> Result<i8> {
    let mut buffer = [0u8; 1];
    f.read_exact(&mut buffer)?;
    Ok(i8::from_le_bytes(buffer))
}

pub fn read_u8(f: &mut File) -> Result<u8> {
    let mut buffer = [0u8; 1];
    f.read_exact(&mut buffer)?;
    Ok(u8::from_le_bytes(buffer))
}

pub fn read_i16(f: &mut File) -> Result<i16> {
    let mut buffer = [0u8; 2];
    f.read_exact(&mut buffer)?;
    Ok(i16::from_le_bytes(buffer))
}

pub fn read_u16(f: &mut File) -> Result<u16> {
    let mut buffer = [0u8; 2];
    f.read_exact(&mut buffer)?;
    Ok(u16::from_le_bytes(buffer))
}

pub fn read_i32(f: &mut File) -> Result<i32> {
    let mut buffer = [0u8; 4];
    f.read_exact(&mut buffer)?;
    Ok(i32::from_le_bytes(buffer))
}

pub fn read_u32(f: &mut File) -> Result<u32> {
    let mut buffer = [0u8; 4];
    f.read_exact(&mut buffer)?;
    Ok(u32::from_le_bytes(buffer))
}

pub fn read_i64(f: &mut File) -> Result<i64> {
    let mut buffer = [0u8; 8];
    f.read_exact(&mut buffer)?;
    Ok(i64::from_le_bytes(buffer))
}

pub fn read_u64(f: &mut File) -> Result<u64> {
    let mut buffer = [0u8; 8];
    f.read_exact(&mut buffer)?;
    Ok(u64::from_le_bytes(buffer))
}

pub fn read_f32(f: &mut File) -> Result<f32> {
    let mut buffer = [0u8; 4];
    f.read_exact(&mut buffer)?;
    Ok(f32::from_le_bytes(buffer))
}

pub fn read_f64(f: &mut File) -> Result<f64> {
    let mut buffer = [0u8; 8];
    f.read_exact(&mut buffer)?;
    Ok(f64::from_le_bytes(buffer))
}

pub fn read_nullstr(f: &mut File) -> Result<String> {
    let mut buffer = [0u8; 1];
    let mut nullstr: String = String::new();
    loop {
        f.read_exact(&mut buffer)?;
        if buffer[0] == 0 {
            return Ok(nullstr);
        }
        nullstr.push(buffer[0] as char)
    }
}

pub fn skip(f: &mut File, n: i64) -> Result<u64> {
    let offset = f.seek(SeekFrom::Current(n))?;
    Ok(offset)
}

pub fn current_offset(f: &mut File) -> Result<u64> {
    let offset = f.seek(SeekFrom::Current(0))?;
    Ok(offset)
}
