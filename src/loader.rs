use super::loaded_assets::{LoadedMaterial, LoadedModel};
use crate::{
    assets::{
        iwi::{self, IWi},
        material::{self, Material},
        xmodel::{self, XModel},
        xmodelpart::{self, XModelPart},
        xmodelsurf::{self, XModelSurf},
    },
    error_log,
    utils::Result,
};
use pyo3::{exceptions::PyBaseException, prelude::*};
use std::{collections::HashMap, path::PathBuf};

#[pyclass(module = "cod_asset_importer")]
pub struct Loader {
    importer: PyObject,
}

#[pymethods]
impl Loader {
    #[new]
    #[pyo3(signature = (importer))]
    fn new(importer: PyObject) -> PyResult<Self> {
        Ok(Loader { importer })
    }

    #[pyo3(signature = (asset_path, file_path))]
    fn import_xmodel(&mut self, py: Python, asset_path: &str, file_path: &str) -> PyResult<()> {
        let importer_ref = self.importer.as_ref(py);

        let loaded_model =
            match Self::load_xmodel(PathBuf::from(asset_path), PathBuf::from(file_path)) {
                Ok(loaded_model) => loaded_model,
                Err(error) => {
                    error_log!("{}", error);
                    return Err(PyBaseException::new_err(error.to_string()));
                }
            };

        match importer_ref.call_method1("xmodel", (loaded_model,)) {
            Ok(_) => Ok(()),
            Err(error) => {
                error_log!("{}", error);
                Err(error)
            }
        }
    }
}

impl Loader {
    fn load_xmodel(asset_path: PathBuf, file_path: PathBuf) -> Result<LoadedModel> {
        let xmodel = XModel::load(file_path)?;
        let lod0 = xmodel.lods[0].clone();

        let xmodelpart_file_path = asset_path
            .join(xmodelpart::ASSETPATH)
            .join(lod0.name.clone());
        let xmodelpart = match XModelPart::load(xmodelpart_file_path) {
            Ok(xmodelpart) => Some(xmodelpart),
            Err(error) => {
                error_log!("{}", error);
                None
            }
        };

        let xmodelsurf_file_path = asset_path.join(xmodelsurf::ASSETPATH).join(lod0.name);
        let xmodelsurf = XModelSurf::load(xmodelsurf_file_path, xmodelpart.clone())?;

        let mut loaded_materials: Vec<LoadedMaterial> = Vec::new();
        if xmodel.version != xmodel::XModelVersion::V14 as u16 {
            for mat in lod0.materials {
                let loaded_material =
                    match Self::load_material(asset_path.clone(), mat, xmodel.version as i32) {
                        Ok(material) => material,
                        Err(error) => {
                            error_log!("{}", error);
                            continue;
                        }
                    };

                loaded_materials.push(loaded_material);
            }
        }

        Ok(LoadedModel::new(
            xmodel,
            xmodelpart,
            xmodelsurf,
            loaded_materials,
            [0f32; 3],
            [0f32; 3],
            [1f32; 3],
        ))
    }

    fn load_material(
        asset_path: PathBuf,
        material_name: String,
        version: i32,
    ) -> Result<LoadedMaterial> {
        let material_file_path = asset_path.join(material::ASSETPATH).join(&material_name);
        let material = Material::load(material_file_path, version)?;

        let mut loaded_textures: HashMap<String, IWi> = HashMap::new();
        for texture in material.textures {
            if loaded_textures.contains_key(&texture.name) {
                continue;
            }

            let texture_file_path = asset_path.join(iwi::ASSETPATH).join(&texture.name);
            let loaded_texture = match IWi::load(texture_file_path) {
                Ok(iwi) => iwi,
                Err(error) => {
                    error_log!("{}", error);
                    continue;
                }
            };

            loaded_textures.insert(texture.name, loaded_texture);
        }

        Ok(LoadedMaterial::new(material_name, loaded_textures))
    }
}
