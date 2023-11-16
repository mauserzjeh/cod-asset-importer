use pyo3::prelude::*;
use valid_enum::ValidEnum;

pub mod ibsp;
pub mod iwi;
pub mod material;
pub mod xmodel;
pub mod xmodelpart;
pub mod xmodelsurf;

#[pyclass(module = "cod_asset_importer", name = "GAME_VERSIONS")]
#[derive(ValidEnum, Debug, Clone, Copy)]
#[valid_enum(u16)]
pub enum GameVersion {
    CoD1 = 1, // CoD1 & CoDUO
    CoD2 = 2, // CoD2
    CoD4 = 4, // CoD4
    CoD5 = 5, // CoD5
}
