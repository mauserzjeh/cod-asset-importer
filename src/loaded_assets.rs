use crate::{
    assets::{
        iwi::IWi,
        xmodel::XModel,
        xmodelpart::XModelPart,
        xmodelsurf::{XModelSurf, XModelSurfSurface, XModelSurfVertex},
    },
    utils::math::Vec3,
};
use pyo3::prelude::*;
use std::{collections::HashMap, mem};

#[pyclass(module = "cod_asset_importer")]
pub struct LoadedModel {
    xmodel: XModel,
    xmodelpart: Option<XModelPart>,
    xmodelsurf: XModelSurf,
    materials: Vec<LoadedMaterial>,
    angles: Vec3,
    origin: Vec3,
    scale: Vec3,
}

#[pyclass(module = "cod_asset_importer")]
pub struct LoadedMaterial {
    name: String,
    textures: HashMap<String, IWi>,
}

#[pyclass(module = "cod_asset_importer")]
pub struct LoadedSurface {
    vertices: Vec<LoadedVertex>,
    triangles: Vec<[u16; 3]>,
}

#[pyclass(module = "cod_asset_importer")]
pub struct LoadedVertex {
    normal: [f32; 3],
    color: [f32; 4],
    uv: [f32; 2],
    bone: u16,
    position: [f32; 3],
    // weights TODO
}

#[pymethods]
impl LoadedModel {
    fn name(&self) -> &str {
        &self.xmodel.name
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
        let surfaces = mem::take(&mut self.xmodelsurf.surfaces);
        surfaces.into_iter().map(|s| s.into()).collect()
    }

    // TODO bones / skeleton
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
}

impl LoadedModel {
    pub fn new(
        xmodel: XModel,
        xmodelpart: Option<XModelPart>,
        xmodelsurf: XModelSurf,
        materials: Vec<LoadedMaterial>,
        angles: Vec3,
        origin: Vec3,
        scale: Vec3,
    ) -> Self {
        LoadedModel {
            xmodel,
            xmodelpart,
            xmodelsurf,
            materials,
            angles,
            origin,
            scale,
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
    pub fn new(name: String, textures: HashMap<String, IWi>) -> Self {
        LoadedMaterial { name, textures }
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
