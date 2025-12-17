use pyo3::prelude::*;
use pyo3::types::PyModule;
use pyo3::Bound;
use pyo3_async_runtimes::tokio;
use std::sync::{Arc, Mutex};

mod engine;

/// The interface between Python (Dynamic Bliss) and Rust (Static Pain).
#[pyclass]
#[derive(Default)]
struct Calculator {
    // I had to use Arc<Mutex<>> because the borrow checker kept yelling at me.
    // I just want to share a list, why is it so hard?
    history: Arc<Mutex<Vec<String>>>,
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
            Ok(v) => if v.fract() == 0.0 { (v as i64).to_string() } else { v.to_string() },
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
                Ok(v) => if v.fract() == 0.0 { (v as i64).to_string() } else { v.to_string() },
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
