use pyo3::prelude::*;
use pyo3::exceptions::PyRuntimeError;
use std::sync::{Mutex, MutexGuard};

/// Helper to lock a mutex and map poison errors to PyRuntimeError
pub fn lock_mutex<T>(mutex: &Mutex<T>) -> PyResult<MutexGuard<'_, T>> {
    mutex
        .lock()
        .map_err(|e| PyRuntimeError::new_err(format!("Lock poisoned: {}", e)))
}
