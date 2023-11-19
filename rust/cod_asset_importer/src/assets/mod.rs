use pyo3::prelude::*;
use valid_enum::ValidEnum;

pub mod ibsp;
pub mod iwi;
pub mod material;
pub mod xmodel;
pub mod xmodelpart;
pub mod xmodelsurf;

#[pyclass(module = "cod_asset_importer", name = "GAME_VERSION")]
#[derive(ValidEnum, Debug, Clone, Copy)]
#[valid_enum(u16)]
pub enum GameVersion {
    CoD, // CoD1 & CoDUO
    CoD2, // CoD2
    CoD4, // CoD4
    CoD5, // CoD5
    CoDBO1, // CoDBO1
}
