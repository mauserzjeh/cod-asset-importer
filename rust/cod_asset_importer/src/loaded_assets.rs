use crate::{
    assets::{
        ibsp::{IbspEntity, IbspSurface, IbspVertex},
        iwi::IWi,
        xmodelpart::XModelPartBone,
        xmodelsurf::{XModelSurfSurface, XModelSurfVertex, XModelSurfWeight},
    },
    debug_log,
    utils::math::Vec3,
};
use pyo3::prelude::*;
use std::{iter, mem};

#[pyclass(module = "cod_asset_importer")]
pub struct LoadedIbsp {
    pub name: String,
    pub version: i32,
    pub materials: Vec<String>,
    pub entities: Vec<LoadedIbspEntity>,
    pub surfaces: Vec<LoadedIbspSurface>,
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
pub struct LoadedIbspSurface {
    material: String,
    vertices: Vec<f32>,
    normals: Vec<[f32; 3]>,
    loop_uvs: Vec<f32>,
    loop_colors: Vec<[f32; 4]>,
    loops_len: usize,
    polygons_len: usize,
    polygon_loop_starts: Vec<usize>,
    polygon_loop_totals: Vec<usize>,
    polygon_vertices: Vec<u32>,
}

#[pyclass(module = "cod_asset_importer")]
#[derive(Clone)]
pub struct LoadedModel {
    pub name: String,
    version: u16,
    angles: Vec3,
    origin: Vec3,
    scale: Vec3,
    materials: Vec<LoadedMaterial>,
    surfaces: Vec<LoadedSurface>,
    bones: Vec<LoadedBone>,
}

#[pyclass(module = "cod_asset_importer")]
#[derive(Clone)]
pub struct LoadedMaterial {
    name: String,
    version: i32,
    textures: Vec<LoadedTexture>,
}

#[pyclass(module = "cod_asset_importer")]
#[derive(Clone)]
pub struct LoadedTexture {
    name: String,
    texture_type: String,
    width: u16,
    height: u16,
    data: Vec<f32>,
}

#[pyclass(module = "cod_asset_importer")]
#[derive(Clone)]
pub struct LoadedSurface {
    vertices: Vec<LoadedVertex>,
    triangles: Vec<[u16; 3]>,
}

#[pyclass(module = "cod_asset_importer")]
#[derive(Clone)]
pub struct LoadedVertex {
    normal: [f32; 3],
    color: [f32; 4],
    uv: [f32; 2],
    bone: u16,
    position: [f32; 3],
    weights: Vec<LoadedWeight>,
}

#[pyclass(module = "cod_asset_importer")]
#[derive(Clone, Copy)]
pub struct LoadedWeight {
    bone: u16,
    influence: f32,
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

