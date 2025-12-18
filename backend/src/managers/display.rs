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

        // Always update history
        calc_widget.call_method0(py, "update_history_display")?;

        // Check parent
        let parent = display.call_method0(py, "get_parent")?;
        
        if parent.is(&self.placeholder) {
            // Already in stack, just show it
            self.placeholder.call_method1(py, "set_visible_child", (&display,))?;
            return Ok(());
        }

        // If it has a different parent, remove it first? 
        // GTK4 usually reparents automatically or warns. Safe to unparent.
        if !parent.is_none(py) {
             parent.call_method1(py, "remove", (&display,))?;
        }

        // Add to stack and show
        // Using "add_child" for GtkStack
        self.placeholder.call_method1(py, "add_child", (&display,))?;
        self.placeholder.call_method1(py, "set_visible_child", (&display,))?;

        Ok(())
    }
}
