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

        // 3. Add 'python_gui' directory to sys.path.
        let current_dir = env::current_dir()?;
        let search_paths = vec![
            current_dir.join("python_gui"),
            current_dir.parent().unwrap_or(&current_dir).join("python_gui"),
            current_dir.parent().unwrap_or(&current_dir).parent().unwrap_or(&current_dir).join("python_gui"),
        ];
        
        let mut found_path = None;
        for path in search_paths {
            if path.exists() {
                found_path = Some(path);
                break;
            }
        }
        
        if let Some(gui_path) = found_path {
            path.insert(0, gui_path)?;
        } else {
             eprintln!("Could not find python_gui directory!");
             path.insert(0, "python_gui")?;
        }

        // 4. Import the application module.
        // If this works, it's a miracle.
        let app_module = py.import("app")?;
        
        // 5. Run the main function.
        // call_method0? Zero arguments? What if I want arguments?
        // Too late, clicking run.
        app_module.call_method0("main")?;

        Ok(())
    })
}
