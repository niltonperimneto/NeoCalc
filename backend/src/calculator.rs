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
    /* Stores the history of calculations as a list of strings */
    history: Arc<Mutex<Vec<String>>>,
    /* Stores the current input value being typed or displayed */
    input_buffer: Arc<Mutex<String>>,
    /* Stores variables */
    variables: Arc<Mutex<engine::types::Context>>,
}

#[pymethods]
impl Calculator {
    #[new]
    fn new() -> Self {
        /* Initialize a new Calculator with empty history and "0" as input */
        Calculator {
            history: Arc::new(Mutex::new(Vec::new())),
            input_buffer: Arc::new(Mutex::new(String::from("0"))),
            variables: Arc::new(Mutex::new(std::collections::HashMap::new())),
        }
    }

    fn input(&self, text: String) -> PyResult<String> {
        /* Lock the buffer to safely modify it across threads */
        let mut buffer = lock_mutex(&self.input_buffer)?;

        /* If buffer is "0", replace it unless user enters decimal or paren */
        if *buffer == "0" && text != "." && text != ")" {
            *buffer = text;
        } else {
             /* Map special tokens like X to * and append */
             let mapped = utils::map_input_token(&text);
             buffer.push_str(mapped);

             /* If a function like sin( is added, ensure opening paren */
             if utils::should_auto_paren(mapped) {
                 buffer.push('(');
             }
        }
        /* Return the updated buffer */
        Ok(buffer.clone())
    }

    fn backspace(&self) -> PyResult<String> {
        let mut buffer = lock_mutex(&self.input_buffer)?;
        /* Remove the last character if buffer is not empty */
        if !buffer.is_empty() {
            buffer.pop();
            /* If buffer becomes empty, reset to "0" */
            if buffer.is_empty() {
                *buffer = "0".to_string();
            }
        }
        Ok(buffer.clone())
    }

    fn clear(&self) -> PyResult<String> {
        /* Reset the entire buffer to "0" */
        let mut buffer = lock_mutex(&self.input_buffer)?;
        *buffer = "0".to_string();
        Ok(buffer.clone())
    }

    fn get_buffer(&self) -> PyResult<String> {
        Ok(lock_mutex(&self.input_buffer)?.clone())
    }

    fn evaluate(&self, _expression: Option<String>) -> PyResult<String> {
        /* Determine whether to evaluate provided expression or current buffer */
        let expr_to_eval = if let Some(e) = _expression {
            e
        } else {
            lock_mutex(&self.input_buffer)?.clone()
        };

        /* Call the core engine to calculate result */
        let mut context = lock_mutex(&self.variables)?;
        let res = engine::evaluate(&expr_to_eval, &mut context);
        let output = match res {
            Ok(n) => utils::format_number(n),
            Err(_) => "Error".to_string(),
        };

        /* If valid result, save to history and update buffer */
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
             match lock_mutex(&self.input_buffer) {
                 Ok(g) => g.clone(),
                 Err(e) => return Err(e),
             }
        };

        let history = self.history.clone();
        let buffer_arc = self.input_buffer.clone();
        let variables_arc = self.variables.clone();

        let expr_for_task = buffer_val.clone();

        /* Run evaluation in a separate blocking thread to keep UI responsive */
        let _guard = crate::utils::RUNTIME.enter();
        future_into_py(py, async move {
            let output = crate::utils::RUNTIME.spawn_blocking(move || {
                let mut context = match variables_arc.lock() {
                     Ok(g) => g,
                     Err(_) => return "Error: Lock poisoned".to_string(),
                 };
                 
                let res = engine::evaluate(&expr_for_task, &mut context);
                match res {
                    Ok(n) => utils::format_number(n),
                    Err(_) => "Error".to_string(),
                }
            }).await.map_err(|e| PyRuntimeError::new_err(format!("Join error: {}", e)))?;

            /* Update state if successful */
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
        Ok(lock_mutex(&self.history)?.clone())
    }

    fn clear_history(&self) -> PyResult<()> {
        let mut h = lock_mutex(&self.history)?;
        h.clear();
        Ok(())
    }

    fn convert_to_hex(&self) -> PyResult<String> {
        let buffer = lock_mutex(&self.input_buffer)?;
        /* Try to parse the current buffer as an integer */
        /* Note: This is simple parsing; for robust behavior we might want to evaluate first if it's an expression */
        /* But for now let's assume the user hits 'Hex' after '=', so buffer is a number */
        
        /* If it's a raw number */
        if let Ok(val) = buffer.parse::<f64>() {
            let int_val = val as i64;
            return Ok(format!("0x{:X}", int_val));
        }

        /* If unsuccessful, just return buffer (maybe it's already hex or error) */
        Ok(buffer.clone())
    }

    fn convert_to_bin(&self) -> PyResult<String> {
        let buffer = lock_mutex(&self.input_buffer)?;
        if let Ok(val) = buffer.parse::<f64>() {
            let int_val = val as i64;
            return Ok(format!("0b{:b}", int_val));
        }
        Ok(buffer.clone())
    }

    fn preview(&self, expression: String) -> PyResult<String> {
        let mut context = lock_mutex(&self.variables)?;
        // Clone context to ensure preview doesn't modify actual state (if we had mutable ops)
        // Currently evaluate accepts &mut Context. Assignments modify it.
        // We WANT preview to NOT modify variables (e.g. previewing "x=5" shouldn't set x).
        // So we should clone the context.
        let mut context_clone = context.clone();
        
        let res = engine::evaluate(&expression, &mut context_clone);
        match res {
            Ok(n) => Ok(utils::format_number(n)),
            Err(_) => Ok("".to_string()), // Return empty for errors in preview
        }
    }

    fn get_variables(&self) -> PyResult<std::collections::HashMap<String, String>> {
        let context = lock_mutex(&self.variables)?;
        let mut result = std::collections::HashMap::new();
        for (k, v) in context.iter() {
            result.insert(k.clone(), utils::format_number(v.clone()));
        }
        Ok(result)
    }
}
