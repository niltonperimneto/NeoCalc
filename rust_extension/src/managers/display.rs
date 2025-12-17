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

        // Check if already child: current = self.placeholder.get_first_child()
        let current_child = self.placeholder.call_method0(py, "get_first_child")?;

        if current_child.is(&display) {
            // calc_widget.update_history_display()
            calc_widget.call_method0(py, "update_history_display")?;
            return Ok(());
        }

        // Remove existing children
        let mut child = self.placeholder.call_method0(py, "get_first_child")?;
        while !child.is_none(py) {
            let next_child = child.call_method0(py, "get_next_sibling")?;
            self.placeholder.call_method1(py, "remove", (&child,))?;
            child = next_child;
        }

        // Unparent if needed
        let parent = display.call_method0(py, "get_parent")?;
        if !parent.is_none(py) && !parent.is(&self.placeholder) {
            parent.call_method1(py, "remove", (&display,))?;
        }

        // Append
        self.placeholder.call_method1(py, "append", (&display,))?;

        Ok(())
    }
}
