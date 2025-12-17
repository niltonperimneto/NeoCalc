use pyo3::prelude::*;
use pyo3::types::PyList;
use std::env;
use neocalc_backend::neocalc_backend;

// Using 'current_thread' because GTK demands the main thread like a diva.
// Also, making this async because someone on Reddit said it's "Mockern".
#[tokio::main(flavor = "current_thread")]
async fn main() -> PyResult<()> {
    // 1. Inject the Rust backend module into Python.
    // I read in the docs that this is how you do it. 
    // It feels dirty, like global variables.
    pyo3::append_to_inittab!(neocalc_backend);

    // 2. Initialize Python. 
    // The compiler yelled at me about 'with_gil', so now we 'attach'. 
    // It sounds clingy, but I don't make the rules.
    // We are blocking the async runtime here. Don't tell Tokio.
    Python::attach(|py| {
        let sys = py.import("sys")?;
        // getattr("path")?.extract()?; -> The '?' operator is carrying this entire codebase.
        let path: Bound<PyList> = sys.getattr("path")?.extract()?;

        // 3. Find 'python_gui' directory.
        // We look in current directory and parents to support running from 'target/debug'
        let exe_path = env::current_exe()?;
        let exe_dir = exe_path.parent().ok_or_else(|| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>("Failed to get exe directory"))?;
        
        let mut gui_dir = exe_dir.join("python_gui");
        let mut found = false;
        
        // Search up to 3 levels up
        let mut current_search = exe_dir.to_path_buf();
        for _ in 0..3 {
            let candidate = current_search.join("python_gui");
            if candidate.exists() {
                gui_dir = candidate;
                found = true;
                break;
            }
            if let Some(parent) = current_search.parent() {
                current_search = parent.to_path_buf();
            } else {
                break;
            }
        }

        if !found {
            eprintln!("WARNING: Could not find 'python_gui' directory. Defaulting to: {:?}", gui_dir);
        } else {
            eprintln!("Found python_gui at: {:?}", gui_dir);
        }

        let app_path = gui_dir.join("app.py");
        let file_exists = app_path.exists();

        // Add BOTH the gui directory and the root directory to be safe
        path.insert(0, gui_dir.clone())?;

        // 4. Import the application module.
        // We catch the error to add the computed path to the message for debugging.
        let app_module = py.import("app").map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyImportError, _>(
                format!("Failed to import 'app'. \nCheck: {} -> Exists? {} \nComputed Path: {:?} \nsys.path: {:?} \nOriginal Error: {}", 
                    app_path.display(), file_exists, gui_dir, path, e)
            )
        })?;
        
        // 5. Run the main function.
        // call_method0? Zero arguments? What if I want arguments?
        // Too late, clicking run.
        app_module.call_method0("main")?;

        Ok(())
    })
}
