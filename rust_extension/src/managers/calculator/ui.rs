use pyo3::prelude::*;
use pyo3::types::PyDict;

/// Helper to create a sidebar row widget
pub fn create_sidebar_row(py: Python<'_>, title: &str, name: &str, calc_widget: Py<PyAny>, count: i32) -> PyResult<Py<PyAny>> {
    let gtk = py.import("gi.repository.Gtk")?;
    
    let row = gtk.call_method0("ListBoxRow")?;
    let row_box = gtk.call_method0("Box")?;
    
    // Setup Row Box
    row_box.call_method1("set_orientation", (gtk.getattr("Orientation")?.getattr("VERTICAL")?,))?;
    row_box.call_method1("set_spacing", (4,))?;
    row_box.setattr("margin_start", 4)?;
    row_box.setattr("margin_end", 4)?;
    row_box.setattr("margin_top", 4)?;
    row_box.setattr("margin_bottom", 4)?;

    // Setup Header Box
    let header_box = gtk.call_method0("Box")?;
    header_box.call_method1("set_orientation", (gtk.getattr("Orientation")?.getattr("HORIZONTAL")?,))?;
    header_box.call_method1("set_spacing", (4,))?;

    // Title Label
    let title_label = gtk.call_method0("Label")?;
    title_label.call_method1("set_label", (title,))?;
    title_label.call_method1("set_xalign", (0.0,))?;
    title_label.call_method1("set_hexpand", (true,))?;
    title_label.call_method1("add_css_class", ("heading",))?;
    header_box.call_method1("append", (&title_label,))?;

    // Close Button
    let close_btn = gtk.call_method0("Button")?;
    close_btn.call_method1("set_icon_name", ("window-close-symbolic",))?;
    close_btn.call_method1("add_css_class", ("flat",))?;
    close_btn.call_method1("add_css_class", ("circular",))?;
    close_btn.call_method1("set_tooltip_text", ("Close Calculation",))?;

    // Connect Close Signal
    let locals = PyDict::new(py);
    locals.set_item("cw", &calc_widget)?;
    // Use default argument `cw=cw` to capture it in the lambda closure
    let code = std::ffi::CString::new("lambda b, cw=cw: cw.parent_window.calc_manager.on_close_calculator_from_sidebar(cw)").map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
    let close_lambda = py.eval(&code, None, Some(&locals))?;
    close_btn.call_method("connect", ("clicked", close_lambda), None)?;

    header_box.call_method1("append", (&close_btn,))?;
    row_box.call_method1("append", (&header_box,))?;

    // Preview Label
    let preview_label = gtk.call_method0("Label")?;
    preview_label.call_method1("set_label", ("0",))?;
    preview_label.call_method1("set_xalign", (1.0,))?;
    preview_label.call_method1("add_css_class", ("calc-preview",))?;
    preview_label.call_method1("set_wrap", (true,))?;
    preview_label.call_method1("set_max_width_chars", (20,))?;
    row_box.call_method1("append", (&preview_label,))?;

    row.call_method1("set_child", (&row_box,))?;

    // Store Metadata
    row.setattr("calc_widget", calc_widget)?;
    row.setattr("calc_name", name)?;
    row.setattr("calc_number", count)?;
    row.setattr("preview_label", &preview_label)?;
    row.setattr("title_label", &title_label)?;

    Ok(row.into())
}
