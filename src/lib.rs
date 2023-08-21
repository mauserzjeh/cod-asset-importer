pub mod assets;
pub mod utils;
pub mod loader;
pub mod loaded_assets;

use pyo3::prelude::*;

#[pymodule]
fn cod_asset_importer(_py: Python, m: &PyModule) -> PyResult<()> {
    Ok(())
}