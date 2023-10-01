#[macro_export]
macro_rules! error_log {
    ($($arg:tt)*) => {
        {
            let error_message = format!("[ERROR] {}:{} - {}", file!(), line!(), format_args!($($arg)*));
            println!("{}", error_message);
        }
    };
}

#[macro_export]
macro_rules! info_log {
    ($($arg:tt)*) => {
        {
            let info_message = format!("[INFO] {}:{} - {}", file!(), line!(), format_args!($($arg)*));
            println!("{}", info_message);
        }
    };
}

#[macro_export]
macro_rules! debug_log {
    ($($arg:tt)*) => {
        {
            let debug_message = format!("[DEBUG] {}:{} - {}", file!(), line!(), format_args!($($arg)*));
            println!("{}", debug_message);
        }
    };
}

