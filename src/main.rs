use cod_asset_importer::assets::ibsp::Ibsp;
use cod_asset_importer::{error_log, info_log};


fn main() {
    let file_path = "E:\\MOVIEMAKING\\CALL OF DUTY\\3D STUFF\\CODASSETS\\COD2ASSETS\\maps\\mp\\mp_toujane.d3dbsp".to_string();
    let res = Ibsp::load(file_path);
    match res {
        Ok(ibsp) => {
            info_log!("name: {}", ibsp.name);
            info_log!("materials_len: {}", ibsp.materials.len());
            info_log!("entities_len: {}", ibsp.entities.len());
            info_log!("surfaces_len: {}", ibsp.surfaces.len());
        },
        Err(error) => {
            error_log!("{}", error)
        }
    }
}
