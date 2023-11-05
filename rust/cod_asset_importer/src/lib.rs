mod assets;
mod loaded_assets;
mod loader;
mod utils;

use assets::xmodel::XModelVersion;
use loaded_assets::{
    LoadedBone, LoadedIbsp, LoadedIbspEntity, LoadedMaterial, LoadedModel, LoadedSurface,
    LoadedTexture,
};
use loader::Loader;
use pyo3::prelude::*;

#[pymodule]
fn cod_asset_importer(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Loader>()?;
    m.add_class::<LoadedIbsp>()?;
    m.add_class::<LoadedIbspEntity>()?;
    m.add_class::<LoadedModel>()?;
    m.add_class::<LoadedMaterial>()?;
    m.add_class::<LoadedTexture>()?;
    m.add_class::<LoadedSurface>()?;
    m.add_class::<LoadedBone>()?;
    m.add_class::<XModelVersion>()?;

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
