use pyo3::prelude::*;
use pyo3::types::PyModule;
use pyo3::Bound;
use pyo3_async_runtimes::tokio;
use std::sync::{Arc, Mutex};

mod engine;

use num_complex::Complex64;

/// The interface between Python (Dynamic Bliss) and Rust (Static Pain).
#[pyclass]
#[derive(Default)]
struct Calculator {
    // I had to use Arc<Mutex<>> because the borrow checker kept yelling at me.
    // I just want to share a list, why is it so hard?
    history: Arc<Mutex<Vec<String>>>,
    input_buffer: Arc<Mutex<String>>,
}

fn format_complex(c: Complex64) -> String {
    let re = c.re;
    let im = c.im;
    let epsilon = 1e-10;

    if im.abs() < epsilon {
        if re.fract().abs() < epsilon { (re.round() as i64).to_string() } else { re.to_string() }
    } else {
        let re_str = if re.fract().abs() < epsilon { (re.round() as i64).to_string() } else { re.to_string() };
        let im_abs = im.abs();
        let im_str = if im_abs.fract().abs() < epsilon { (im_abs.round() as i64).to_string() } else { im_abs.to_string() };
        
        if re.abs() < epsilon {
             format!("{}i", if im < 0.0 { format!("-{}", im_str) } else { im_str })
        } else {
             format!("{} {} {}i", re_str, if im < 0.0 { "-" } else { "+" }, im_str)
        }
    }
}

#[pymethods]
impl Calculator {
    #[new]
    fn new() -> Self {
        Calculator {
            // Arc::new(Mutex::new(...)) - I feel like I'm casting a spell.
            history: Arc::new(Mutex::new(Vec::new())),
            input_buffer: Arc::new(Mutex::new(String::from("0"))),
        }
    }

    fn input(&self, text: String) -> String {
        let mut buffer = self.input_buffer.lock().unwrap();
        
        if *buffer == "0" && text != "." && text != ")" {
            *buffer = text;
        } else {
             // Basic mapping logic moved from Python
             let mapped = match text.as_str() {
                 "÷" => "/",
                 "×" => "*",
                 "−" => "-",
                 "π" => "pi",
                 "√" => "sqrt(", 
                 _ => text.as_str(),
             };
             
             buffer.push_str(mapped);
             
             // Simple heuristic for functions without needing explicit type info
             let funcs = ["sin", "cos", "tan", "asin", "acos", "atan", "sinh", "cosh", "tanh", "log", "ln", "sqrt", "abs"];
             if funcs.contains(&mapped) {
                 buffer.push('(');
             }
        }
        buffer.clone()
    }

    fn backspace(&self) -> String {
        let mut buffer = self.input_buffer.lock().unwrap();
        if buffer.len() > 0 {
            buffer.pop();
            if buffer.is_empty() {
                *buffer = "0".to_string();
            }
        }
        buffer.clone()
    }

    fn clear(&self) -> String {
        let mut buffer = self.input_buffer.lock().unwrap();
        *buffer = "0".to_string();
        buffer.clone()
    }

    fn get_buffer(&self) -> String {
        self.input_buffer.lock().unwrap().clone()
    }

    fn evaluate(&self, _expression: Option<String>) -> String {
        // If expression provided (legacy/compat), use it. 
        // Otherwise use buffer.
        let expr_to_eval = if let Some(e) = _expression {
            e
        } else {
            self.input_buffer.lock().unwrap().clone()
        };

        // Calling my 'engine'. It's just a file I copied from StackOverflow (kidding... mostly).
        let res = engine::evaluate(&expr_to_eval);
        let output = match res {
            Ok(c) => format_complex(c),
            Err(_) => "Error".to_string(), // Error handling is hard, let's just return a string.
        };

        if output != "Error" && !expr_to_eval.trim().is_empty() {
            // lock()? unwrap()? I hope this doesn't panic.
            if let Ok(mut h) = self.history.lock() {
                h.push(format!("{} = {}", expr_to_eval, output));
            }
            // Update buffer with result if we used internal buffer
            if let Ok(mut b) = self.input_buffer.lock() {
                *b = output.clone();
            }
        }
        output
    }

    fn evaluate_async<'py>(&self, py: Python<'py>, expression: Option<String>) -> PyResult<Bound<'py, PyAny>> {
        let buffer_val = if let Some(e) = expression {
            e
        } else {
            self.input_buffer.lock().unwrap().clone()
        };
        
        let history = self.history.clone();
        let buffer_arc = self.input_buffer.clone();

        tokio::future_into_py(py, async move {
            let res = engine::evaluate(&buffer_val);
            let output = match res {
                Ok(c) => format_complex(c),
                Err(_) => "Error".to_string(),
            };

            if output != "Error" && !buffer_val.trim().is_empty() {
                if let Ok(mut h) = history.lock() {
                     h.push(format!("{} = {}", buffer_val, output));
                }
                if let Ok(mut b) = buffer_arc.lock() {
                    *b = output.clone();
                }
            }
            Ok(output)
        })
    }

    fn get_history(&self) -> Vec<String> {
        self.history.lock().unwrap().clone()
    }
    
    fn clear_history(&self) {
        if let Ok(mut h) = self.history.lock() {
            h.clear();
        }
    }
}

mod managers;

#[pymodule]
pub fn neocalc_backend(m: &Bound<PyModule>) -> PyResult<()> {
    m.add_class::<Calculator>()?;
    m.add_class::<managers::DisplayManager>()?;
    m.add_class::<managers::CalculatorManager>()?;
    Ok(())
}
