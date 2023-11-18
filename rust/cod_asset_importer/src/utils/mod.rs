use std::result;

pub mod binary;
pub mod decode;
pub mod error;
pub mod log;
pub mod math;
pub mod path;

pub type Result<T> = result::Result<T, error::Error>;
