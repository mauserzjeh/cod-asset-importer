use crate::utils::{binary, error::Error, path::file_name_without_ext, Result};
use pyo3::prelude::*;
use std::{fs::File, path::PathBuf};
use valid_enum::ValidEnum;

use super::GameVersion;

pub const ASSETPATH: &str = "xmodel";

pub struct XModel {
    pub name: String,
    pub version: XModelVersion,
    pub lods: Vec<XModelLod>,
}

#[derive(Debug, Clone)]
pub struct XModelLod {
    pub name: String,
    pub distance: f32,
    pub materials: Vec<String>,
}

#[derive(ValidEnum)]
#[valid_enum(u8)]
pub enum XModelType {
    Rigid = 48,
    Animated = 49,
    Viewmodel = 50,
    Playerbody = 51,
    Viewhands = 52,
}

#[pyclass(module = "cod_asset_importer", name = "XMODEL_VERSIONS")]
#[derive(ValidEnum, Clone, Copy, PartialEq)]
#[valid_enum(u16)]
pub enum XModelVersion {
    V14 = 0x0E, // CoD1 & CoDUO
    V20 = 0x14, // CoD2
    V25 = 0x19, // CoD4 & CoD5
    V62 = 0x3E, // CoDBO1
}

type XModelLoadFunction = fn(&mut XModel, &mut File) -> Result<()>;

impl XModel {
    pub fn load(file_path: PathBuf, selected_version: GameVersion) -> Result<XModel> {
        let mut file = File::open(&file_path)?;
        let name = file_name_without_ext(file_path);
        let version = binary::read::<u16>(&mut file)?;

        let xmodel_version = match XModelVersion::valid(version) {
            Some(version) => version,
            None => return Err(Error::new(format!("invalid xmodel version {}", version))),
        };

        let mut xmodel = XModel {
            name,
            version: xmodel_version,
            lods: Vec::new(),
        };

        let (expected_version, load_function): (XModelVersion, XModelLoadFunction) =
            match selected_version {
                GameVersion::CoD1 => (XModelVersion::V14, XModel::load_v14),
                GameVersion::CoD2 => (XModelVersion::V20, XModel::load_v20),
                GameVersion::CoD4 => (XModelVersion::V25, |xmodel, file| {
                    XModel::load_v25(xmodel, file, 26)
                }),
                GameVersion::CoD5 => (XModelVersion::V25, |xmodel, file| {
                    XModel::load_v25(xmodel, file, 27)
                }),
                GameVersion::CoD7 => (XModelVersion::V62, XModel::load_v62),
            };

        if xmodel_version != expected_version {
            return Err(Error::new(format!(
                "invalid xmodel version selected {:?} for version {}",
                selected_version, version
            )));
        }

        (load_function)(&mut xmodel, &mut file)?;
        Ok(xmodel)
    }

    fn load_v14(&mut self, file: &mut File) -> Result<()> {
        binary::skip(file, 24)?;

        for _ in 0..3 {
            let distance = binary::read::<f32>(file)?;
            let name = binary::read_string(file)?;

            if !name.is_empty() {
                self.lods.push(XModelLod {
                    name,
                    distance,
                    materials: Vec::new(),
                })
            }
        }

        binary::skip(file, 4)?;

        let padding_count = binary::read::<u32>(file)?;
        for _ in 0..padding_count {
            let sub_padding_count = binary::read::<u32>(file)?;
            binary::skip(file, ((sub_padding_count * 48) + 36) as i64)?;
        }

        for k in 0..self.lods.len() {
            let texture_count = binary::read::<u16>(file)?;
            for _ in 0..texture_count {
                let texture = binary::read_string(file)?;
                self.lods[k].materials.push(texture);
            }
        }

        Ok(())
    }

    fn load_v20(&mut self, file: &mut File) -> Result<()> {
        binary::skip(file, 25)?;

        for _ in 0..4 {
            let distance = binary::read::<f32>(file)?;
            let name = binary::read_string(file)?;

            if !name.is_empty() {
                self.lods.push(XModelLod {
                    name,
                    distance,
                    materials: Vec::new(),
                })
            }
        }

        binary::skip(file, 4)?;

        let padding_count = binary::read::<u32>(file)?;
        for _ in 0..padding_count {
            let sub_padding_count = binary::read::<u32>(file)?;
            binary::skip(file, ((sub_padding_count * 48) + 36) as i64)?;
        }

        for k in 0..self.lods.len() {
            let material_count = binary::read::<u16>(file)?;
            for _ in 0..material_count {
                let material = binary::read_string(file)?;
                self.lods[k].materials.push(material);
            }
        }

        Ok(())
    }

    fn load_v25(&mut self, file: &mut File, skip: i64) -> Result<()> {
        binary::skip(file, skip)?;

        for _ in 0..4 {
            let distance = binary::read::<f32>(file)?;
            let name = binary::read_string(file)?;

            if !name.is_empty() {
                self.lods.push(XModelLod {
                    name,
                    distance,
                    materials: Vec::new(),
                })
            }
        }

        binary::skip(file, 4)?;

        let padding_count = binary::read::<u32>(file)?;
        for _ in 0..padding_count {
            let sub_padding_count = binary::read::<u32>(file)?;
            binary::skip(file, ((sub_padding_count * 48) + 36) as i64)?;
        }

        for k in 0..self.lods.len() {
            let material_count = binary::read::<u16>(file)?;
            for _ in 0..material_count {
                let material = binary::read_string(file)?;
                self.lods[k].materials.push(material);
            }
        }

        Ok(())
    }

    fn load_v62(&mut self, file: &mut File) -> Result<()> {
        binary::skip(file, 28)?;
        binary::read_string(file)?;
        binary::read_string(file)?;
        binary::skip(file, 5)?;

        for _ in 0..4 {
            let distance = binary::read::<f32>(file)?;
            let name = binary::read_string(file)?;

            if !name.is_empty() {
                self.lods.push(XModelLod {
                    name,
                    distance,
                    materials: Vec::new(),
                })
            }
        }

        binary::skip(file, 4)?;

        let padding_count = binary::read::<u32>(file)?;
        for _ in 0..padding_count {
            let sub_padding_count = binary::read::<u32>(file)?;
            binary::skip(file, ((sub_padding_count * 48) + 36) as i64)?;
        }

        for k in 0..self.lods.len() {
            let material_count = binary::read::<u16>(file)?;
            for _ in 0..material_count {
                let material = binary::read_string(file)?;
                self.lods[k].materials.push(material);
            }
        }

        Ok(())
    }
}
