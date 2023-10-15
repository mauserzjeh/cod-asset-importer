use crate::{
    assets::{
        ibsp::{Ibsp, IbspVersion},
        iwi::{self, IWi},
        material::{self, Material},
        xmodel::{self, XModel, XModelVersion},
        xmodelpart::{self, XModelPart},
        xmodelsurf::{self, XModelSurf},
    },
    error_log, info_log,
    loaded_assets::{LoadedBone, LoadedIbsp, LoadedMaterial, LoadedModel, LoadedTexture},
    thread_pool::ThreadPool,
    utils::Result,
    wait_group::WaitGroup,
};
use pyo3::{exceptions::PyBaseException, prelude::*};
use std::{path::PathBuf, time::Instant};

#[pyclass(module = "cod_asset_importer")]
pub struct Loader {
    importer: PyObject,
    threads: usize,
}

#[pymethods]
impl Loader {
    #[new]
    #[pyo3(signature = (importer, threads))]
    fn new(importer: PyObject, threads: usize) -> Self {
        Loader { importer, threads }
    }

    #[pyo3(signature = (asset_path, file_path))]
    fn import_bsp(&self, py: Python, asset_path: &str, file_path: &str) -> PyResult<()> {
        let start = Instant::now();
        let importer_ref = self.importer.as_ref(py);

        let loaded_ibsp = match Self::load_ibsp(PathBuf::from(file_path)) {
            Ok(loaded_ibsp) => loaded_ibsp,
            Err(error) => {
                error_log!("{}", error);
                return Err(PyBaseException::new_err(error.to_string()));
            }
        };

        let ibsp_name = loaded_ibsp.name.clone();
        let materials = loaded_ibsp.materials.clone();
        let entities = loaded_ibsp.entities.clone();

        // let pool = ThreadPool::new(self.threads);
        // let wg = WaitGroup::new();

        for material in materials {
            let material_name = material.clone();
            let start_material = Instant::now();
            let mut version = XModelVersion::V14;
            if loaded_ibsp.version == IbspVersion::V4 as i32 {
                version = XModelVersion::V20;
            }

            let loaded_material = if loaded_ibsp.version == IbspVersion::V59 as i32 {
                Ok(LoadedMaterial::new(material, Vec::new(), version as i32))
            } else {
                Self::load_material(PathBuf::from(asset_path), material, version as i32)
            };

            match loaded_material {
                Ok(loaded_material) => {
                    match importer_ref.call_method1("material", (loaded_material, false)) {
                        Ok(_) => {
                            info_log!(
                                "{} imported in {:?}",
                                material_name,
                                start_material.elapsed()
                            );
                            ()
                        }
                        Err(error) => {
                            error_log!("{}", error)
                        }
                    }
                }
                Err(error) => {
                    error_log!("{}", error);
                }
            }

            // let wg = wg.clone();
            // pool.execute(move || {
            //     // should execute load/import in the pool

            //     drop(wg);
            // });
        }

        match importer_ref.call_method1("ibsp", (loaded_ibsp,)) {
            Ok(_) => (),
            Err(error) => {
                error_log!("{}", error)
            }
        }

        for entity in entities {
            match Self::import_xmodel(
                &self,
                py,
                asset_path,
                PathBuf::from(asset_path)
                    .join(xmodel::ASSETPATH)
                    .join(entity.name)
                    .display()
                    .to_string()
                    .as_str(),
                entity.angles,
                entity.origin,
                entity.scale,
            ) {
                Ok(_) => (),
                Err(error) => {
                    error_log!("{}", error);
                }
            }
        }

        info_log!("{} imported in {:?}", ibsp_name, start.elapsed());
        Ok(())
    }

    #[pyo3(signature = (asset_path, file_path, angles, origin, scale))]
    fn import_xmodel(
        &self,
        py: Python,
        asset_path: &str,
        file_path: &str,
        angles: [f32; 3],
        origin: [f32; 3],
        scale: [f32; 3],
    ) -> PyResult<()> {
        let start = Instant::now();

        let importer_ref = self.importer.as_ref(py);

        let mut loaded_model =
            match Self::load_xmodel(PathBuf::from(asset_path), PathBuf::from(file_path)) {
                Ok(loaded_model) => loaded_model,
                Err(error) => {
                    error_log!("{}", error);
                    return Err(PyBaseException::new_err(error.to_string()));
                }
            };

        loaded_model.set_angles(angles);
        loaded_model.set_origin(origin);
        loaded_model.set_scale(scale);
        let model_name = loaded_model.name.clone();

        match importer_ref.call_method1("xmodel", (loaded_model,)) {
            Ok(_) => {
                info_log!("{} imported in {:?}", model_name, start.elapsed());
                Ok(())
            }
            Err(error) => {
                error_log!("{}", error);
                Err(error)
            }
        }
    }
}

impl Loader {
    fn load_ibsp(file_path: PathBuf) -> Result<LoadedIbsp> {
        let ibsp = Ibsp::load(file_path)?;

        Ok(LoadedIbsp::new(
            ibsp.name,
            ibsp.version,
            ibsp.materials.into_iter().map(|m| m.get_name()).collect(),
            ibsp.entities.into_iter().map(|e| e.into()).collect(),
            ibsp.surfaces.into_iter().map(|s| s.into()).collect(),
        ))
    }

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
        for mat in lod0.materials {
            if xmodel.version != xmodel::XModelVersion::V14 as u16 {
                let loaded_material =
                    match Self::load_material(asset_path.clone(), mat, xmodel.version as i32) {
                        Ok(material) => material,
                        Err(error) => {
                            error_log!("{}", error);
                            continue;
                        }
                    };

                loaded_materials.push(loaded_material);
                continue;
            }

            loaded_materials.push(LoadedMaterial::new(mat, Vec::new(), xmodel.version as i32))
        }

        Ok(LoadedModel::new(
            xmodel.name,
            xmodel.version,
            [0f32; 3],
            [0f32; 3],
            [1f32; 3],
            loaded_materials,
            xmodelsurf.surfaces.into_iter().map(|s| s.into()).collect(),
            match xmodelpart {
                Some(xmodelpart) => xmodelpart.bones.into_iter().map(|b| b.into()).collect(),
                None => Vec::<LoadedBone>::new(),
            },
        ))
    }

    fn load_material(
        asset_path: PathBuf,
        material_name: String,
        version: i32,
    ) -> Result<LoadedMaterial> {
        let material_file_path = asset_path.join(material::ASSETPATH).join(&material_name);
        let material = Material::load(material_file_path, version)?;

        let mut loaded_textures: Vec<LoadedTexture> = Vec::new();
        for texture in material.textures {
            let mut texture_file_path = asset_path.join(iwi::ASSETPATH).join(&texture.name);
            texture_file_path.set_extension("iwi");
            let mut loaded_texture: LoadedTexture = match IWi::load(texture_file_path) {
                Ok(iwi) => iwi.into(),
                Err(error) => {
                    error_log!("{}", error);
                    continue;
                }
            };

            loaded_texture.set_name(texture.name);
            loaded_texture.set_texture_type(texture.texture_type);
            loaded_textures.push(loaded_texture);
        }

        Ok(LoadedMaterial::new(material_name, loaded_textures, version))
    }
}
