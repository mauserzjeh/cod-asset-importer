use std::{
    collections::HashMap,
    fs::File,
    io::{Read, Seek, SeekFrom},
    mem::size_of,
};

use super::{Color, Triangle, Vec3, UV};
use crate::utils::{binary, error::Error, Result};

#[repr(C)]
#[derive(Debug)]
pub struct Ibsp {
    pub name: String,
    pub materials: Vec<IbspMaterial>,
    pub entities: Vec<IbspEntity>,
    // surfaces: Vec<IbspSurface>,
}

#[repr(C)]
#[derive(Debug)]
pub struct IbspHeader {
    magic: [u8; 4],
    version: i32,
}

#[repr(C)]
#[derive(Clone, Copy)]
struct IbspLump {
    length: u32,
    offset: u32,
}

#[repr(C)]
#[derive(Debug)]
pub struct IbspMaterial {
    name: [u8; 64],
    flag: u64,
}

#[repr(C)]
struct IbspTriangleSoup {
    material_idx: u16,
    draw_order: u16,
    vertices_offset: u32,
    vertices_length: u16,
    triangles_length: u16,
    triangles_offset: u32,
}

#[repr(C)]
struct IbspVertex {
    position: Vec3,
    normal: Vec3,
    color: Color,
    uv: UV,
}

#[repr(C)]
#[derive(Debug)]
pub struct IbspEntity {
    pub name: String,
    pub angles: Vec3,
    pub origin: Vec3,
    pub scale: Vec3,
}

#[repr(C)]
struct IbspSurface {
    material: String,
    vertices: HashMap<u16, IbspVertex>,
    triangles: Vec<Triangle>,
}

#[repr(i32)]
enum IbspVersion {
    V59 = 0x3B,
    V4 = 0x4,
}

enum IbspLumpIndexV59 {
    Materials = 0,
    TriangleSoups = 6,
    Vertices = 7,
    Triangles = 8,
    Entities = 29,
}

enum IbspLumpIndexV4 {
    Materials = 0,
    TriangleSoups = 7,
    Vertices = 8,
    Triangles = 9,
    Entities = 37,
}

impl Ibsp {
    pub fn load(file_path: String) -> Result<Ibsp> {
        let mut file = match File::open(&file_path) {
            Ok(f) => f,
            Err(error) => return Err(Error::new(error.to_string())),
        };

        let header = Self::read_header(&mut file)?;
        let lumps = Self::read_lumps(&mut file)?;
        let materials = Self::read_materials(&mut file, header.version, &lumps)?;
        let triangle_soups = Self::read_trianglesoups(&mut file, header.version, &lumps)?;
        let vertices = Self::read_vertices(&mut file, header.version, &lumps)?;
        let triangles = Self::read_triangles(&mut file, header.version, &lumps)?;
        let entities = Self::read_entities(&mut file, header.version, &lumps)?;

        Ok(Ibsp {
            name: file_path,
            materials,
            entities,
        })
    }

    fn read_header(file: &mut File) -> Result<IbspHeader> {
        let mut magic = [0u8; 4];
        file.read_exact(&mut magic)?;

        if magic != [b'I', b'B', b'S', b'P'] {
            return Err(Error::new(format!(
                "invalid magic: {}{}{}{}",
                magic[0], magic[1], magic[2], magic[3]
            )));
        }
        let version = binary::read_i32(file)?;
        if version != IbspVersion::V59 as i32 && version != IbspVersion::V4 as i32 {
            return Err(Error::new(format!("invalid IBSP version {}", version)));
        }

        Ok(IbspHeader { magic, version })
    }

    fn read_lumps(file: &mut File) -> Result<Vec<IbspLump>> {
        let mut lumps: Vec<IbspLump> = Vec::new();
        for _ in 0..39 {
            let length = binary::read_u32(file)?;
            let offset = binary::read_u32(file)?;

            lumps.push(IbspLump { length, offset });
        }

        Ok(lumps)
    }

    fn read_materials(
        file: &mut File,
        version: i32,
        lumps: &Vec<IbspLump>,
    ) -> Result<Vec<IbspMaterial>> {
        let mut materials: Vec<IbspMaterial> = Vec::new();

        let mut materials_lump_idx = IbspLumpIndexV59::Materials as usize;
        if version == IbspVersion::V4 as i32 {
            materials_lump_idx = IbspLumpIndexV4::Materials as usize;
        }

        let materials_lump = lumps[materials_lump_idx];
        let material_size = size_of::<IbspMaterial>();

        file.seek(SeekFrom::Start(materials_lump.offset as u64))?;
        for _ in (0..materials_lump.length).step_by(material_size) {
            let mut name = [0u8; 64];
            file.read_exact(&mut name)?;
            let flag = binary::read_u64(file)?;
            materials.push(IbspMaterial { name, flag })
        }

        Ok(materials)
    }

