use std::sync::{Mutex, MutexGuard};
use pyo3::prelude::*;
use pyo3::exceptions::PyRuntimeError;
use num_complex::Complex64;

pub const EPSILON: f64 = 1e-10;

/// Helper to lock a mutex and map poison errors to PyRuntimeError
pub fn lock_mutex<T>(mutex: &Mutex<T>) -> PyResult<MutexGuard<'_, T>> {
    mutex.lock().map_err(|e| PyRuntimeError::new_err(format!("Lock poisoned: {}", e)))
}

pub fn format_float(val: f64) -> String {
    if val.fract().abs() < EPSILON {
        (val.round() as i64).to_string()
    } else {
        val.to_string()
    }
}

pub fn format_complex(c: Complex64) -> String {
    let re = c.re;
    let im = c.im;

    if im.abs() < EPSILON {
        format_float(re)
    } else {
        let re_str = format_float(re);
        let im_abs = im.abs();
        let im_str = format_float(im_abs);
        
        if re.abs() < EPSILON {
             if im < 0.0 { format!("-{}i", im_str) } else { format!("{}i", im_str) }
        } else {
             format!("{} {} {}i", re_str, if im < 0.0 { "-" } else { "+" }, im_str)
        }
    }
}

pub fn map_input_token(text: &str) -> &str {
    match text {
        "÷" => "/",
        "×" => "*",
        "−" => "-",
        "π" => "pi",
        "√" => "sqrt(", 
        _ => text,
    }
}

pub fn should_auto_paren(token: &str) -> bool {
    matches!(token, "sin" | "cos" | "tan" | "asin" | "acos" | "atan" | "sinh" | "cosh" | "tanh" | "log" | "ln" | "sqrt" | "abs")
}
