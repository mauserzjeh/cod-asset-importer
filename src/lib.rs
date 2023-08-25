pub mod assets;
pub mod utils;
pub mod loader;
pub mod loaded_assets;

use loaded_assets::{LoadedIbsp, LoadedIbspEntity, LoadedIbspSurface, LoadedModel, LoadedMaterial, LoadedTexture, LoadedSurface, LoadedVertex, LoadedWeight, LoadedBone};
use pyo3::prelude::*;

#[pymodule]
fn cod_asset_importer(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<LoadedIbsp>()?;
    m.add_class::<LoadedIbspEntity>()?;
    m.add_class::<LoadedIbspSurface>()?;
    m.add_class::<LoadedModel>()?;
    m.add_class::<LoadedMaterial>()?;
    m.add_class::<LoadedTexture>()?;
    m.add_class::<LoadedSurface>()?;
    m.add_class::<LoadedVertex>()?;
    m.add_class::<LoadedWeight>()?;
    m.add_class::<LoadedBone>()?;

    #[pyfn(m)]
    fn error_log(error: &str) {
        error_log!("{}", error);
    }

    #[pyfn(m)]
    fn info_log(info: &str) {
        info_log!("{}", info)
    }

    #[pyfn(m)]
    fn debug_log(debug: &str) {
        debug_log!("{}", debug)
    }

    Ok(())
}