    fn version(&self) -> u16 {
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

    fn materials(&mut self) -> Vec<LoadedMaterial> {
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

    fn version(&self) -> i32 {
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

    fn texture_type(&self) -> &str {
        &self.texture_type
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
    fn vertices(&mut self) -> Vec<LoadedVertex> {
        mem::take(&mut self.vertices)
    }

    fn triangles(&mut self) -> Vec<[u16; 3]> {
        mem::take(&mut self.triangles)
    }
}

#[pymethods]
impl LoadedVertex {
    fn normal(&self) -> [f32; 3] {
        self.normal
    }

    fn color(&self) -> [f32; 4] {
        self.color
    }

    fn uv(&self) -> [f32; 2] {
        self.uv
    }

    fn bone(&self) -> u16 {
        self.bone
    }

    fn position(&self) -> [f32; 3] {
        self.position
    }

    fn weights(&self) -> Vec<LoadedWeight> {
        self.weights.clone() // TODO review if can we do weights without cloning
                             // mem::take(&mut self.weights)
    }
}

#[pymethods]
impl LoadedWeight {
    fn bone(&self) -> u16 {
        self.bone
    }

    fn influence(&self) -> f32 {
        self.influence
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

    fn version(&self) -> i32 {
        self.version
    }

    fn materials(&mut self) -> Vec<String> {
        mem::take(&mut self.materials)
    }

    fn entities(&mut self) -> Vec<LoadedIbspEntity> {
        mem::take(&mut self.entities)
    }

    fn surfaces(&mut self) -> Vec<LoadedIbspSurface> {
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

#[pymethods]
impl LoadedIbspSurface {
    fn material(&self) -> &str {
        &self.material
    }

    fn vertices(&mut self) -> Vec<f32> {
        mem::take(&mut self.vertices)
    }

    fn normals(&mut self) -> Vec<[f32; 3]> {
        mem::take(&mut self.normals)
    }

    fn loop_uvs(&mut self) -> Vec<f32> {
        mem::take(&mut self.loop_uvs)
    }

    fn loop_colors(&mut self) -> Vec<[f32; 4]> {
        mem::take(&mut self.loop_colors)
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
}

impl LoadedIbsp {
    pub fn new(
        name: String,
        version: i32,
        materials: Vec<String>,
        entities: Vec<LoadedIbspEntity>,
        surfaces: Vec<LoadedIbspSurface>,
    ) -> Self {
        LoadedIbsp {
            name,
            version,
            materials,
            entities,
            surfaces,
        }
    }
}

impl LoadedModel {
    #[allow(clippy::too_many_arguments)]
    pub fn new(
        name: String,
        version: u16,
        angles: Vec3,
        origin: Vec3,
        scale: Vec3,
        materials: Vec<LoadedMaterial>,
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
    pub fn new(name: String, textures: Vec<LoadedTexture>, version: i32) -> Self {
        LoadedMaterial {
            name,
            textures,
            version,
        }
    }
}

impl LoadedTexture {
    pub fn set_texture_type(&mut self, texture_type: String) {
        self.texture_type = texture_type;
    }
    pub fn set_name(&mut self, name: String) {
        self.name = name;
    }
}

impl From<IWi> for LoadedTexture {
    fn from(iwi: IWi) -> Self {
        Self {
            name: "".to_string(),
            texture_type: "".to_string(),
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

impl From<XModelSurfWeight> for LoadedWeight {
    fn from(xmodelsurf_weight: XModelSurfWeight) -> Self {
        Self {
            bone: xmodelsurf_weight.bone,
            influence: xmodelsurf_weight.influence,
        }
    }
}

impl From<XModelSurfVertex> for LoadedVertex {
    fn from(xmodelsurf_vertex: XModelSurfVertex) -> Self {
        Self {
            normal: xmodelsurf_vertex.normal,
            color: xmodelsurf_vertex.color,
            uv: xmodelsurf_vertex.uv,
            bone: xmodelsurf_vertex.bone,
            position: xmodelsurf_vertex.position,
            weights: xmodelsurf_vertex
                .weights
                .into_iter()
                .map(|w| w.into())
                .collect(),
        }
    }
}

impl From<IbspVertex> for LoadedVertex {
    fn from(ibsp_vertex: IbspVertex) -> Self {
        Self {
            normal: ibsp_vertex.normal,
            color: ibsp_vertex.color,
            uv: ibsp_vertex.uv,
            bone: 0,
            position: ibsp_vertex.position,
            weights: Vec::new(),
        }
    }
}

impl From<XModelSurfSurface> for LoadedSurface {
    fn from(xmodelsurf_surface: XModelSurfSurface) -> Self {
        Self {
            vertices: xmodelsurf_surface
                .vertices
                .into_iter()
                .map(|v| v.into())
                .collect(),
            triangles: xmodelsurf_surface.triangles,
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

impl From<IbspSurface> for LoadedIbspSurface {
    fn from(ibsp_surface: IbspSurface) -> Self {
        let vertices: Vec<f32> = ibsp_surface
            .vertices
            .iter()
            .flat_map(|v| v.position)
            .collect();

        let normals: Vec<[f32; 3]> = ibsp_surface.vertices.iter().map(|v| v.normal).collect();

        let loop_uvs: Vec<f32> = ibsp_surface
            .triangles
            .iter()
            .flat_map(|t| [t[0], t[2], t[1]].map(|i| ibsp_surface.vertices[i as usize].uv))
            .flatten()
            .collect();

        let loop_colors: Vec<[f32; 4]> = ibsp_surface
            .triangles
            .iter()
            .flat_map(|t| [t[0], t[2], t[1]].map(|i| ibsp_surface.vertices[i as usize].color))
            .collect();

        let polygons_len = ibsp_surface.triangles.len();

        let loops_len = polygons_len * 3;

        let polygon_loop_starts: Vec<usize> =
            (0..ibsp_surface.triangles.len()).map(|i| i * 3).collect();

        let polygon_loop_totals: Vec<usize> = iter::repeat(3).take(polygons_len).collect();

        let polygon_vertices: Vec<u32> = ibsp_surface
            .triangles
            .iter()
            .flat_map(|t| [t[0], t[2], t[1]])
            .collect();

        Self {
            material: ibsp_surface.material,
            vertices,
            normals,
            loop_uvs,
            loop_colors,
            polygons_len,
            loops_len,
            polygon_loop_starts,
            polygon_loop_totals,
            polygon_vertices,
        }
    }
}
