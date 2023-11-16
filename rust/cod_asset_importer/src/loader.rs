use crate::{
    assets::{
        ibsp::{Ibsp, IbspVersion},
        iwi::{self, IWi},
        material::{self, Material},
        xmodel::{self, XModel, XModelVersion},
        xmodelpart::{self, XModelPart},
        xmodelsurf::{self, XModelSurf},
        GameVersion,
    },
    error_log, info_log,
    loaded_assets::{LoadedBone, LoadedIbsp, LoadedMaterial, LoadedModel, LoadedTexture},
    utils::{error::Error, Result},
};
use crossbeam_utils::sync::WaitGroup;
use pyo3::{exceptions::PyBaseException, prelude::*};
use rayon::ThreadPoolBuilder;
use std::{
    collections::HashMap,
    path::PathBuf,
    sync::{mpsc::channel, Arc, Mutex},
    thread,
    time::{Duration, Instant},
};

#[pyclass(module = "cod_asset_importer")]
pub struct Loader {
    importer: PyObject,
    threads: usize,
}

#[pymethods]
impl Loader {
    #[new]
    #[pyo3(signature = (importer))]
    fn new(importer: PyObject) -> Self {
        // use half the threads that is available on the system, fallback value 1
        let threads = thread::available_parallelism()
            .map(|p| p.get().checked_div(2).unwrap_or(1))
            .unwrap_or(1);

        info_log!("[AVAILABLE THREADS] {}", threads);
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

        let mut version = XModelVersion::V14;
        let mut game_version = GameVersion::CoD1;
        if loaded_ibsp.version == IbspVersion::V4 as i32 {
            version = XModelVersion::V20;
            game_version = GameVersion::CoD2
        }

        for material in materials {
            let material_name = material.clone();
            let start_material = Instant::now();
            let loaded_material = if loaded_ibsp.version == IbspVersion::V59 as i32 {
                Ok(LoadedMaterial::new(material, Vec::new(), version))
            } else {
                Self::load_material(PathBuf::from(asset_path), material, version)
            };

            match loaded_material {
                Ok(loaded_material) => {
                    match importer_ref.call_method1("material", (loaded_material, false)) {
                        Ok(_) => {
                            info_log!(
                                "[MATERIAL] {} [{:?}]",
                                material_name,
                                start_material.elapsed()
                            );
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
        }

        match importer_ref.call_method1("ibsp", (loaded_ibsp,)) {
            Ok(_) => (),
            Err(error) => {
                error_log!("{}", error)
            }
        }

        let model_cache = ModelCache::new();
        let (sender, receiver) = channel::<(LoadedModel, Duration)>();
        let pool = ThreadPoolBuilder::new()
            .num_threads(self.threads)
            .build()
            .unwrap();

        for entity in entities {
            let mut cache = model_cache.clone();
            let sender_clone = sender.clone();
            let entity_name = entity.name.clone();
            let entity_asset_path = PathBuf::from(asset_path);
            let entity_path = PathBuf::from(asset_path)
                .join(xmodel::ASSETPATH)
                .join(entity.name);
            let game_version = game_version.clone();

            pool.spawn(move || {
                let load_start = Instant::now();
                let mut loaded_model = match Self::load_xmodel_cached(
                    entity_asset_path.clone(),
                    entity_path,
                    entity_name,
                    game_version,
                    &mut cache,
                ) {
                    Ok(loaded_model) => loaded_model,
                    Err(error) => {
                        error_log!("{}", error);
                        return;
                    }
                };

                loaded_model.set_angles(entity.angles);
                loaded_model.set_origin(entity.origin);
                loaded_model.set_scale(entity.scale);

                let load_duration = load_start.elapsed();
                sender_clone.send((loaded_model, load_duration)).unwrap();
            });
        }

        drop(sender);

        for r in receiver {
            let import_start = Instant::now();
            let loaded_model = r.0;
            let load_duration = r.1;
            let model_name = loaded_model.name.clone();
            match importer_ref.call_method1("xmodel", (loaded_model,)) {
                Ok(_) => {
                    let model_duration = load_duration + import_start.elapsed();
                    info_log!("[MODEL] {} [{:?}]", model_name, model_duration);
                }
                Err(error) => {
                    error_log!("{}", error);
                }
            }
        }

        info_log!("[MAP] {} [{:?}]", ibsp_name, start.elapsed());
        Ok(())
    }

    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (asset_path, file_path, selected_version, angles, origin, scale))]
    fn import_xmodel(
        &self,
        py: Python,
        asset_path: &str,
        file_path: &str,
        selected_version: GameVersion,
        angles: [f32; 3],
        origin: [f32; 3],
        scale: [f32; 3],
    ) -> PyResult<()> {
        let start = Instant::now();

        let importer_ref = self.importer.as_ref(py);

        let mut loaded_model = match Self::load_xmodel(
            PathBuf::from(asset_path),
            PathBuf::from(file_path),
            selected_version,
        ) {
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
                info_log!("[MODEL] {} [{:?}]", model_name, start.elapsed());
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
        Ok(ibsp.into())
    }

    fn load_xmodel(
        asset_path: PathBuf,
        file_path: PathBuf,
        selected_version: GameVersion,
    ) -> Result<LoadedModel> {
        let xmodel = XModel::load(file_path, selected_version)?;
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
            match xmodel.version {
                XModelVersion::V14 => {
                    loaded_materials.push(LoadedMaterial::new(mat, Vec::new(), xmodel.version))
                }
                _ => {
                    let loaded_material =
                        match Self::load_material(asset_path.clone(), mat, xmodel.version) {
                            Ok(material) => material,
                            Err(error) => {
                                error_log!("{}", error);
                                continue;
                            }
                        };

                    loaded_materials.push(loaded_material);
                }
            }
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

    fn load_xmodel_cached(
        asset_path: PathBuf,
        file_path: PathBuf,
        model_name: String,
        selected_version: GameVersion,
        cache: &mut ModelCache,
    ) -> Result<LoadedModel> {
        match cache.get_model(&model_name) {
            Some(cached_model) => match cached_model {
                CachedModel::Cached(model) => Ok(model),
                CachedModel::Loading(wg) => {
                    wg.wait();

                    let cached_model = cache.get_model(&model_name).unwrap();
                    let CachedModel::Cached(model) = cached_model else {
                        panic!("model {} still not cached\n", model_name);
                    };

                    Ok(model.clone())
                }
            },
            None => {
                let wg = WaitGroup::new();
                cache.set_model(&model_name, CachedModel::Loading(wg.clone()));

                let loaded_model = match Self::load_xmodel(asset_path, file_path, selected_version)
                {
                    Ok(loaded_model) => loaded_model,
                    Err(error) => {
                        error_log!("{}", error);
                        return Err(Error::new(error.to_string()));
                    }
                };

                cache.set_model(&model_name, CachedModel::Cached(loaded_model.clone()));
                drop(wg);
                Ok(loaded_model.clone())
            }
        }
    }

    fn load_material(
        asset_path: PathBuf,
        material_name: String,
        version: XModelVersion,
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

#[derive(Clone)]
enum CachedModel {
    Loading(WaitGroup),
    Cached(LoadedModel),
}
#[derive(Clone)]
struct ModelCache {
    loaded_models: Arc<Mutex<HashMap<String, CachedModel>>>,
}

impl ModelCache {
    fn new() -> Self {
        ModelCache {
            loaded_models: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    fn set_model(&mut self, model_name: &str, cached_model: CachedModel) {
        let mut loaded_models = self.loaded_models.lock().unwrap();
        loaded_models.insert(String::from(model_name), cached_model);
    }

    fn get_model(&self, loaded_model_name: &str) -> Option<CachedModel> {
        let loaded_models = self.loaded_models.lock().unwrap();
        loaded_models.get(loaded_model_name).cloned()
    }
}
