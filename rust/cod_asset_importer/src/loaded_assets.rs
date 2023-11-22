use crate::{
    assets::{
        ibsp::{Ibsp, IbspEntity, IbspSurface},
        iwi::IWi,
        material::TextureType,
        xmodel::XModelVersion,
        xmodelpart::XModelPartBone,
        xmodelsurf::XModelSurfSurface,
    },
    utils::math::Vec3,
};
use pyo3::prelude::*;
use std::{collections::HashMap, iter, mem};

#[pyclass(module = "cod_asset_importer")]
pub struct LoadedIbsp {
    pub name: String,
    pub version: i32,
    pub materials: Vec<String>,
    pub entities: Vec<LoadedIbspEntity>,
    pub surfaces: Vec<LoadedSurface>,
}

#[pyclass(module = "cod_asset_importer")]
#[derive(Clone)]
pub struct LoadedIbspEntity {
    pub name: String,
    pub angles: [f32; 3],
    pub origin: [f32; 3],
    pub scale: [f32; 3],
}

#[pyclass(module = "cod_asset_importer")]
#[derive(Clone)]
pub struct LoadedModel {
    pub name: String,
    version: XModelVersion,
    angles: Vec3,
    origin: Vec3,
    scale: Vec3,
    materials: HashMap<String, LoadedMaterial>,
    surfaces: Vec<LoadedSurface>,
    bones: Vec<LoadedBone>,
}

#[pyclass(module = "cod_asset_importer")]
#[derive(Clone)]
pub struct LoadedMaterial {
    name: String,
    version: XModelVersion,
    textures: Vec<LoadedTexture>,
}

#[pyclass(module = "cod_asset_importer")]
#[derive(Clone)]
pub struct LoadedTexture {
    name: String,
    texture_type: TextureType,
    width: u16,
    height: u16,
    data: Vec<f32>,
}

#[pyclass(module = "cod_asset_importer")]
#[derive(Clone)]
pub struct LoadedSurface {
    material: String,
    vertices: Vec<f32>,
    normals: Vec<[f32; 3]>,
    colors: Vec<f32>,
    uvs: Vec<f32>,
    loops_len: usize,
    polygons_len: usize,
    polygon_loop_starts: Vec<usize>,
    polygon_loop_totals: Vec<usize>,
    polygon_vertices: Vec<u32>,
    weight_groups: HashMap<u16, HashMap<usize, f32>>,
}

#[pyclass(module = "cod_asset_importer")]
#[derive(Clone)]
pub struct LoadedBone {
    name: String,
    parent: i8,
    position: [f32; 3],
    rotation: [f32; 4],
}

#[pymethods]
impl LoadedModel {
    fn name(&self) -> &str {
        &self.name
    }

    fn version(&self) -> XModelVersion {
        self.version
    }

    fn angles(&self) -> [f32; 3] {
        self.angles
    }

    fn origin(&self) -> [f32; 3] {
        self.origin
    }

    fn scale(&self) -> [f32; 3] {
        self.scale
    }

    fn materials(&mut self) -> HashMap<String, LoadedMaterial> {
        mem::take(&mut self.materials)
    }

    fn surfaces(&mut self) -> Vec<LoadedSurface> {
        mem::take(&mut self.surfaces)
    }

    fn bones(&mut self) -> Vec<LoadedBone> {
        mem::take(&mut self.bones)
    }
}

#[pymethods]
impl LoadedMaterial {
    fn name(&self) -> &str {
        &self.name
    }

    fn version(&self) -> XModelVersion {
        self.version
    }

    fn textures(&mut self) -> Vec<LoadedTexture> {
        mem::take(&mut self.textures)
    }
}

#[pymethods]
impl LoadedTexture {
    fn name(&self) -> &str {
        &self.name
    }

    fn texture_type(&self) -> TextureType {
        self.texture_type
    }

    fn width(&self) -> u16 {
        self.width
    }

    fn height(&self) -> u16 {
        self.height
    }

    fn data(&mut self) -> Vec<f32> {
        mem::take(&mut self.data)
    }
}

