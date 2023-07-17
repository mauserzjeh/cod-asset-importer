use std::{io, fmt};


pub struct Error {
    pub error: String
}

impl Error {
    pub fn new(e: String) -> Self {
        Self { error: e }
    }
}

impl From<io::Error> for Error {
    fn from(error: io::Error) -> Self {
        Error { error:error.to_string() }
    }
}

impl fmt::Display for Error {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.error)
    }
}