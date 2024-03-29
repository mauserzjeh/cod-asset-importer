use crate::utils::{
    binary,
    error::Error,
    math::{color_from_vec, uv_from_vec, vec3_from_vec, Color, Vec3, UV},
    path::file_name_without_ext,
    Result,
};
use std::{
    collections::{hash_map::Entry::Vacant, HashMap},
    fs::File,
    io::{Seek, SeekFrom},
    mem::size_of,
    path::PathBuf,
    str,
};
use valid_enum::ValidEnum;

#[derive(Debug)]
pub struct Ibsp {
    pub name: String,
    pub version: i32,
    pub materials: Vec<IbspMaterial>,
    pub entities: Vec<IbspEntity>,
    pub surfaces: Vec<IbspSurface>,
}

#[derive(Debug)]
pub struct IbspHeader {
    magic: [u8; 4],
    version: i32,
}

#[derive(Clone, Copy)]
struct IbspLump {
    length: u32,
    offset: u32,
}

#[derive(Clone, Copy, Debug)]
pub struct IbspMaterial {
    name: [u8; 64],
    flag: u64,
}

#[derive(Debug)]
struct IbspTriangleSoup {
    material_idx: u16,
    draw_order: u16,
    vertices_offset: u32,
    vertices_length: u16,
    triangles_length: u16,
    triangles_offset: u32,
}

#[derive(Clone, Copy, Debug)]
pub struct IbspVertex {
    pub position: Vec3,
    pub normal: Vec3,
    pub color: Color,
    pub uv: UV,
}

#[derive(Debug)]
pub struct IbspEntity {
    pub name: String,
    pub angles: Vec3,
    pub origin: Vec3,
    pub scale: Vec3,
}

#[derive(Debug)]
pub struct IbspSurface {
    pub material: String,
    pub vertices: Vec<IbspVertex>,
    pub triangles: Vec<u32>,
}

#[derive(ValidEnum)]
#[valid_enum(i32)]
pub enum IbspVersion {
    // CoD1 & CoDUO
    V59 = 0x3B,
    // CoD2
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
    pub fn load(file_path: PathBuf) -> Result<Ibsp> {
        let mut file = File::open(&file_path)?;
        let name = file_name_without_ext(file_path);
        let header = Self::read_header(&mut file)?;
        let lumps = Self::read_lumps(&mut file)?;
        let materials = Self::read_materials(&mut file, header.version, &lumps)?;
        let triangle_soups = Self::read_trianglesoups(&mut file, header.version, &lumps)?;
        let vertices = Self::read_vertices(&mut file, header.version, &lumps)?;
        let triangles = Self::read_triangles(&mut file, header.version, &lumps)?;
        let entities = Self::read_entities(&mut file, header.version, &lumps)?;
        let surfaces = Self::load_surfaces(triangle_soups, &materials, vertices, triangles);

        Ok(Ibsp {
            name,
            version: header.version,
            materials,
            entities,
            surfaces,
        })
    }

    fn read_header(file: &mut File) -> Result<IbspHeader> {
        let magic = binary::read_vec::<u8>(file, 4)?;
        if magic != [b'I', b'B', b'S', b'P'] {
            return Err(Error::new(format!(
                "invalid magic: {}",
                str::from_utf8(&magic).unwrap()
            )));
        }

        let version = binary::read::<i32>(file)?;
        match IbspVersion::valid(version) {
            Some(_) => (),
            None => return Err(Error::new(format!("invalid IBSP version {}", version))),
        }

        Ok(IbspHeader {
            magic: magic.try_into().unwrap(),
            version,
        })
    }

    fn read_lumps(file: &mut File) -> Result<Vec<IbspLump>> {
        let mut lumps: Vec<IbspLump> = Vec::new();
        for _ in 0..39 {
            let lump_data = binary::read_vec::<u32>(file, 2)?;
            lumps.push(IbspLump {
                length: lump_data[0],
                offset: lump_data[1],
            });
        }

        Ok(lumps)
    }

    fn read_materials(
        file: &mut File,
        version: i32,
        lumps: &[IbspLump],
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
            let name = binary::read_vec::<u8>(file, 64)?;
            let flag = binary::read::<u64>(file)?;
            materials.push(IbspMaterial {
                name: name.try_into().unwrap(),
                flag,
            })
        }

