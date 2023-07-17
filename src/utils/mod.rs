use std::result;

pub mod binary;
pub mod log;
pub mod error;

pub type Result<T> = result::Result<T, error::Error>;


