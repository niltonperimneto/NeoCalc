use pyo3::prelude::*;
use pyo3::exceptions::PyRuntimeError;
use pyo3_async_runtimes::tokio::future_into_py;
use std::sync::{Arc, Mutex};

use crate::engine;
use crate::utils::{self, lock_mutex};

/// The interface between Python (Dynamic Bliss) and Rust (Static Pain).
#[pyclass]
#[derive(Default)]
pub struct Calculator {
    history: Arc<Mutex<Vec<String>>>,
    input_buffer: Arc<Mutex<String>>,
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
        let mut buffer = lock_mutex(&self.input_buffer)?;
        
        if *buffer == "0" && text != "." && text != ")" {
            *buffer = text;
        } else {
             let mapped = utils::map_input_token(&text);
             buffer.push_str(mapped);
             
             if utils::should_auto_paren(mapped) {
                 buffer.push('(');
             }
        }
        Ok(buffer.clone())
    }

    fn backspace(&self) -> PyResult<String> {
        let mut buffer = lock_mutex(&self.input_buffer)?;
        if !buffer.is_empty() {
            buffer.pop();
            if buffer.is_empty() {
                *buffer = "0".to_string();
            }
        }
        Ok(buffer.clone())
    }

    fn clear(&self) -> PyResult<String> {
        let mut buffer = lock_mutex(&self.input_buffer)?;
        *buffer = "0".to_string();
        Ok(buffer.clone())
    }

    fn get_buffer(&self) -> PyResult<String> {
        Ok(lock_mutex(&self.input_buffer)?.clone())
    }

    fn evaluate(&self, _expression: Option<String>) -> PyResult<String> {
        let expr_to_eval = if let Some(e) = _expression {
            e
        } else {
            lock_mutex(&self.input_buffer)?.clone()
        };

        let res = engine::evaluate(&expr_to_eval);
        let output = match res {
            Ok(c) => utils::format_complex(c),
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

    fn set_expression(&self, expression: String) -> PyResult<()> {
        let mut buffer = lock_mutex(&self.input_buffer)?;
        *buffer = expression;
        Ok(())
    }

    fn evaluate_async<'py>(&self, py: Python<'py>, expression: Option<String>) -> PyResult<Bound<'py, PyAny>> {
        let buffer_val = if let Some(e) = expression {
            e
        } else {
            lock_mutex(&self.input_buffer)?.clone()
        };
        
        let history = self.history.clone();
        let buffer_arc = self.input_buffer.clone();
        
        // Clone for the blocking task
        let expr_for_task = buffer_val.clone();

        future_into_py(py, async move {
            let output = tokio::task::spawn_blocking(move || {
                let res = engine::evaluate(&expr_for_task);
                match res {
                    Ok(c) => utils::format_complex(c),
                    Err(_) => "Error".to_string(),
                }
            }).await.map_err(|e| PyRuntimeError::new_err(format!("Join error: {}", e)))?;

            if output != "Error" && !buffer_val.trim().is_empty() {
                // We use explicit matches or unwrap_or_else here to avoid extensive error handling inside async block
                // keeping it simple as these locks shouldn't be poisoned easily in this content
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
        Ok(lock_mutex(&self.history)?.clone())
    }
    
    fn clear_history(&self) -> PyResult<()> {
        let mut h = lock_mutex(&self.history)?;
        h.clear();
        Ok(())
    }
}