#[pymethods]
impl LoadedSurface {
    fn material(&self) -> &str {
        &self.material
    }

    fn vertices(&mut self) -> Vec<f32> {
        mem::take(&mut self.vertices)
    }

    fn normals(&mut self) -> Vec<[f32; 3]> {
        mem::take(&mut self.normals)
    }

    fn colors(&mut self) -> Vec<f32> {
        mem::take(&mut self.colors)
    }

    fn uvs(&mut self) -> Vec<f32> {
        mem::take(&mut self.uvs)
    }

    fn loops_len(&self) -> usize {
        self.loops_len
    }

    fn polygons_len(&self) -> usize {
        self.polygons_len
    }

    fn polygon_loop_starts(&mut self) -> Vec<usize> {
        mem::take(&mut self.polygon_loop_starts)
    }

    fn polygon_loop_totals(&mut self) -> Vec<usize> {
        mem::take(&mut self.polygon_loop_totals)
    }

    fn polygon_vertices(&mut self) -> Vec<u32> {
        mem::take(&mut self.polygon_vertices)
    }

    fn weight_groups(&mut self) -> HashMap<u16, HashMap<usize, f32>> {
        mem::take(&mut self.weight_groups)
    }
}

#[pymethods]
impl LoadedBone {
    fn name(&self) -> &str {
        &self.name
    }

    fn parent(&self) -> i8 {
        self.parent
    }

    fn position(&self) -> [f32; 3] {
        self.position
    }

    fn rotation(&self) -> [f32; 4] {
        self.rotation
    }
}

#[pymethods]
impl LoadedIbsp {
    fn name(&self) -> &str {
        &self.name
    }

    fn surfaces(&mut self) -> Vec<LoadedSurface> {
        mem::take(&mut self.surfaces)
    }
}

#[pymethods]
impl LoadedIbspEntity {
    fn name(&self) -> &str {
        &self.name
    }

    fn angles(&self) -> [f32; 3] {
        self.angles
    }

    fn origin(&self) -> [f32; 3] {
        self.origin
    }

    fn scale(&self) -> [f32; 3] {
        self.scale
    }
}

impl LoadedModel {
    #[allow(clippy::too_many_arguments)]
    pub fn new(
        name: String,
        version: XModelVersion,
        angles: Vec3,
        origin: Vec3,
        scale: Vec3,
        materials: HashMap<String, LoadedMaterial>,
        surfaces: Vec<LoadedSurface>,
        bones: Vec<LoadedBone>,
    ) -> Self {
        LoadedModel {
            name,
            version,
            angles,
            origin,
            scale,
            materials,
            surfaces,
            bones,
        }
    }

    pub fn set_angles(&mut self, angles: Vec3) {
        self.angles = angles;
    }

    pub fn set_origin(&mut self, origin: Vec3) {
        self.origin = origin;
    }

    pub fn set_scale(&mut self, scale: Vec3) {
        self.scale = scale;
    }
}

impl LoadedMaterial {
    pub fn new(name: String, textures: Vec<LoadedTexture>, version: XModelVersion) -> Self {
        LoadedMaterial {
            name,
            textures,
            version,
        }
    }
}

impl LoadedTexture {
    pub fn set_texture_type(&mut self, texture_type: TextureType) {
        self.texture_type = texture_type;
    }
    pub fn set_name(&mut self, name: String) {
        self.name = name;
    }
}

impl LoadedSurface {
    pub fn set_material(&mut self, material: String) {
        self.material = material;
    }
}

impl From<IWi> for LoadedTexture {
    fn from(iwi: IWi) -> Self {
        Self {
            name: "".to_string(),
            texture_type: "".to_string().into(),
            width: iwi.width,
            height: iwi.height,
            data: iwi.data,
        }
    }
}

impl From<XModelPartBone> for LoadedBone {
    fn from(xmodelpart_bone: XModelPartBone) -> Self {
        Self {
            name: xmodelpart_bone.name,
            parent: xmodelpart_bone.parent,
            position: xmodelpart_bone.local_transform.position,
            rotation: xmodelpart_bone.local_transform.rotation,
        }
    }
}

