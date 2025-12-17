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
        }
    }

    fn evaluate(&self, expression: String) -> String {
        // Calling my 'engine'. It's just a file I copied from StackOverflow (kidding... mostly).
        let res = engine::evaluate(&expression);
        let output = match res {
            Ok(c) => format_complex(c),
            Err(_) => "Error".to_string(), // Error handling is hard, let's just return a string.
        };

        if output != "Error" && !expression.trim().is_empty() {
            // lock()? unwrap()? I hope this doesn't panic.
            if let Ok(mut h) = self.history.lock() {
                h.push(format!("{} = {}", expression, output));
            }
        }
        output
    }

    fn evaluate_async<'py>(&self, py: Python<'py>, expression: String) -> PyResult<Bound<'py, PyAny>> {
        let history = self.history.clone();
        tokio::future_into_py(py, async move {
            let res = engine::evaluate(&expression);
            let output = match res {
                Ok(c) => format_complex(c),
                Err(_) => "Error".to_string(),
            };

            if output != "Error" && !expression.trim().is_empty() {
                if let Ok(mut h) = history.lock() {
                    h.push(format!("{} = {}", expression, output));
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

#[pymodule]
pub fn neocalc_backend(m: &Bound<PyModule>) -> PyResult<()> {
    m.add_class::<Calculator>()?;
    Ok(())
}