    fn read_trianglesoups(
        file: &mut File,
        version: i32,
        lumps: &Vec<IbspLump>,
    ) -> Result<Vec<IbspTriangleSoup>> {
        let mut trianglesoups: Vec<IbspTriangleSoup> = Vec::new();

        let mut trianglesoups_lump_idx = IbspLumpIndexV59::TriangleSoups as usize;
        if version == IbspVersion::V4 as i32 {
            trianglesoups_lump_idx = IbspLumpIndexV4::TriangleSoups as usize;
        }

        let trianglesoups_lump = lumps[trianglesoups_lump_idx];
        let triannglesoup_size = size_of::<IbspTriangleSoup>();

        file.seek(SeekFrom::Start(trianglesoups_lump.offset as u64))?;
        for _ in (0..trianglesoups_lump.length).step_by(triannglesoup_size) {
            let material_idx = binary::read_u16(file)?;
            let draw_order = binary::read_u16(file)?;
            let vertices_offset = binary::read_u32(file)?;
            let vertices_length = binary::read_u16(file)?;
            let triangles_length = binary::read_u16(file)?;
            let triangles_offset = binary::read_u32(file)?;

            trianglesoups.push(IbspTriangleSoup {
                material_idx,
                draw_order,
                vertices_offset,
                vertices_length,
                triangles_length,
                triangles_offset,
            })
        }

        Ok(trianglesoups)
    }

    fn read_vertices(
        file: &mut File,
        version: i32,
        lumps: &Vec<IbspLump>,
    ) -> Result<Vec<IbspVertex>> {
        if version == IbspVersion::V59 as i32 {
            let vertices_lump_idx = IbspLumpIndexV59::Vertices as usize;
            let vertices_lump = lumps[vertices_lump_idx];
            let vertices = Self::read_vertices_v59(file, vertices_lump)?;
            return Ok(vertices);
        }

        let vertices_lump_idx = IbspLumpIndexV4::Vertices as usize;
        let vertices_lump = lumps[vertices_lump_idx];
        let vertices = Self::read_vertices_v4(file, vertices_lump)?;
        Ok(vertices)
    }

    fn read_vertices_v59(file: &mut File, vertices_lump: IbspLump) -> Result<Vec<IbspVertex>> {
        let mut vertices: Vec<IbspVertex> = Vec::new();
        let vertex_size: usize = 44;

        file.seek(SeekFrom::Start(vertices_lump.offset as u64))?;
        for _ in (0..vertices_lump.length).step_by(vertex_size) {
            let px = binary::read_f32(file)?;
            let py = binary::read_f32(file)?;
            let pz = binary::read_f32(file)?;

            let u = binary::read_f32(file)?;
            let v = binary::read_f32(file)?;

            match binary::skip(file, 8) {
                Ok(_) => (),
                Err(error) => return Err(Error::new(error.to_string())),
            }

            let nx = binary::read_f32(file)?;
            let ny = binary::read_f32(file)?;
            let nz = binary::read_f32(file)?;

            let mut color = [0u8; 4];
            file.read_exact(&mut color)?;

            vertices.push(IbspVertex {
                position: [px, py, pz],
                normal: [nx, ny, nz],
                color: [
                    color[0] as f32 / 255.0,
                    color[1] as f32 / 255.0,
                    color[2] as f32 / 255.0,
                    color[3] as f32 / 255.0,
                ],
                uv: [u, v],
            })
        }

        Ok(vertices)
    }

    fn read_vertices_v4(file: &mut File, vertices_lump: IbspLump) -> Result<Vec<IbspVertex>> {
        let mut vertices: Vec<IbspVertex> = Vec::new();
        let vertex_size: usize = 68;

        file.seek(SeekFrom::Start(vertices_lump.offset as u64))?;
        for _ in (0..vertices_lump.length).step_by(vertex_size) {
            let px = binary::read_f32(file)?;
            let py = binary::read_f32(file)?;
            let pz = binary::read_f32(file)?;

            let nx = binary::read_f32(file)?;
            let ny = binary::read_f32(file)?;
            let nz = binary::read_f32(file)?;

            let mut color = [0u8; 4];
            file.read_exact(&mut color)?;

            let u = binary::read_f32(file)?;
            let v = binary::read_f32(file)?;

            match binary::skip(file, 32) {
                Ok(_) => (),
                Err(error) => return Err(Error::new(error.to_string())),
            }

            vertices.push(IbspVertex {
                position: [px, py, pz],
                normal: [nx, ny, nz],
                color: [
                    color[0] as f32 / 255.0,
                    color[1] as f32 / 255.0,
                    color[2] as f32 / 255.0,
                    color[3] as f32 / 255.0,
                ],
                uv: [u, v],
            })
        }

        Ok(vertices)
    }