impl From<IbspSurface> for LoadedSurface {
    fn from(ibsp_surface: IbspSurface) -> Self {
        let vertices: Vec<f32> = ibsp_surface
            .vertices
            .iter()
            .flat_map(|v| v.position)
            .collect();

        let normals: Vec<[f32; 3]> = ibsp_surface.vertices.iter().map(|v| v.normal).collect();

        let colors = ibsp_surface.vertices.iter().flat_map(|v| v.color).collect();

        let uvs: Vec<f32> = ibsp_surface
            .triangles
            .iter()
            .flat_map(|&i| ibsp_surface.vertices[i as usize].uv)
            .collect();

        let loops_len = ibsp_surface.triangles.len();

        let polygons_len = loops_len / 3;

        let polygon_loop_starts: Vec<usize> = (0..polygons_len).map(|i| i * 3).collect();

        let polygon_loop_totals: Vec<usize> = iter::repeat(3).take(polygons_len).collect();

        let weight_groups: HashMap<u16, HashMap<usize, f32>> = HashMap::new();

        Self {
            material: ibsp_surface.material,
            vertices,
            normals,
            colors,
            uvs,
            loops_len,
            polygons_len,
            polygon_loop_starts,
            polygon_loop_totals,
            polygon_vertices: ibsp_surface.triangles,
            weight_groups,
        }
    }
}

impl From<XModelSurfSurface> for LoadedSurface {
    fn from(xmodelsurf_surface: XModelSurfSurface) -> Self {
        let vertices: Vec<f32> = xmodelsurf_surface
            .vertices
            .iter()
            .flat_map(|v| v.position)
            .collect();

        let normals: Vec<[f32; 3]> = xmodelsurf_surface
            .vertices
            .iter()
            .map(|v| v.normal)
            .collect();

        let colors = xmodelsurf_surface
            .vertices
            .iter()
            .flat_map(|v| v.color)
            .collect();

        let uvs: Vec<f32> = xmodelsurf_surface
            .triangles
            .iter()
            .flat_map(|&i| xmodelsurf_surface.vertices[i as usize].uv)
            .collect();

        let loops_len = xmodelsurf_surface.triangles.len();

        let polygons_len = loops_len / 3;

        let polygon_loop_starts: Vec<usize> = (0..polygons_len).map(|i| i * 3).collect();

        let polygon_loop_totals: Vec<usize> = iter::repeat(3).take(polygons_len).collect();

        let polygon_vertices: Vec<u32> = xmodelsurf_surface
            .triangles
            .iter()
            .map(|&t| t.into())
            .collect();

        let mut weight_groups: HashMap<u16, HashMap<usize, f32>> = HashMap::new();
        for (vertex_index, vertex) in xmodelsurf_surface.vertices.iter().enumerate() {
            for weight in vertex.weights.iter() {
                weight_groups
                    .entry(weight.bone)
                    .or_default()
                    .insert(vertex_index, weight.influence);
            }
        }

        Self {
            material: String::from(""),
            vertices,
            normals,
            colors,
            uvs,
            loops_len,
            polygons_len,
            polygon_loop_starts,
            polygon_loop_totals,
            polygon_vertices,
            weight_groups,
        }
    }
}

impl From<IbspEntity> for LoadedIbspEntity {
    fn from(ibps_entity: IbspEntity) -> Self {
        Self {
            name: ibps_entity.name,
            angles: ibps_entity.angles,
            origin: ibps_entity.origin,
            scale: ibps_entity.scale,
        }
    }
}

impl From<Ibsp> for LoadedIbsp {
    fn from(ibsp: Ibsp) -> Self {
        Self {
            name: ibsp.name,
            version: ibsp.version,
            materials: ibsp.materials.into_iter().map(|m| m.get_name()).collect(),
            entities: ibsp.entities.into_iter().map(|e| e.into()).collect(),
            surfaces: ibsp.surfaces.into_iter().map(|s| s.into()).collect(),
        }
    }
}
