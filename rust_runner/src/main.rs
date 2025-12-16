use pyo3::prelude::*;
use pyo3::types::PyList;
use std::env;
use neocalc_backend::neocalc_backend;


fn main() -> PyResult<()> {
    // Add the current directory/src to python path so it can find 'gui.py'
    // We assume the binary is run from project root or we find 'src' relative to it.
    
    let current_dir = env::current_dir()?;
    let src_dir = current_dir.join("python_gui");

    // Register the rust backend module
    pyo3::append_to_inittab!(neocalc_backend);

    Python::with_gil(|py| {
        let sys = py.import("sys")?;
        let path: &PyList = sys.getattr("path")?.extract()?;
        path.insert(0, src_dir)?;
        
        // Also ensure the extension is available if it's not installed system-wide
        // (Usage of maturin develop installs it into the venv, so it should be fine if we use the same venv)

        let gui = py.import("app")?;
        gui.call_method0("main")?;
        
        Ok(())
    })
}
