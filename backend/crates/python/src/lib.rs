use pyo3::prelude::*;
use pyo3::types::PyModule;
use pyo3::Bound;

mod calculator;
mod managers;
mod utils;

#[pymodule]
pub fn neocalc_backend(m: &Bound<PyModule>) -> PyResult<()> {
    m.add_class::<calculator::Calculator>()?;
    m.add_class::<managers::DisplayManager>()?;
    m.add_class::<managers::CalculatorManager>()?;
    Ok(())
}
