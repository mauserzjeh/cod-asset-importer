#[macro_export]
macro_rules! error_log {
    ($($arg:tt)*) => {
        {
            let error_message = format!("[ERROR] {}", format_args!($($arg)*));
            println!("{}", error_message);
        }
    };
}

#[macro_export]
macro_rules! info_log {
    ($($arg:tt)*) => {
        {
            let error_message = format!("[INFO] {}", format_args!($($arg)*));
            println!("{}", error_message);
        }
    };
}

#[macro_export]
macro_rules! debug_log {
    ($($arg:tt)*) => {
        {
            let error_message = format!("[DEBUG] {}", format_args!($($arg)*));
            println!("{}", error_message);
        }
    };
}

