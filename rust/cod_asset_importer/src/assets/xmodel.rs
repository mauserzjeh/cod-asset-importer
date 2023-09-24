use crate::utils::{binary, error::Error, path::file_name_without_ext, Result};
use pyo3::prelude::*;
use std::{fs::File, path::PathBuf};
use valid_enum::ValidEnum;

pub const ASSETPATH: &str = "xmodel";

pub struct XModel {
    pub name: String,
    pub version: u16,
    pub lods: Vec<XModelLod>,
}

#[derive(Debug, Clone)]
pub struct XModelLod {
    pub name: String,
    pub distance: f32,
    pub materials: Vec<String>,
}

#[pyclass(module= "cod_asset_importer", name="XMODEL_TYPES")]
#[derive(ValidEnum)]
#[valid_enum(u8)]
pub enum XModelType {
    Rigid = 48,
    Animated = 49,
    Viewmodel = 50,
    Playerbody = 51,
    Viewhands = 52,
}

#[pyclass(module= "cod_asset_importer", name="XMODEL_VERSIONS")]
#[derive(ValidEnum)]
#[valid_enum(u16)]
pub enum XModelVersion {
    // CoD1 & CoDUO
    V14 = 0x0E,
    // CoD2
    V20 = 0x14,
    // CoD4
    V25 = 0x19,
}

impl XModel {
    pub fn load(file_path: PathBuf) -> Result<XModel> {
        let mut file = File::open(&file_path)?;
        let name = file_name_without_ext(file_path);
        let version = binary::read::<u16>(&mut file)?;
        let mut xmodel = XModel {
            name,
            version,
            lods: Vec::new(),
        };

        match XModelVersion::valid(version) {
            Some(XModelVersion::V14) => {
                xmodel.load_v14(&mut file)?;
                return Ok(xmodel);
            }
            Some(XModelVersion::V20) => {
                xmodel.load_v20(&mut file)?;
                return Ok(xmodel);
            }
            Some(XModelVersion::V25) => {
                xmodel.load_v25(&mut file)?;
                return Ok(xmodel);
            }
            None => return Err(Error::new(format!("invalid xmodel version {}", version))),
        }
    }

    fn load_v14(&mut self, file: &mut File) -> Result<()> {
        binary::skip(file, 24)?;

        for _ in 0..3 {
            let distance = binary::read::<f32>(file)?;
            let name = binary::read_string(file)?;

            if name.len() > 0 {
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

            if name.len() > 0 {
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

    fn load_v25(&mut self, file: &mut File) -> Result<()> {
        binary::skip(file, 26)?;

        for _ in 0..4 {
            let distance = binary::read::<f32>(file)?;
            let name = binary::read_string(file)?;

            if name.len() > 0 {
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
