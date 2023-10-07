use crate::utils::{
    binary, decode::decode_dxt1, decode::decode_dxt3, decode::decode_dxt5, error::Error, Result,
};
use std::{
    fs::File,
    io::{Seek, SeekFrom},
    path::PathBuf,
    str,
};
use valid_enum::ValidEnum;

pub const ASSETPATH: &str = "images";

pub struct IWi {
    pub width: u16,
    pub height: u16,
    pub data: Vec<f32>,
}

struct IWiHeader {
    magic: [u8; 3],
    version: u8,
}

#[derive(Clone, Copy)]
struct IWiInfo {
    format: u8,
    usage: u8,
    width: u16,
    height: u16,
    depth: u16,
}

#[derive(Clone, Copy)]
struct IWiMipMap {
    offset: u32,
    size: u32,
}

#[derive(ValidEnum)]
#[valid_enum(u8)]
pub enum IWiVersion {
    V5 = 0x05,
    V6 = 0x06,
}

#[derive(ValidEnum)]
#[valid_enum(u8)]
pub enum IWiFormat {
    ARGB32 = 0x01,
    RGB24 = 0x02,
    GA16 = 0x03,
    A8 = 0x04,
    DXT1 = 0x0B,
    DXT3 = 0x0C,
    DXT5 = 0x0D,
}

impl IWi {
    pub fn load(file_path: PathBuf) -> Result<IWi> {
        let mut file = File::open(&file_path)?;
        Self::read_header(&mut file)?;
        let info = Self::read_info(&mut file)?;

        let offsets = binary::read_vec::<u32>(&mut file, 4)?;
        let current_offset = binary::current_offset(&mut file)?;
        let file_size = file.seek(SeekFrom::End(0))?;
        let mipmap = Self::calculate_highest_mipmap(offsets, current_offset, file_size);
        file.seek(SeekFrom::Start(mipmap.offset as u64))?;
        let raw_texture_data = binary::read_vec::<u8>(&mut file, mipmap.size as usize)?;
        if raw_texture_data.len() == 0 {
            return Err(Error::new(String::from("texture data length is 0")));
        }

        let data = Self::decode_data(raw_texture_data, info)?;

        Ok(IWi {
            width: info.width,
            height: info.height,
            data,
        })
    }

    fn read_header(file: &mut File) -> Result<IWiHeader> {
        let magic = binary::read_vec::<u8>(file, 3)?;
        if magic != [b'I', b'W', b'i'] {
            return Err(Error::new(format!(
                "invalid magic: {}",
                str::from_utf8(&magic).unwrap()
            )));
        }

        let version = binary::read::<u8>(file)?;
        match IWiVersion::valid(version) {
            Some(_) => (),
            None => return Err(Error::new(format!("invalid IWi version {}", version))),
        }

        Ok(IWiHeader {
            magic: magic.try_into().unwrap(),
            version,
        })
    }

    fn read_info(file: &mut File) -> Result<IWiInfo> {
        let format = binary::read::<u8>(file)?;
        let usage = binary::read::<u8>(file)?;
        let width = binary::read::<u16>(file)?;
        let height = binary::read::<u16>(file)?;
        let depth = binary::read::<u16>(file)?;

        Ok(IWiInfo {
            format,
            usage,
            width,
            height,
            depth,
        })
    }

    fn calculate_highest_mipmap(offsets: Vec<u32>, first: u64, size: u64) -> IWiMipMap {
        let mut mipmaps: Vec<IWiMipMap> = Vec::new();

        let offsets_len = offsets.len();
        for i in 0..offsets_len {
            if i == 0 {
                mipmaps.push(IWiMipMap {
                    offset: offsets[i],
                    size: (size as u32) - offsets[i],
                });
            } else if i == (offsets_len - 1) {
                mipmaps.push(IWiMipMap {
                    offset: first as u32,
                    size: offsets[i] - (first as u32),
                });
            } else {
                mipmaps.push(IWiMipMap {
                    offset: offsets[i],
                    size: offsets[i - 1] - offsets[i],
                })
            }
        }

        let mut max_idx = 0;
        for i in 0..mipmaps.len() {
            if mipmaps[i].size > mipmaps[max_idx].size {
                max_idx = i;
            }
        }

        return mipmaps[max_idx];
    }

    fn decode_data(data: Vec<u8>, info: IWiInfo) -> Result<Vec<f32>> {
        match IWiFormat::valid(info.format) {
            Some(IWiFormat::DXT1) => {
                Ok(decode_dxt1(data, info.width as usize, info.height as usize))
            }
            Some(IWiFormat::DXT3) => {
                Ok(decode_dxt3(data, info.width as usize, info.height as usize))
            }
            Some(IWiFormat::DXT5) => {
                Ok(decode_dxt5(data, info.width as usize, info.height as usize))
            }
            _ => Err(Error::new(format!(
                "unsupported decode format {}",
                info.format
            ))),
        }
    }
}
