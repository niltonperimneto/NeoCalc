use gettextrs::*;
use neocalc_backend::neocalc_backend;
use pyo3::prelude::*;
use pyo3::types::PyList;
use std::env;
use std::path::PathBuf;

#[tokio::main(flavor = "current_thread")]
async fn main() -> PyResult<()> {
    /* Initialize localization support (gettext) */
    setlocale(LocaleCategory::LcAll, "");
    bindtextdomain("neocalc", "locale").expect("Failed to bind text domain");
    textdomain("neocalc").expect("Failed to set text domain");

    /* Build a new Python module from the request Rust functions */
    pyo3::append_to_inittab!(neocalc_backend);

    /* Initialize the embedded Python interpreter */
    Python::attach(|py| {
        let sys = py.import("sys")?;

        let sys_path: Bound<PyList> = sys.getattr("path")?.extract()?;

        /* Try to locate the 'python' folder containing the app source code */
        let mut found_path: Option<PathBuf> = None;

        /* Look relative to the current executable first */
        if let Ok(exe_path) = env::current_exe() {
             if let Some(exe_dir) = exe_path.parent() {
                 let candidate = exe_dir.join("python");
                 if candidate.exists() {
                     found_path = Some(candidate);
                 } else {

                      /* Fallback: look in parent directories (development environment) */
                     let mut current_search = exe_dir.to_path_buf();
                     for _ in 0..3 {
                        if let Some(parent) = current_search.parent() {
                            let candidate = parent.join("python");
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

        /* Final check in current working directory */
        if found_path.is_none() {
             if let Ok(cwd) = env::current_dir() {
                 let candidate = cwd.join("python");
                 if candidate.exists() {
                     found_path = Some(candidate);
                 }
             }
        }

        let gui_dir = found_path.ok_or_else(|| {
            PyErr::new::<pyo3::exceptions::PyFileNotFoundError, _>(gettext(
                "Could not find 'python' directory. It's gone. Reduced to atoms.",
            ))
        })?;

        /* Add the found directory to Python path */
        sys_path.insert(0, gui_dir.to_string_lossy())?;

        /* Import the Python application entry point */
        let app_module = py.import("neocalc.app").map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyImportError, _>(format!(
                "Failed to import 'neocalc.app'. \nPath value: {:?} \nError: {}",
                gui_dir, e
            ))
        })?;

        /* Start the application */
        app_module.call_method0("main")?;

        Ok(())
    })
}
