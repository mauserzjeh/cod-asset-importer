use pyo3::exceptions::PyBaseException;
use std::{fmt, io, string};

#[derive(Debug)]
pub struct Error {
    pub error: String,
}

impl Error {
    pub fn new(e: String) -> Self {
        Self { error: e }
    }
}

impl From<io::Error> for Error {
    fn from(error: io::Error) -> Self {
        Error {
            error: error.to_string(),
        }
    }
}

impl From<string::FromUtf8Error> for Error {
    fn from(error: string::FromUtf8Error) -> Self {
        Error {
            error: error.to_string(),
        }
    }
}

impl From<serde_json::Error> for Error {
    fn from(error: serde_json::Error) -> Self {
        Error {
            error: error.to_string(),
        }
    }
}

impl From<Error> for pyo3::PyErr {
    fn from(error: Error) -> Self {
        PyBaseException::new_err(error.to_string())
    }
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.error)
    }
}
