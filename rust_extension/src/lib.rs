use pyo3::prelude::*;
use pyo3::types::PyModule;
use pyo3::Bound;
use pyo3::exceptions::PyRuntimeError;
use pyo3_async_runtimes::tokio::future_into_py;
use std::sync::{Arc, Mutex};

mod engine;

use num_complex::Complex64;

/// The interface between Python (Dynamic Bliss) and Rust (Static Pain).
#[pyclass]
#[derive(Default)]
struct Calculator {
    history: Arc<Mutex<Vec<String>>>,
    input_buffer: Arc<Mutex<String>>,
}

fn format_float(val: f64) -> String {
    let epsilon = 1e-10;
    if val.fract().abs() < epsilon {
        (val.round() as i64).to_string()
    } else {
        val.to_string()
    }
}

fn format_complex(c: Complex64) -> String {
    let re = c.re;
    let im = c.im;
    let epsilon = 1e-10;

    if im.abs() < epsilon {
        format_float(re)
    } else {
        let re_str = format_float(re);
        let im_abs = im.abs();
        let im_str = format_float(im_abs);
        
        if re.abs() < epsilon {
             if im < 0.0 { format!("-{}i", im_str) } else { format!("{}i", im_str) }
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
            history: Arc::new(Mutex::new(Vec::new())),
            input_buffer: Arc::new(Mutex::new(String::from("0"))),
        }
    }

    fn input(&self, text: String) -> PyResult<String> {
        let mut buffer = self.input_buffer.lock().map_err(|e| PyRuntimeError::new_err(format!("Lock poisoned: {}", e)))?;
        
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
        Ok(buffer.clone())
    }

    fn backspace(&self) -> PyResult<String> {
        let mut buffer = self.input_buffer.lock().map_err(|e| PyRuntimeError::new_err(format!("Lock poisoned: {}", e)))?;
        if buffer.len() > 0 {
            buffer.pop();
            if buffer.is_empty() {
                *buffer = "0".to_string();
            }
        }
        Ok(buffer.clone())
    }

    fn clear(&self) -> PyResult<String> {
        let mut buffer = self.input_buffer.lock().map_err(|e| PyRuntimeError::new_err(format!("Lock poisoned: {}", e)))?;
        *buffer = "0".to_string();
        Ok(buffer.clone())
    }

    fn get_buffer(&self) -> PyResult<String> {
        Ok(self.input_buffer.lock().map_err(|e| PyRuntimeError::new_err(format!("Lock poisoned: {}", e)))?.clone())
    }

    fn evaluate(&self, _expression: Option<String>) -> PyResult<String> {
        let expr_to_eval = if let Some(e) = _expression {
            e
        } else {
            self.input_buffer.lock().map_err(|e| PyRuntimeError::new_err(format!("Lock poisoned: {}", e)))?.clone()
        };

        let res = engine::evaluate(&expr_to_eval);
        let output = match res {
            Ok(c) => format_complex(c),
            Err(_) => "Error".to_string(),
        };

        if output != "Error" && !expr_to_eval.trim().is_empty() {
            if let Ok(mut h) = self.history.lock() {
                h.push(format!("{} = {}", expr_to_eval, output));
            }
            if let Ok(mut b) = self.input_buffer.lock() {
                *b = output.clone();
            }
        }
        Ok(output)
    }

    fn evaluate_async<'py>(&self, py: Python<'py>, expression: Option<String>) -> PyResult<Bound<'py, PyAny>> {
        let buffer_val = if let Some(e) = expression {
            e
        } else {
            self.input_buffer.lock().map_err(|e| PyRuntimeError::new_err(format!("Lock poisoned: {}", e)))?.clone()
        };
        
        let history = self.history.clone();
        let buffer_arc = self.input_buffer.clone();
        
        // Clone for the blocking task
        let expr_for_task = buffer_val.clone();

        future_into_py(py, async move {
            let output = tokio::task::spawn_blocking(move || {
                let res = engine::evaluate(&expr_for_task);
                match res {
                    Ok(c) => format_complex(c),
                    Err(_) => "Error".to_string(),
                }
            }).await.map_err(|e| PyRuntimeError::new_err(format!("Join error: {}", e)))?;

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

    fn get_history(&self) -> PyResult<Vec<String>> {
        Ok(self.history.lock().map_err(|e| PyRuntimeError::new_err(format!("Lock poisoned: {}", e)))?.clone())
    }
    
    fn clear_history(&self) -> PyResult<()> {
        let mut h = self.history.lock().map_err(|e| PyRuntimeError::new_err(format!("Lock poisoned: {}", e)))?;
        h.clear();
        Ok(())
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
