use super::xmodel::XModelVersion;
use super::xmodelpart::XModelPart;
use crate::utils::{
    binary,
    error::Error,
    math::{Color, Triangle, Vec3, UV},
    path::file_name_without_ext,
    Result,
};
use std::{fs::File, path::PathBuf};

pub struct XModelSurf {
    name: String,
    version: u16,
    surfaces: Vec<XModelSurfSurface>,
}

pub struct XModelSurfVertex {
    normal: Vec3,
    color: Color,
    uv: UV,
    bone: u16,
    position: Vec3,
    weights: Vec<XModelSurfWeight>,
}

pub struct XModelSurfWeight {
    bone: u16,
    influence: f32,
}

pub struct XModelSurfSurface {
    vertices: Vec<XModelSurfVertex>,
    triangles: Triangle,
}

const RIGGED: i32 = 65535;

impl XModelSurf {
    pub fn load(file_path: PathBuf, xmodel_part: Option<XModelPart>) -> Result<XModelSurf> {
        let mut file = File::open(&file_path)?;
        let name = file_name_without_ext(file_path);
        let version = binary::read::<u16>(&mut file)?;
        let mut xmodel_surf = XModelSurf {
            name,
            version,
            surfaces: Vec::new(),
        };

        match XModelVersion::valid(version) {
            Some(XModelVersion::V14) => {
                xmodel_surf.load_v14(&mut file)?;
                return Ok(xmodel_surf);
            }
            Some(XModelVersion::V20) => {
                xmodel_surf.load_v20(&mut file)?;
                return Ok(xmodel_surf);
            }
            Some(XModelVersion::V25) => {
                xmodel_surf.load_v25(&mut file)?;
                return Ok(xmodel_surf);
            }
            None => {
                return Err(Error::new(format!(
                    "invalid xmodelsurf version {}",
                    version
                )))
            }
        }
    }

    fn load_v14(&mut self, file: &mut File) -> Result<()> {
        Ok(())
    }

    fn load_v20(&mut self, file: &mut File) -> Result<()> {
        Ok(())
    }

    fn load_v25(&mut self, file: &mut File) -> Result<()> {
        Ok(())
    }
}
