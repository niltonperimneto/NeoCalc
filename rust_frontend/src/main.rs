use pyo3::prelude::*;
use pyo3::types::PyList;
use std::env;
use std::path::PathBuf;
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
        let sys_path: Bound<PyList> = sys.getattr("path")?.extract()?;

        // 3. Find the 'python_gui' directory. 
        // We are going on a treasure hunt.
        let mut found_path: Option<PathBuf> = None;
        
        // Strategy A: Look relative to the executable (wherever we deployed this mess)
        if let Ok(exe_path) = env::current_exe() {
             if let Some(exe_dir) = exe_path.parent() {
                 let candidate = exe_dir.join("python_gui");
                 if candidate.exists() {
                     found_path = Some(candidate);
                 } else {
                     // Maybe we are in a nested build dir? Up we go!
                     // Search up to 3 levels up because cargo directories are a maze.
                     let mut current_search = exe_dir.to_path_buf();
                     for _ in 0..3 {
                        if let Some(parent) = current_search.parent() {
                            let candidate = parent.join("python_gui");
                            if candidate.exists() {
                                found_path = Some(candidate);
                                break;
                            }
                            current_search = parent.to_path_buf();
                        } else {
                            break;
                        }
                     }
                 }
             }
        }

        // Strategy B: Look relative to where ever the user clicked run (CWD)
        // This is the fallback plan if Strategy A fails like my last startup.
        if found_path.is_none() {
             if let Ok(cwd) = env::current_dir() {
                 let candidate = cwd.join("python_gui");
                 if candidate.exists() {
                     found_path = Some(candidate);
                 }
             }
        }

        let gui_dir = found_path.ok_or_else(|| {
            PyErr::new::<pyo3::exceptions::PyFileNotFoundError, _>(
                "Could not find 'python_gui' directory. It's gone. Reduced to atoms."
            )
        })?;



        // Add the found path to sys.path so Python can actually find the files
        sys_path.insert(0, gui_dir.to_string_lossy())?;
        if let Some(parent) = gui_dir.parent() {
             sys_path.insert(0, parent.to_string_lossy())?;
        }

        // 4. Import the application module.
        let app_path = gui_dir.join("app.py");
        let app_module = py.import("app").map_err(|e| {
             PyErr::new::<pyo3::exceptions::PyImportError, _>(
                format!("Failed to import 'app'. \nPath value: {:?} \nError: {}\nIs app.py actually there? {}", 
                    gui_dir, e, app_path.exists())
            )
        })?;
        
        // 5. Run the main function.
        // There is no turning back now.
        app_module.call_method0("main")?;

        Ok(())
    })
}
