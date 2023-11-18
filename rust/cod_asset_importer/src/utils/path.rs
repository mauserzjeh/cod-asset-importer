use std::path::PathBuf;

pub fn file_name_without_ext(file_path: PathBuf) -> String {
    file_path
        .file_stem()
        .unwrap_or_default()
        .to_str()
        .unwrap_or_default()
        .to_string()
}

pub fn file_name(file_path: PathBuf) -> String {
    file_path
        .file_name()
        .unwrap_or_default()
        .to_str()
        .unwrap_or_default()
        .to_string()
}
