use std::path::PathBuf;

pub fn file_name_without_ext(file_path: PathBuf) -> String {
    let name = file_path
        .file_stem()
        .unwrap_or_default()
        .to_str()
        .unwrap_or_default()
        .to_string();
    name
}