        Ok(materials)
    }

    fn read_trianglesoups(
        file: &mut File,
        version: i32,
        lumps: &[IbspLump],
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
            let material_idx = binary::read::<u16>(file)?;
            let draw_order = binary::read::<u16>(file)?;
            let vertices_offset = binary::read::<u32>(file)?;
            let vertices_length = binary::read::<u16>(file)?;
            let triangles_length = binary::read::<u16>(file)?;
            let triangles_offset = binary::read::<u32>(file)?;

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

    fn read_vertices(file: &mut File, version: i32, lumps: &[IbspLump]) -> Result<Vec<IbspVertex>> {
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
            let p = binary::read_vec::<f32>(file, 3)?;
            let uv = binary::read_vec::<f32>(file, 2)?;

            binary::skip(file, 8)?;

            let n = binary::read_vec::<f32>(file, 3)?;
            let color = binary::read_vec::<u8>(file, 4)?;

            vertices.push(IbspVertex {
                position: vec3_from_vec(p).unwrap(),
                normal: vec3_from_vec(n).unwrap(),
                color: color_from_vec(color).unwrap(),
                uv: uv_from_vec(uv, true).unwrap(),
            })
        }

        Ok(vertices)
    }

    fn read_vertices_v4(file: &mut File, vertices_lump: IbspLump) -> Result<Vec<IbspVertex>> {
        let mut vertices: Vec<IbspVertex> = Vec::new();
        let vertex_size: usize = 68;

        file.seek(SeekFrom::Start(vertices_lump.offset as u64))?;
        for _ in (0..vertices_lump.length).step_by(vertex_size) {
            let p = binary::read_vec::<f32>(file, 3)?;
            let n = binary::read_vec::<f32>(file, 3)?;
            let color = binary::read_vec::<u8>(file, 4)?;
            let uv = binary::read_vec::<f32>(file, 2)?;

            binary::skip(file, 32)?;

            vertices.push(IbspVertex {
                position: vec3_from_vec(p).unwrap(),
                normal: vec3_from_vec(n).unwrap(),
                color: color_from_vec(color).unwrap(),
                uv: uv_from_vec(uv, false).unwrap(),
            })
        }

        Ok(vertices)
    }

    fn read_triangles(file: &mut File, version: i32, lumps: &[IbspLump]) -> Result<Vec<u16>> {
        let mut triangles_lump_idx = IbspLumpIndexV59::Triangles as usize;
        if version == IbspVersion::V4 as i32 {
            triangles_lump_idx = IbspLumpIndexV4::Triangles as usize;
        }

        let triangles_lump = lumps[triangles_lump_idx];

        file.seek(SeekFrom::Start(triangles_lump.offset as u64))?;
        let triangles_amount = triangles_lump.length as usize / size_of::<u16>();
        let triangles = binary::read_vec::<u16>(file, triangles_amount)?;

        Ok(triangles)
    }

    fn read_entities(file: &mut File, version: i32, lumps: &[IbspLump]) -> Result<Vec<IbspEntity>> {
        let mut entities: Vec<IbspEntity> = Vec::new();

        let mut entities_lump_idx = IbspLumpIndexV59::Entities as usize;
        if version == IbspVersion::V4 as i32 {
            entities_lump_idx = IbspLumpIndexV4::Entities as usize;
        }

        let entities_lump = lumps[entities_lump_idx];

        file.seek(SeekFrom::Start(entities_lump.offset as u64))?;
        let entities_data = binary::read_vec::<u8>(file, entities_lump.length as usize)?;

        let mut entities_string = String::from_utf8(entities_data)?;
        entities_string = entities_string.trim_matches(char::from(0)).to_string();
        entities_string = format!("[{}]", entities_string);
        entities_string = entities_string.replace("}\n{\n", "},\n{\n");
        entities_string = entities_string.replace("\"\n\"", "\",\n\"");
        entities_string = entities_string.replace("\" \"", "\":\"");
        entities_string = entities_string.replace('\\', "/");

        let re = regex::Regex::new(r"^xmodel\/(.*)").unwrap();
        let filter_classes = ["spawn", "actor"];
        let filter_models = ["fx"];

        let entities_json = serde_json::from_str::<Vec<serde_json::Value>>(&entities_string)?;
        for entity in entities_json.iter() {
            let def = serde_json::json!("");
            let Some(name) = entity
                .get("model")
                .unwrap_or(&def)
                .as_str()
                .and_then(|model| re.captures(model))
                .and_then(|caps| caps.get(1))
                .map(|m| m.as_str())
            else {
                continue;
            };

            if filter_models.iter().any(|&s| name == s) {
                continue;
            }

            if let Some(classname) = entity.get("classname").and_then(|c| c.as_str()) {
                if filter_classes.iter().any(|&s| classname.contains(s)) {
                    continue;
                }
            }

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
                name: name.to_string(),
                angles,
                origin,
                scale,
            });
        }

        Ok(entities)
    }

    fn parse_transform(transform: &str) -> Option<Vec3> {
        if transform.is_empty() {
            return None;
        }

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

    fn load_surfaces(
        triangle_soups: Vec<IbspTriangleSoup>,
        materials: &[IbspMaterial],
        vertices: Vec<IbspVertex>,
        triangles: Vec<u16>,
    ) -> Vec<IbspSurface> {
        let mut surfaces: Vec<IbspSurface> = Vec::new();

        for ts in triangle_soups.iter() {
            let surface_material = materials[ts.material_idx as usize].get_name();
            let mut surface_vertices: Vec<IbspVertex> = Vec::new();
            let mut surface_triangles: Vec<u32> = Vec::new();
            let mut index_mapping: HashMap<u32, u32> = HashMap::new();

            let start = ts.triangles_offset as usize;
            let end = ts.triangles_offset as usize + ts.triangles_length as usize;
            for i in (start..end).step_by(3) {
                let mut t = [0u32; 3];
                for j in 0..3 {
                    let v_idx = triangles[i + j] as u32 + ts.vertices_offset;
                    let vertex = vertices[v_idx as usize];
                    let t_idx = surface_vertices.len() as u32;

                    if let Vacant(entry) = index_mapping.entry(v_idx) {
                        entry.insert(t_idx);
                        surface_vertices.push(vertex);
                    }

                    t[j] = *index_mapping.get(&v_idx).unwrap();
                }
                surface_triangles.extend_from_slice(&[t[0], t[2], t[1]]);
            }

            surfaces.push(IbspSurface {
                material: surface_material,
                vertices: surface_vertices,
                triangles: surface_triangles,
            })
        }

        surfaces
    }
}

impl IbspMaterial {
    pub fn get_name(&self) -> String {
        str::from_utf8(&self.name)
            .unwrap()
            .trim_matches(char::from(0))
            .to_string()
    }
}
