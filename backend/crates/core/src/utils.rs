use crate::Number;

pub fn format_number(_n: Number) -> String {
    "0".to_string()
}

pub fn map_input_token(t: &str) -> String {
    t.to_string()
}

pub fn should_auto_paren(_t: String) -> bool {
    false
}
