use pyo3::prelude::*;
use pyo3::types::PyDict;
use pyo3::exceptions::PyRuntimeError;
use super::constants::*;

pub fn create_calculator_widget(py: Python<'_>, parent_window: &Py<PyAny>) -> PyResult<Py<PyAny>> {
    let view_mod = py.import("python_gui.calculator.view")?;
    let calc_widget_class = view_mod.getattr("CalculatorWidget")?;
    
    let locals = PyDict::new(py);
    locals.set_item("CalculatorWidget", &calc_widget_class)?;
    let code = std::ffi::CString::new("CalculatorWidget()").map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
    let calc_widget = py.eval(&code, None, Some(&locals))?.unbind();

    calc_widget.bind(py).setattr(ATTR_PARENT_WINDOW, parent_window)?;
    Ok(calc_widget)
}

pub fn add_to_tab_view(py: Python<'_>, tab_view: &Py<PyAny>, calc_widget: &Py<PyAny>, title: &str, name: &str, count: i32) -> PyResult<Py<PyAny>> {
    let page = tab_view.bind(py).call_method1(METHOD_ADD_PAGE, (calc_widget,))?;
    page.call_method1(METHOD_SET_TITLE, (title,))?;
    let none_obj: Option<Py<PyAny>> = None; 
    page.call_method1(METHOD_SET_INDICATOR, (none_obj,))?;

    // Metadata
    page.setattr(ATTR_CALC_NAME, name)?;
    page.setattr(ATTR_CALC_WIDGET, calc_widget)?;
    page.setattr(ATTR_CALC_NUMBER, count)?;

    // Attach name to widget for DisplayManager reverse lookups
    calc_widget.setattr(py, ATTR_CALC_NAME, name)?;

    Ok(page.unbind())
}

pub fn connect_widget_signals(py: Python<'_>, calc_widget: &Py<PyAny>, row: &Py<PyAny>) -> PyResult<()> {
    let row_preview_label = row.bind(py).getattr(ATTR_PREVIEW_LABEL)?;
    
    let locals = PyDict::new(py);
    locals.set_item("preview_label", &row_preview_label)?;
    let code = std::ffi::CString::new("lambda text, pl=preview_label: pl.set_text(text or '0')").map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
    let lambda = py.eval(&code, None, Some(&locals))?;
    
    calc_widget.bind(py).setattr("on_expression_changed", lambda)?;
    Ok(())
}

pub fn find_page_by_widget(py: Python<'_>, tab_view: &Py<PyAny>, target_widget: &Py<PyAny>) -> PyResult<Option<(i32, Py<PyAny>)>> {
    let n_pages: i32 = tab_view.call_method0(py, METHOD_GET_N_PAGES)?.extract(py)?;
    for i in 0..n_pages {
        let page = tab_view.call_method1(py, METHOD_GET_NTH_PAGE, (i,))?;
        if page.bind(py).hasattr(ATTR_CALC_WIDGET)? {
            let page_cw = page.getattr(py, ATTR_CALC_WIDGET)?;
            if page_cw.is(target_widget) {
                return Ok(Some((i, page)));
            }
        }
    }
    Ok(None)
}

pub fn find_sidebar_row_by_widget(py: Python<'_>, sidebar_view: &Py<PyAny>, target_widget: &Py<PyAny>) -> PyResult<Option<Py<PyAny>>> {
    let sidebar_list = sidebar_view.getattr(py, ATTR_SIDEBAR_LIST)?;
    let mut i = 0;
    loop {
        let row = sidebar_list.call_method1(py, METHOD_GET_ROW_AT_INDEX, (i,))?;
        if row.is_none(py) { break; }
        
        if row.bind(py).hasattr(ATTR_CALC_WIDGET)? {
            let row_cw = row.getattr(py, ATTR_CALC_WIDGET)?;
            if row_cw.is(target_widget) {
                return Ok(Some(row));
            }
        }
        i += 1;
    }
    Ok(None)
}

pub fn format_title(history_entry: &str) -> String {
    let parts: Vec<&str> = history_entry.split(" = ").collect();
    let mut t = parts[0].to_string();
    if t.len() > 20 {
        t = format!("{}...", &t[..17]);
    }
    t
}

pub fn renumber_instances(py: Python<'_>, tab_view: &Py<PyAny>, sidebar_view: &Py<PyAny>) -> PyResult<()> {
    let n_pages: i32 = tab_view.call_method0(py, METHOD_GET_N_PAGES)?.extract(py)?;
    
    for i in 0..n_pages {
        let page = tab_view.call_method1(py, METHOD_GET_NTH_PAGE, (i,))?;
        let new_number = i + 1;
        
        if !page.bind(py).hasattr(ATTR_CALC_NUMBER)? { continue; }
        
        page.setattr(py, ATTR_CALC_NUMBER, new_number)?;
        
        let calc_widget = page.getattr(py, ATTR_CALC_WIDGET)?;
        let logic = calc_widget.getattr(py, ATTR_LOGIC)?;
        let history: Vec<String> = logic.call_method0(py, METHOD_GET_HISTORY)?.extract(py)?;
        
        let title = if let Some(last) = history.last() {
            format_title(last)
        } else {
            format!("Calculator {}", new_number)
        };
        
        page.call_method1(py, METHOD_SET_TITLE, (&title,))?;

        // Update sidebar
        if let Some(row) = find_sidebar_row_by_widget(py, sidebar_view, &calc_widget)? {
            row.setattr(py, ATTR_CALC_NUMBER, new_number)?;
            if row.bind(py).hasattr(ATTR_TITLE_LABEL)? {
                let tl = row.getattr(py, ATTR_TITLE_LABEL)?;
                tl.call_method1(py, METHOD_SET_LABEL, (&title,))?;
            }
        }
    }
    Ok(())
}