    fn read_triangles(
        file: &mut File,
        version: i32,
        lumps: &Vec<IbspLump>,
    ) -> Result<Vec<Triangle>> {
        let mut triangles: Vec<Triangle> = Vec::new();

        let mut triangles_lump_idx = IbspLumpIndexV59::Triangles as usize;
        if version == IbspVersion::V4 as i32 {
            triangles_lump_idx = IbspLumpIndexV4::Triangles as usize;
        }

        let triangles_lump = lumps[triangles_lump_idx];
        let triangle_size = size_of::<Triangle>();

        file.seek(SeekFrom::Start(triangles_lump.offset as u64))?;
        for _ in (0..triangles_lump.length).step_by(triangle_size) {
            let idx1 = binary::read_u16(file)?;
            let idx2 = binary::read_u16(file)?;
            let idx3 = binary::read_u16(file)?;

            triangles.push([idx1, idx2, idx3])
        }

        Ok(triangles)
    }

    fn read_entities(
        file: &mut File,
        version: i32,
        lumps: &Vec<IbspLump>,
    ) -> Result<Vec<IbspEntity>> {
        let mut entities: Vec<IbspEntity> = Vec::new();

        let mut entities_lump_idx = IbspLumpIndexV59::Entities as usize;
        if version == IbspVersion::V4 as i32 {
            entities_lump_idx = IbspLumpIndexV4::Entities as usize;
        }

        let entities_lump = lumps[entities_lump_idx];

        file.seek(SeekFrom::Start(entities_lump.offset as u64))?;
        let mut entities_data: Box<[u8]> =
            Vec::with_capacity(entities_lump.length as usize).into_boxed_slice();
        file.read_exact(&mut entities_data)?;

        let mut entities_string = String::from_utf8(entities_data.into_vec())?;
        entities_string = entities_string.trim_matches(char::from(0)).to_string();
        entities_string = format!("[{}]", entities_string);
        entities_string = str::replace(&entities_string, "}\n{\n", "},\n{\n");
        entities_string = str::replace(&entities_string, "\"\n\"", "\",\n\"");
        entities_string = str::replace(&entities_string, "\" \"", "\":\"");
        entities_string = str::replace(&entities_string, "\\", "/");

        let re = regex::Regex::new(r"^xmodel\/(.*)").unwrap();

        let entities_json = serde_json::from_str::<Vec<serde_json::Value>>(&entities_string)?;
        for entity in entities_json.iter() {
            let Some(name) = entity.get("model").unwrap_or(&serde_json::json!("")).as_str().and_then(|model| re.captures(model)).and_then(|caps| caps.get(1)).and_then(|m| Some(m.as_str())).and_then(|name| Some(name.to_string())) else {
                continue
            };

            let angles = Self::parse_transform(
                entity
                    .get("angles")
                    .unwrap_or(&serde_json::json!(""))
                    .as_str()
                    .unwrap(),
            )
            .unwrap_or([0f32; 3]);

            let origin = Self::parse_transform(
                entity
                    .get("origin")
                    .unwrap_or(&serde_json::json!(""))
                    .as_str()
                    .unwrap(),
            )
            .unwrap_or([0f32; 3]);

            let scale = Self::parse_transform(
                entity
                    .get("modelscale")
                    .unwrap_or(&serde_json::json!(""))
                    .as_str()
                    .unwrap(),
            )
            .unwrap_or([1f32; 3]);

            entities.push(IbspEntity {
                name,
                angles,
                origin,
                scale,
            });
        }

        Ok(entities)
    }

    fn parse_transform(transform: &str) -> Option<Vec3> {
        let t = transform.split(' ').collect::<Vec<&str>>();
        let l = t.len();

        if l == 3 {
            return Some([
                t[0].parse::<f32>().unwrap_or(0.0),
                t[1].parse::<f32>().unwrap_or(0.0),
                t[2].parse::<f32>().unwrap_or(0.0),
            ]);
        } else if l == 1 {
            return Some([
                t[0].parse::<f32>().unwrap_or(0.0),
                t[0].parse::<f32>().unwrap_or(0.0),
                t[0].parse::<f32>().unwrap_or(0.0),
            ]);
        }

        None
    }

    fn load_surfaces(triangle_soups: Vec<IbspTriangleSoup>, materials: Vec<IbspMaterial>, vertices: Vec<IbspVertex>, triangles: Vec<Triangle>) -> Vec<IbspSurface> {
        let mut surfaces: Vec<IbspSurface> = Vec::new();
        
        // TODO

        surfaces
    }



}
