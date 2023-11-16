use crate::utils::{binary, Result};
use std::{
    fs::File,
    io::{Seek, SeekFrom},
    path::PathBuf,
};

use super::xmodel::XModelVersion;

pub const ASSETPATH: &str = "materials";

pub struct Material {
    techset: String,
    pub name: String,
    pub textures: Vec<MaterialTexture>,
}

#[derive(Debug)]
pub struct MaterialTexture {
    pub texture_type: String,
    flags: u32,
    pub name: String,
}

impl Material {
    pub fn load(file_path: PathBuf, version: XModelVersion) -> Result<Material> {
        let mut file = File::open(&file_path)?;
        let name_offset = binary::read::<u32>(&mut file)?;

        match version {
            XModelVersion::V20 => {
                binary::skip(&mut file, 48)?;
            }
            _ => {
                binary::skip(&mut file, 44)?;
            }
        }

        let texture_count = binary::read::<u16>(&mut file)?;

        binary::skip(&mut file, 2)?;

        let techset_offset = binary::read::<u32>(&mut file)?;
        let textures_offset = binary::read::<u32>(&mut file)?;

        file.seek(SeekFrom::Start(name_offset as u64))?;
        let name = binary::read_string(&mut file)?;

        file.seek(SeekFrom::Start(techset_offset as u64))?;
        let techset = binary::read_string(&mut file)?;

        let mut textures: Vec<MaterialTexture> = Vec::new();

        file.seek(SeekFrom::Start(textures_offset as u64))?;
        for _ in 0..texture_count {
            let texture_type_offset = binary::read::<u32>(&mut file)?;
            let texture_flags = binary::read::<u32>(&mut file)?;
            let texture_name_offset = binary::read::<u32>(&mut file)?;

            let current_offset = binary::current_offset(&mut file)?;

            file.seek(SeekFrom::Start(texture_type_offset as u64))?;
            let texture_type = binary::read_string(&mut file)?;

            file.seek(SeekFrom::Start(texture_name_offset as u64))?;
            let texture_name = binary::read_string(&mut file)?;

            textures.push(MaterialTexture {
                texture_type,
                flags: texture_flags,
                name: texture_name,
            });

            file.seek(SeekFrom::Start(current_offset))?;
        }

        Ok(Material {
            techset,
            name,
            textures,
        })
    }
}
