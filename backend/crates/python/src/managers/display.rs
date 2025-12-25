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

        let display = calc_widget.call_method0(py, "get_display_widget")?;

        calc_widget.call_method0(py, "update_history_display")?;

        let parent = display.call_method0(py, "get_parent")?;

        if parent.is(&self.placeholder) {

            self.placeholder.call_method1(py, "set_visible_child", (&display,))?;
            return Ok(());
        }

        if !parent.is_none(py) {
             parent.call_method1(py, "remove", (&display,))?;
        }

        self.placeholder.call_method1(py, "add_child", (&display,))?;
        self.placeholder.call_method1(py, "set_visible_child", (&display,))?;

        Ok(())
    }
}
