use cod_asset_importer::assets::ibsp::Ibsp;
use cod_asset_importer::{error_log, info_log};


fn main() {
    let file_path = "E:\\MOVIEMAKING\\CALL OF DUTY\\3D STUFF\\CODASSETS\\COD2ASSETS\\maps\\mp\\mp_toujane.d3dbsp".to_string();
    let res = Ibsp::load(file_path);
    match res {
        Ok(ibsp) => {
            info_log!("{}", ibsp.name);
        },
        Err(error) => {
            error_log!("{}", error)
        }
    }
}
