use pyo3::prelude::*;
use pyo3::types::PyModule;
use pyo3::Bound;

mod engine;
mod managers;
mod utils;
mod calculator;

#[pymodule]
pub fn neocalc_backend(m: &Bound<PyModule>) -> PyResult<()> {
    m.add_class::<calculator::Calculator>()?;
    m.add_class::<managers::DisplayManager>()?;
    m.add_class::<managers::CalculatorManager>()?;
    Ok(())
}
