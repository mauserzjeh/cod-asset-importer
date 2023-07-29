use cod_asset_importer::assets::{
    ibsp::Ibsp, iwi::IWi, material::Material, xmodel::XModel, xmodelpart::XModelPart,
    xmodelsurf::XModelSurf,
};
use cod_asset_importer::{error_log, info_log};
use std::path;
use std::time;

enum Test {
    Ibsp,
    XModel,
    IWi,
    Material,
}

fn main() {
    // let test_type = Test::Ibsp;
    let test_type = Test::XModel; // TODO fix xmodelsurf -> index out of range
    // let test_type = Test::IWi;
    // let test_type = Test::Material;
    match test_type {
        Test::Ibsp => ibsp_test(),
        Test::XModel => xmodel_test(),
        Test::IWi => iwi_test(),
        Test::Material => material_test(),
    }
}

fn ibsp_test() {
    info_log!("ibsp test");

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

fn xmodel_test() {
    info_log!("xmodel test");

    let file_path = path::PathBuf::from(
        "E:\\MOVIEMAKING\\CALL OF DUTY\\3D STUFF\\CODASSETS\\COD2ASSETS\\xmodel\\character_german_normandy_coat_dark",
    );
    let start = time::Instant::now();
    let xmodel_res = XModel::load(file_path);
    let duration = start.elapsed();
    match xmodel_res {
        Ok(xmodel) => {
            info_log!("name: {}", xmodel.name);
            info_log!("version: {}", xmodel.version);
            if xmodel.lods.len() > 0 {
                info_log!("lod0: {:?}", xmodel.lods[0])
            }
        }
        Err(error) => {
            error_log!("{}", error)
        }
    }
    info_log!("xmodel duration {:?}", duration);

    // -----------------------------------------------------------------------------

    info_log!("xmodelpart test");

    let file_path = path::PathBuf::from(
        "E:\\MOVIEMAKING\\CALL OF DUTY\\3D STUFF\\CODASSETS\\COD2ASSETS\\xmodelparts\\body_german_winter_jon_8k1",
    );
    let start = time::Instant::now();
    let xmodelpart_res = XModelPart::load(file_path);
    let duration = start.elapsed();
    match xmodelpart_res {
        Ok(ref xmodelpart) => {
            info_log!("name: {}", xmodelpart.name);
            info_log!("version: {}", xmodelpart.version);
            info_log!("bones_len: {}", xmodelpart.bones.len());
            info_log!("bones[0]: {}", xmodelpart.bones[0].name)
        }
        Err(ref error) => {
            error_log!("{}", error)
        }
    }

    info_log!("xmodelpart duration {:?}", duration);

    // -----------------------------------------------------------------------------

    match xmodelpart_res {
        Ok(_) => {
            info_log!("xmodelsurf test");
            let file_path = path::PathBuf::from(
                "E:\\MOVIEMAKING\\CALL OF DUTY\\3D STUFF\\CODASSETS\\COD2ASSETS\\xmodelsurfs\\body_german_winter_jon_8k1",
            );
            let start = time::Instant::now();
            let xmodelsurf_res = XModelSurf::load(file_path, Some(xmodelpart_res.unwrap()));
            let duration = start.elapsed();
            match xmodelsurf_res {
                Ok(xmodelsurf) => {
                    info_log!("name: {}", xmodelsurf.name);
                    info_log!("surfaces_len: {}", xmodelsurf.surfaces.len());
                }
                Err(error) => {
                    error_log!("{}", error)
                }
            }
            info_log!("xmodelsurf duration {:?}", duration);
        }
        Err(error) => {
            error_log!("{}", error)
        }
    }
}

fn iwi_test() {
    info_log!("iwi test");

    let file_path = path::PathBuf::from(
        "E:\\MOVIEMAKING\\CALL OF DUTY\\3D STUFF\\CODASSETS\\COD2ASSETS\\images\\german_winter_color.iwi",
    );
    let start = time::Instant::now();
    let res = IWi::load(file_path);
    let duration = start.elapsed();
    match res {
        Ok(iwi) => {
            info_log!("width: {}", iwi.width);
            info_log!("height: {}", iwi.height);
            info_log!("data_len: {}", iwi.data.len());
        }
        Err(error) => {
            error_log!("{}", error)
        }
    }
    info_log!("duration {:?}", duration)
}

fn material_test() {
    info_log!("material test");

    let file_path = path::PathBuf::from(
        "E:\\MOVIEMAKING\\CALL OF DUTY\\3D STUFF\\CODASSETS\\COD2ASSETS\\materials\\mtl_german_nrmndy_chrcters_body",
    );
    let start = time::Instant::now();
    let res = Material::load(file_path, 20);
    let duration = start.elapsed();
    match res {
        Ok(material) => {
            info_log!("name: {}", material.name);
            info_log!("textures: {:?}", material.textures);
        }
        Err(error) => {
            error_log!("{}", error)
        }
    }
    info_log!("duration {:?}", duration)
}
