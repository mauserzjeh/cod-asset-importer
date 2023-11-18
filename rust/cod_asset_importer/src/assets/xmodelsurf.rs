use super::xmodel::XModelVersion;
use super::xmodelpart::XModelPart;
use crate::utils::{
    binary,
    error::Error,
    math::{color_from_vec, uv_from_vec, vec3_add, vec3_from_vec, vec3_rotate, Color, Vec3, UV},
    path::file_name_without_ext,
    Result,
};
use std::{fs::File, path::PathBuf};

pub const ASSETPATH: &str = "xmodelsurfs";
const RIGGED: i32 = 65535;

pub struct XModelSurf {
    pub name: String,
    pub version: u16,
    pub surfaces: Vec<XModelSurfSurface>,
}

pub struct XModelSurfVertex {
    pub normal: Vec3,
    pub color: Color,
    pub uv: UV,
    pub bone: u16,
    pub position: Vec3,
    pub weights: Vec<XModelSurfWeight>,
}

pub struct XModelSurfWeight {
    pub bone: u16,
    pub influence: f32,
}

pub struct XModelSurfSurface {
    pub vertices: Vec<XModelSurfVertex>,
    pub triangles: Vec<u16>,
}

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
                xmodel_surf.load_v14(&mut file, xmodel_part)?;
                Ok(xmodel_surf)
            }
            Some(XModelVersion::V20) => {
                xmodel_surf.load_v20(&mut file, xmodel_part)?;
                Ok(xmodel_surf)
            }
            Some(XModelVersion::V25) => {
                xmodel_surf.load_v25(&mut file)?;
                Ok(xmodel_surf)
            }
            None => Err(Error::new(format!(
                "invalid xmodelsurf version {}",
                version
            ))),
        }
    }

    fn load_v14(&mut self, file: &mut File, xmodel_part: Option<XModelPart>) -> Result<()> {
        let surface_count = binary::read::<u16>(file)?;

        for _ in 0..surface_count {
            binary::skip(file, 1)?;

            let vertex_count = binary::read::<u16>(file)?;
            let triangle_count = binary::read::<u16>(file)?;

            binary::skip(file, 2)?;

            let og_default_bone_idx = binary::read::<u16>(file)?;
            let default_bone_idx = if og_default_bone_idx as i32 == RIGGED {
                binary::skip(file, 4)?;
                0
            } else {
                og_default_bone_idx
            };

            let mut triangles: Vec<u16> = Vec::new();
            loop {
                let idx_count = binary::read::<u8>(file)?;

                let idx1 = binary::read::<u16>(file)?;
                let mut idx2 = binary::read::<u16>(file)?;
                let mut idx3 = binary::read::<u16>(file)?;

                if idx1 != idx2 && idx1 != idx3 && idx2 != idx3 {
                    triangles.extend_from_slice(&[idx3, idx2, idx1]);
                }

                let mut i = 3;
                while i < idx_count {
                    let idx4 = idx3;
                    let idx5 = binary::read::<u16>(file)?;

                    if idx4 != idx2 && idx4 != idx5 && idx2 != idx5 {
                        triangles.extend_from_slice(&[idx5, idx2, idx4]);
                    }

                    let v = i + 1;
                    if v >= idx_count {
                        break;
                    }

                    idx2 = idx5;
                    idx3 = binary::read::<u16>(file)?;

                    if idx4 != idx2 && idx4 != idx3 && idx2 != idx3 {
                        triangles.extend_from_slice(&[idx3, idx2, idx4]);
                    }

                    i = v + 1;
                }

                if triangles.len() / 3 >= triangle_count as usize {
                    break;
                }
            }

            let mut bone_weight_counts = vec![0u16; vertex_count as usize];
            let mut vertices: Vec<XModelSurfVertex> = Vec::new();
            for i in 0..vertex_count {
                let normal = binary::read_vec::<f32>(file, 3)?;
                let mut normal = vec3_from_vec(normal).unwrap();

                let uv = binary::read_vec::<f32>(file, 2)?;
                let mut weight_count = 0;
                let mut vertex_bone_idx = default_bone_idx;

                if og_default_bone_idx as i32 == RIGGED {
                    weight_count = binary::read::<u16>(file)?;
                    vertex_bone_idx = binary::read::<u16>(file)?;
                }

                let position = binary::read_vec::<f32>(file, 3)?;
                let mut position = vec3_from_vec(position).unwrap();

                if weight_count != 0 {
                    binary::skip(file, 4)?;
                }

                bone_weight_counts[i as usize] = weight_count;

                if let Some(xmodel_part) = xmodel_part.to_owned() {
                    let xmodel_part_bone = xmodel_part.bones[vertex_bone_idx as usize].to_owned();

                    position = vec3_rotate(position, xmodel_part_bone.world_transform.rotation);
                    position = vec3_add(position, xmodel_part_bone.world_transform.position);
                    normal = vec3_rotate(normal, xmodel_part_bone.world_transform.rotation);
                }

                vertices.push(XModelSurfVertex {
                    normal,
                    color: [1.0, 1.0, 1.0, 1.0],
                    uv: uv_from_vec(uv, true).unwrap(),
                    bone: vertex_bone_idx,
                    position,
                    weights: vec![XModelSurfWeight {
                        bone: vertex_bone_idx,
                        influence: 1.0,
                    }],
                })
            }

            for i in 0..vertex_count {
                for _ in 0..bone_weight_counts[i as usize] {
                    let weight_bone_idx = binary::read::<u16>(file)?;

                    binary::skip(file, 12)?;

                    let mut weight_influence = binary::read::<f32>(file)?;
                    weight_influence /= RIGGED as f32;

                    vertices[i as usize].weights[0].influence -= weight_influence;
                    vertices[i as usize].weights.push(XModelSurfWeight {
                        bone: weight_bone_idx,
                        influence: weight_influence,
                    });
                }
            }

            self.surfaces.push(XModelSurfSurface {
                vertices,
                triangles,
            });
        }

        Ok(())
    }

    fn load_v20(&mut self, file: &mut File, xmodel_part: Option<XModelPart>) -> Result<()> {
        let surface_count = binary::read::<u16>(file)?;

        for _ in 0..surface_count {
            binary::skip(file, 1)?;

            let vertex_count = binary::read::<u16>(file)?;
            let triangle_count = binary::read::<u16>(file)?;
            let og_default_bone_idx = binary::read::<u16>(file)?;
            let default_bone_idx: u16 = if og_default_bone_idx as i32 == RIGGED {
                binary::skip(file, 2)?;
                0
            } else {
                og_default_bone_idx
            };

            let mut vertices: Vec<XModelSurfVertex> = Vec::new();
            for _ in 0..vertex_count {
                let normal = binary::read_vec::<f32>(file, 3)?;
                let mut normal = vec3_from_vec(normal).unwrap();

                let color = binary::read_vec::<u8>(file, 4)?;
                let uv = binary::read_vec::<f32>(file, 2)?;

                binary::skip(file, 24)?;

                let mut weight_count = 0;
                let mut vertex_bone_idx = default_bone_idx;

                if og_default_bone_idx as i32 == RIGGED {
                    weight_count = binary::read::<u8>(file)?;
                    vertex_bone_idx = binary::read::<u16>(file)?;
                }

                let position = binary::read_vec::<f32>(file, 3)?;
                let mut position = vec3_from_vec(position).unwrap();

                let mut vertex_weights: Vec<XModelSurfWeight> = vec![XModelSurfWeight {
                    bone: vertex_bone_idx,
                    influence: 1.0,
                }];

                if weight_count > 0 {
                    binary::skip(file, 1)?;

                    for _ in 0..weight_count {
                        let weight_bone_idx = binary::read::<u16>(file)?;
                        binary::skip(file, 12)?;
                        let weight_influence = binary::read::<u16>(file)?;
                        let weight_influence = weight_influence as f32 / RIGGED as f32;

                        vertex_weights[0].influence -= weight_influence;
                        vertex_weights.push(XModelSurfWeight {
                            bone: weight_bone_idx,
                            influence: weight_influence,
                        });
                    }
                }

                if let Some(xmodel_part) = xmodel_part.to_owned() {
                    let xmodel_part_bone = xmodel_part.bones[vertex_bone_idx as usize].to_owned();

                    position = vec3_rotate(position, xmodel_part_bone.world_transform.rotation);
                    position = vec3_add(position, xmodel_part_bone.world_transform.position);
                    normal = vec3_rotate(normal, xmodel_part_bone.world_transform.rotation);
                }

                vertices.push(XModelSurfVertex {
                    normal,
                    color: color_from_vec(color).unwrap(),
                    uv: uv_from_vec(uv, false).unwrap(),
                    bone: vertex_bone_idx,
                    position,
                    weights: vertex_weights,
                });
            }

            let mut triangles: Vec<u16> = Vec::new();
            for _ in 0..triangle_count {
                let t = binary::read_vec::<u16>(file, 3)?;
                triangles.extend_from_slice(&[t[0], t[2], t[1]]);
            }

            self.surfaces.push(XModelSurfSurface {
                vertices,
                triangles,
            });
        }

        Ok(())
    }

    fn load_v25(&mut self, file: &mut File) -> Result<()> {
        let surface_count = binary::read::<u16>(file)?;

        for _ in 0..surface_count {
            binary::skip(file, 3)?;
            let vertex_count = binary::read::<u16>(file)?;
            let triangle_count = binary::read::<u16>(file)?;
            let vertex_count2 = binary::read::<u16>(file)?;

            if vertex_count != vertex_count2 {
                binary::skip(file, 2)?;
                if vertex_count2 != 0 {
                    loop {
                        let p = binary::read::<u16>(file)?;
                        if p == 0 {
                            break;
                        }
                    }
                    binary::skip(file, 2)?;
                }
            } else {
                binary::skip(file, 4)?;
            }

            let mut vertices: Vec<XModelSurfVertex> = Vec::new();
            for _ in 0..vertex_count {
                let normal = binary::read_vec::<f32>(file, 3)?;
                let color = binary::read_vec::<u8>(file, 4)?;
                let uv = binary::read_vec::<f32>(file, 2)?;

                binary::skip(file, 24)?;

                let mut weight_count = 0;
                let mut vertex_bone_idx = 0;
                if vertex_count != vertex_count2 {
                    weight_count = binary::read::<u8>(file)?;
                    vertex_bone_idx = binary::read::<u16>(file)?;
                }

                let position = binary::read_vec::<f32>(file, 3)?;

                let mut vertex_weights: Vec<XModelSurfWeight> = vec![XModelSurfWeight {
                    bone: vertex_bone_idx,
                    influence: 1.0,
                }];

                if weight_count > 0 {
                    for _ in 0..weight_count {
                        let weight_bone_idx = binary::read::<u16>(file)?;
                        let weight_influence = binary::read::<u16>(file)?;
                        let weight_influence = weight_influence as f32 / RIGGED as f32;
                        vertex_weights[0].influence -= weight_influence;
                        vertex_weights.push(XModelSurfWeight {
                            bone: weight_bone_idx,
                            influence: weight_influence,
                        });
                    }
                }

                vertices.push(XModelSurfVertex {
                    normal: vec3_from_vec(normal).unwrap(),
                    color: color_from_vec(color).unwrap(),
                    uv: uv_from_vec(uv, false).unwrap(),
                    bone: vertex_bone_idx,
                    position: vec3_from_vec(position).unwrap(),
                    weights: vertex_weights,
                })
            }

            let mut triangles: Vec<u16> = Vec::new();
            for _ in 0..triangle_count {
                let t = binary::read_vec::<u16>(file, 3)?;
                triangles.extend_from_slice(&[t[0], t[2], t[1]]);
            }

            self.surfaces.push(XModelSurfSurface {
                vertices,
                triangles,
            });
        }

        Ok(())
    }
}
