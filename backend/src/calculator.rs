use pyo3::prelude::*;
use pyo3_async_runtimes::tokio::future_into_py;
use std::sync::{Arc, Mutex};

use crate::engine;
use crate::engine::ast::Context;
use crate::engine::types::Number;
use crate::utils::{self, lock_mutex};

use crate::engine::errors::EngineError;

/// The interface between Python (Dynamic Bliss) and Rust (Static Pain).
#[pyclass]
#[derive(Clone, Default)]
#[allow(deprecated)] // Ignore deprecations during refactor if any
pub struct Calculator {
    /* Stores the history of calculations as a list of strings */
    history: Arc<Mutex<Vec<String>>>,
    /* Stores the current input value being typed or displayed */
    input_buffer: Arc<Mutex<String>>,
    /* Stores variables */
    variables: Arc<Mutex<Context>>,
}

impl Calculator {
    fn convert_base_internal(&self, radix: u32, prefix: &str) -> PyResult<String> {
        let buffer = lock_mutex(&self.input_buffer)?;
        let mut context = lock_mutex(&self.variables)?;

        let res = engine::evaluate(&buffer, &mut context);

        match res {
            Ok(num) => {
                let mut buffer = self.input_buffer.lock().unwrap();
                let result_str = match num {
                    Number::Integer(i) => {
                        let mut val_str = i.to_str_radix(radix);
                        if radix == 16 {
                            val_str = val_str.to_uppercase();
                        }
                        format!("{}{}", prefix, val_str)
                    }
                    Number::Float(f) => {
                        let int_val = f as i64;
                        let mut val_str = format!("{:b}", int_val);
                        if radix == 16 {
                            val_str = format!("{:X}", int_val);
                        }
                        format!("{}{}", prefix, val_str)
                    }
                    _ => "Error: Conversion not supported for this number type".to_string(),
                };
                *buffer = result_str.clone();
                Ok(result_str)
            }
            Err(e) => Ok(e.to_string()), // Convert EngineError to string for Python UI
        }
    }

    fn evaluate_internal(
        &self,
        expr_to_eval: &str,
        context: &mut Context,
    ) -> Result<Number, EngineError> {
        engine::evaluate(expr_to_eval, context)
    }
}

#[pymethods]
impl Calculator {
    #[new]
    fn new() -> Self {
        /* Initialize a new Calculator with empty history and "0" as input */
        Calculator {
            history: Arc::new(Mutex::new(Vec::new())),
            input_buffer: Arc::new(Mutex::new(String::from("0"))),
            variables: Arc::new(Mutex::new(Context::new())),
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
        let expr_to_eval = if let Some(e) = _expression {
            e
        } else {
            lock_mutex(&self.input_buffer)?.clone()
        };

        let mut context = lock_mutex(&self.variables)?;
        let res = self.evaluate_internal(&expr_to_eval, &mut context);

        let output = match &res {
            Ok(n) => utils::format_number(n.clone()),
            Err(e) => e.to_string(),
        };

        if res.is_ok() && !expr_to_eval.trim().is_empty() {
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

    fn evaluate_async<'py>(
        &self,
        py: Python<'py>,
        expression: Option<String>,
    ) -> PyResult<Bound<'py, PyAny>> {
        let buffer_val = if let Some(e) = expression {
            e
        } else {
            match lock_mutex(&self.input_buffer) {
                Ok(g) => g.clone(),
                Err(e) => return Err(e.into()),
            }
        };

        let self_clone = self.clone();
        let expr_for_task = buffer_val.clone();
        let history = self.history.clone();
        let input_buffer = self.input_buffer.clone();

        future_into_py(py, async move {
            let res = tokio::task::spawn_blocking(move || {
                let mut context = self_clone.variables.lock().unwrap();
                self_clone.evaluate_internal(&expr_for_task, &mut context)
            })
            .await
            .unwrap();

            let output = match &res {
                Ok(n) => utils::format_number(n.clone()),
                Err(e) => e.to_string(),
            };

            if res.is_ok() && !buffer_val.trim().is_empty() {
                if let Ok(mut h) = history.lock() {
                    h.push(format!("{} = {}", buffer_val, output));
                }
                if let Ok(mut b) = input_buffer.lock() {
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
        self.convert_base_internal(16, "0x")
    }

    fn convert_to_bin(&self) -> PyResult<String> {
        self.convert_base_internal(2, "0b")
    }

    fn preview(&self, expression: String) -> PyResult<String> {
        let context = lock_mutex(&self.variables)?;
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
        for scope in &context.scopes {
            for (k, v) in scope {
                result.insert(k.clone(), utils::format_number((**v).clone()));
            }
        }
        Ok(result)
    }
}

