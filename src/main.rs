use cod_asset_importer::assets::ibsp::Ibsp;
use cod_asset_importer::{error_log, info_log};
use std::path;
use std::time;

fn main() {
    let file_path = path::PathBuf::from(
        "E:\\MOVIEMAKING\\CALL OF DUTY\\3D STUFF\\CODASSETS\\COD2ASSETS\\maps\\toujane_ride.d3dbsp",
    );
    let start = time::Instant::now();
    let res = Ibsp::load(file_path);
    let duration = start.elapsed();
    match res {
        Ok(ibsp) => {
            info_log!("name: {}", ibsp.name);
            info_log!("materials_len: {}", ibsp.materials.len());
            info_log!("entities_len: {}", ibsp.entities.len());
            info_log!("surfaces_len: {}", ibsp.surfaces.len());
        }
        Err(error) => {
            error_log!("{}", error)
        }
    }

    info_log!("duration {:?}", duration)
}
