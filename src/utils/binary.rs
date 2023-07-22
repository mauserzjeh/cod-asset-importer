use super::Result;
use std::{
    fs::File,
    io::{Read, Seek, SeekFrom},
};

const SIZE_BYTE: usize = 1;
const SIZE_SHORT: usize = 2;
const SIZE_INT: usize = 4;
const SIZE_LONG: usize = 8;
const SIZE_FLOAT: usize = 4;
const SIZE_DOUBLE: usize = 8;

pub trait BinBytes {
    fn from_bytes(bytes: Vec<u8>) -> Self;
    fn buffer(n: usize) -> Vec<u8>;
    fn size() -> usize;
}

pub fn read<T: BinBytes>(f: &mut File) -> Result<T> {
    let mut buffer = T::buffer(1);
    f.read_exact(&mut buffer)?;
    Ok(T::from_bytes(buffer))
}

pub fn read_vec<T: BinBytes>(f: &mut File, n: usize) -> Result<Vec<T>> {
    let mut buffer = T::buffer(n);
    f.read_exact(&mut buffer)?;
    let mut items: Vec<T> = Vec::new();
    for i in 0..n {
        let start = i * T::size();
        let end = start + T::size();
        let item = T::from_bytes(buffer[start..end].to_vec());
        items.push(item)
    }

    Ok(items)
}

impl BinBytes for i8 {
    fn from_bytes(bytes: Vec<u8>) -> Self {
        i8::from_le_bytes([bytes[0]])
    }
    fn buffer(n: usize) -> Vec<u8> {
        vec![0u8; SIZE_BYTE * n]
    }
    fn size() -> usize {
        SIZE_BYTE
    }
}

impl BinBytes for u8 {
    fn from_bytes(bytes: Vec<u8>) -> Self {
        u8::from_le_bytes([bytes[0]])
    }
    fn buffer(n: usize) -> Vec<u8> {
        vec![0u8; SIZE_BYTE * n]
    }
    fn size() -> usize {
        SIZE_BYTE
    }
}

impl BinBytes for i16 {
    fn from_bytes(bytes: Vec<u8>) -> Self {
        i16::from_le_bytes([bytes[0], bytes[1]])
    }

    fn buffer(n: usize) -> Vec<u8> {
        vec![0u8; SIZE_SHORT * n]
    }
    fn size() -> usize {
        SIZE_SHORT
    }
}
impl BinBytes for u16 {
    fn from_bytes(bytes: Vec<u8>) -> Self {
        u16::from_le_bytes([bytes[0], bytes[1]])
    }

    fn buffer(n: usize) -> Vec<u8> {
        vec![0u8; SIZE_SHORT * n]
    }
    fn size() -> usize {
        SIZE_SHORT
    }
}

impl BinBytes for i32 {
    fn from_bytes(bytes: Vec<u8>) -> Self {
        i32::from_le_bytes([bytes[0], bytes[1], bytes[2], bytes[3]])
    }

    fn buffer(n: usize) -> Vec<u8> {
        vec![0u8; SIZE_INT * n]
    }
    fn size() -> usize {
        SIZE_INT
    }
}
impl BinBytes for u32 {
    fn from_bytes(bytes: Vec<u8>) -> Self {
        u32::from_le_bytes([bytes[0], bytes[1], bytes[2], bytes[3]])
    }

    fn buffer(n: usize) -> Vec<u8> {
        vec![0u8; SIZE_INT * n]
    }
    fn size() -> usize {
        SIZE_INT
    }
}

impl BinBytes for i64 {
    fn from_bytes(bytes: Vec<u8>) -> Self {
        i64::from_le_bytes([
            bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5], bytes[6], bytes[7],
        ])
    }

    fn buffer(n: usize) -> Vec<u8> {
        vec![0u8; SIZE_LONG * n]
    }

    fn size() -> usize {
        SIZE_LONG
    }
}
impl BinBytes for u64 {
    fn from_bytes(bytes: Vec<u8>) -> Self {
        u64::from_le_bytes([
            bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5], bytes[6], bytes[7],
        ])
    }

    fn buffer(n: usize) -> Vec<u8> {
        vec![0u8; SIZE_LONG * n]
    }

    fn size() -> usize {
        SIZE_LONG
    }
}

impl BinBytes for f32 {
    fn from_bytes(bytes: Vec<u8>) -> Self {
        f32::from_le_bytes([bytes[0], bytes[1], bytes[2], bytes[3]])
    }

    fn buffer(n: usize) -> Vec<u8> {
        vec![0u8; SIZE_FLOAT * n]
    }

    fn size() -> usize {
        SIZE_FLOAT
    }
}

impl BinBytes for f64 {
    fn from_bytes(bytes: Vec<u8>) -> Self {
        f64::from_le_bytes([
            bytes[0], bytes[1], bytes[2], bytes[3], bytes[4], bytes[5], bytes[6], bytes[7],
        ])
    }

    fn buffer(n: usize) -> Vec<u8> {
        vec![0u8; SIZE_DOUBLE * n]
    }

    fn size() -> usize {
        SIZE_DOUBLE
    }
}

pub fn read_nullstr(f: &mut File) -> Result<String> {
    let mut buffer = [0u8; SIZE_BYTE];
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
