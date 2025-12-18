use pyo3::prelude::*;

/// Manages the display widget in the header.
#[pyclass]
pub struct DisplayManager {
    placeholder: Py<PyAny>,
}

#[pymethods]
impl DisplayManager {
    #[new]
    fn new(placeholder: Py<PyAny>) -> Self {
        DisplayManager { placeholder }
    }

    fn switch_display_for(&self, py: Python<'_>, calc_widget: Py<PyAny>) -> PyResult<()> {
        if calc_widget.is_none(py) {
            return Ok(());
        }

        // Get display widget: display = calc_widget.get_display_widget()
        let display = calc_widget.call_method0(py, "get_display_widget")?;

        // Check if display is already a child of placeholder
        let parent = display.call_method0(py, "get_parent")?;
        
        let needs_add = if parent.is_none(py) {
            true
        } else {
            !parent.is(&self.placeholder)
        };

        if needs_add {
             if !parent.is_none(py) {
                 parent.call_method1(py, "remove", (&display,))?;
             }
             
             // Try to get name from calc_widget
             if calc_widget.bind(py).hasattr("calc_name")? {
                 let name: String = calc_widget.getattr(py, "calc_name")?.extract(py)?;
                 self.placeholder.call_method1(py, "add_named", (&display, &name))?;
             } else {
                 self.placeholder.call_method1(py, "add_child", (&display,))?;
             }
        }

        // For Gtk.Stack, we just switch the visible child
        self.placeholder.call_method1(py, "set_visible_child", (&display,))?;

        Ok(())
    }
}
