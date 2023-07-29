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
    let test_type = Test::XModel;
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

    let test_data = [
        "E:\\MOVIEMAKING\\CALL OF DUTY\\3D STUFF\\CODASSETS\\COD2ASSETS\\maps\\toujane_ride.d3dbsp",
        "E:\\MOVIEMAKING\\CALL OF DUTY\\3D STUFF\\CODASSETS\\COD1ASSETS\\maps\\ponyri.bsp",
    ];

    let test_data_idx: usize = 1;

    let file_path = path::PathBuf::from(test_data[test_data_idx]);
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

    let test_data :Vec<(&str, &str, &str)> = vec![
        (
            "E:\\MOVIEMAKING\\CALL OF DUTY\\3D STUFF\\CODASSETS\\COD1ASSETS\\xmodel\\character_airborne_winter_medic",
            "E:\\MOVIEMAKING\\CALL OF DUTY\\3D STUFF\\CODASSETS\\COD1ASSETS\\xmodelparts\\USAirborne1",
            "E:\\MOVIEMAKING\\CALL OF DUTY\\3D STUFF\\CODASSETS\\COD1ASSETS\\xmodelsurfs\\USAirborne1",
        ),
        (
            "E:\\MOVIEMAKING\\CALL OF DUTY\\3D STUFF\\CODASSETS\\COD2ASSETS\\xmodel\\character_german_normandy_coat_dark",
            "E:\\MOVIEMAKING\\CALL OF DUTY\\3D STUFF\\CODASSETS\\COD2ASSETS\\xmodelparts\\character_german_normandy_coat_dark_4k1",
            "E:\\MOVIEMAKING\\CALL OF DUTY\\3D STUFF\\CODASSETS\\COD2ASSETS\\xmodelsurfs\\character_german_normandy_coat_dark_4k1",
        ),
        (
            "E:\\MOVIEMAKING\\CALL OF DUTY\\3D STUFF\\CODASSETS\\COD4ASSETS\\xmodel\\body_mp_arab_regular_sniper",
            "E:\\MOVIEMAKING\\CALL OF DUTY\\3D STUFF\\CODASSETS\\COD4ASSETS\\xmodelparts\\body_sp_arab_regular_sadiq_lod02",
            "E:\\MOVIEMAKING\\CALL OF DUTY\\3D STUFF\\CODASSETS\\COD4ASSETS\\xmodelsurfs\\body_sp_arab_regular_sadiq_lod02",
        )
    ];

    let test_data_idx: usize = 2;

    let file_path = path::PathBuf::from(test_data[test_data_idx].0);
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

    let file_path = path::PathBuf::from(test_data[test_data_idx].1);
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
            let file_path = path::PathBuf::from(test_data[test_data_idx].2);
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

    let test_data = [
        "E:\\MOVIEMAKING\\CALL OF DUTY\\3D STUFF\\CODASSETS\\COD2ASSETS\\images\\german_winter_color.iwi",
        "E:\\MOVIEMAKING\\CALL OF DUTY\\3D STUFF\\CODASSETS\\COD2ASSETS\\images\\~caen_grass_normal_01-gggr.iwi",
        "E:\\MOVIEMAKING\\CALL OF DUTY\\3D STUFF\\CODASSETS\\COD2ASSETS\\images\\caen_asphalt_dirt_02.iwi",
        
        "E:\\MOVIEMAKING\\CALL OF DUTY\\3D STUFF\\CODASSETS\\COD4ASSETS\\images\\cobra_pilot_woodland_body_sp_nml.iwi",
        "E:\\MOVIEMAKING\\CALL OF DUTY\\3D STUFF\\CODASSETS\\COD4ASSETS\\images\\m14_col.iwi",
        "E:\\MOVIEMAKING\\CALL OF DUTY\\3D STUFF\\CODASSETS\\COD4ASSETS\\images\\usmc_james_sp_col.iwi",
    ];

    let test_data_idx: usize = 5;

    let file_path = path::PathBuf::from(test_data[test_data_idx]);
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

    let test_data:Vec<(&str, i32)> = vec![
     ("E:\\MOVIEMAKING\\CALL OF DUTY\\3D STUFF\\CODASSETS\\COD2ASSETS\\materials\\mtl_german_nrmndy_chrcters_body", 20),
     ("E:\\MOVIEMAKING\\CALL OF DUTY\\3D STUFF\\CODASSETS\\COD4ASSETS\\materials\\mtl_sas_woodland_body_sp", 25)
    ];

    let test_data_idx: usize = 0;

    let file_path = path::PathBuf::from(test_data[test_data_idx].0);
    let start = time::Instant::now();
    let res = Material::load(file_path, test_data[test_data_idx].1);
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
