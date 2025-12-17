pub mod ui;

use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::sync::{Arc, Mutex};
use pyo3::exceptions::PyRuntimeError;

/// Manages calculator instances, sidebar rows, and tab pages.
#[pyclass]
pub struct CalculatorManager {
    window: Py<PyAny>,
    tab_view: Py<PyAny>,
    sidebar_view: Py<PyAny>,
    display_manager: Py<PyAny>, 
    
    // State
    instance_count: Arc<Mutex<i32>>,
    calculator_widgets: Arc<Mutex<Vec<Py<PyAny>>>>,

    // Async runtime helper
    rt: tokio::runtime::Runtime,
}

#[pymethods]
impl CalculatorManager {
    #[new]
    fn new(
        window: Py<PyAny>,
        tab_view: Py<PyAny>,
        sidebar_view: Py<PyAny>,
        display_manager: Py<PyAny>,
    ) -> PyResult<Self> {
        let rt = tokio::runtime::Builder::new_multi_thread()
            .enable_all()
            .build()
            .map_err(|e| PyRuntimeError::new_err(format!("Failed to create runtime: {}", e)))?;

        Ok(CalculatorManager {
            window,
            tab_view,
            sidebar_view,
            display_manager,
            instance_count: Arc::new(Mutex::new(0)),
            calculator_widgets: Arc::new(Mutex::new(Vec::new())),
            rt,
        })
    }

    /// Simulate a heavy async calculation
    fn perform_async_calc(&self, py: Python<'_>, seconds: u64) -> PyResult<Py<PyAny>> {
        let _guard = self.rt.enter();
        let fut = async move {
            tokio::time::sleep(std::time::Duration::from_secs(seconds)).await;
            Ok(format!("Finished calculation after {} seconds", seconds))
        };
        
        let awaitable = pyo3_async_runtimes::tokio::future_into_py(py, fut)?;
        Ok(awaitable.unbind())
    }

    fn setup_signals(&self, py: Python<'_>, pyself: Py<PyAny>) -> PyResult<()> {
        let on_tab_page_changed = pyself.getattr(py, "on_tab_page_changed")?;
        self.tab_view.bind(py).call_method("connect", ("notify::selected-page", on_tab_page_changed), None)?;
        
        let on_close_page = pyself.getattr(py, "on_close_calculator_clicked")?;
        self.tab_view.bind(py).call_method("connect", ("close-page", on_close_page), None)?;

        let on_page_detached = pyself.getattr(py, "on_page_detached")?;
        self.tab_view.bind(py).call_method("connect", ("page-detached", on_page_detached), None)?;

        Ok(())
    }

    fn add_calculator_instance(&self, py: Python<'_>) -> PyResult<()> {
        let n_pages: i32 = self.tab_view.bind(py).call_method0("get_n_pages")?.extract()?;
        let new_count = n_pages + 1;
        
        {
            let mut count = self.instance_count.lock().map_err(|e| PyRuntimeError::new_err(format!("Lock poisoned: {}", e)))?;
            *count = new_count;
        }

        let title = format!("Calculator {}", new_count);
        let name = format!("calc_{}", new_count);

        let view_mod = py.import("python_gui.calculator.view")?;
        let calc_widget_class = view_mod.getattr("CalculatorWidget")?;
        
        let locals = PyDict::new(py);
        locals.set_item("CalculatorWidget", &calc_widget_class)?;
        let code = std::ffi::CString::new("CalculatorWidget()").map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
        let calc_widget = py.eval(&code, None, Some(&locals))?.unbind();

        // calc_widget.parent_window = self.window
        calc_widget.bind(py).setattr("parent_window", &self.window)?;

        // Add to tab view
        let page = self.tab_view.bind(py).call_method1("add_page", (&calc_widget,))?;
        page.call_method1("set_title", (&title,))?;
        let none_obj: Option<Py<PyAny>> = None; 
        page.call_method1("set_indicator_icon", (none_obj,))?;

        // Store metadata
        page.setattr("calc_name", &name)?;
        page.setattr("calc_widget", &calc_widget)?;
        page.setattr("calc_number", new_count)?;

        self.tab_view.bind(py).call_method1("set_selected_page", (&page,))?;

        // Create sidebar row via helper
        let row = ui::create_sidebar_row(py, &title, &name, calc_widget.clone_ref(py), new_count)?;
        
        self.sidebar_view.bind(py).call_method1("add_row", (&row,))?;

        {
            let mut widgets = self.calculator_widgets.lock().map_err(|e| PyRuntimeError::new_err(format!("Lock poisoned: {}", e)))?;
            widgets.push(calc_widget.clone_ref(py));
        }

        self.sidebar_view.bind(py).call_method1("select_row", (&row,))?;

        self.display_manager.bind(py).call_method1("switch_display_for", (&calc_widget,))?;

        // connect entry changed
        let row_preview_label = row.bind(py).getattr("preview_label")?;
        
        let locals = PyDict::new(py);
        locals.set_item("preview_label", &row_preview_label)?;
        // Use default argument to capture preview_label
        let code = std::ffi::CString::new("lambda e, pl=preview_label: pl.set_text(e.get_text() or '0')").map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
        let lambda = py.eval(&code, None, Some(&locals))?;
        
        let entry = calc_widget.bind(py).getattr("entry")?;
        entry.call_method("connect", ("changed", lambda), None)?;

        Ok(())
    }

    fn on_close_calculator_from_sidebar(&self, py: Python<'_>, calc_widget: Py<PyAny>) -> PyResult<()> {
        let n_pages: i32 = self.tab_view.call_method0(py, "get_n_pages")?.extract(py)?;
        if n_pages <= 1 {
            return Ok(());
        }

        for i in 0..n_pages {
            let page = self.tab_view.call_method1(py, "get_nth_page", (i,))?;
            if !page.bind(py).hasattr("calc_widget")? { continue; }
            let page_cw = page.getattr(py, "calc_widget")?;
            if page_cw.is(&calc_widget) {
                self.tab_view.call_method1(py, "close_page", (&page,))?;
                break;
            }
        }
        Ok(())
    }

    fn on_close_calculator_clicked(&self, py: Python<'_>, _tab_view: Py<PyAny>, _page: Py<PyAny>) -> PyResult<bool> {
        let n_pages: i32 = self.tab_view.call_method0(py, "get_n_pages")?.extract(py)?;
        if n_pages <= 1 {
            Ok(true) // Stop close
        } else {
            Ok(false) // Allow close
        }
    }

    fn on_page_detached(&self, py: Python<'_>, _tab_view: Py<PyAny>, page: Py<PyAny>, _position: Py<PyAny>) -> PyResult<()> {
        if !page.bind(py).hasattr("calc_widget")? { return Ok(()); }
        let calc_widget = page.getattr(py, "calc_widget")?;

        // Remove from widgets list
        {
            let mut widgets = self.calculator_widgets.lock().map_err(|e| PyRuntimeError::new_err(format!("Lock poisoned: {}", e)))?;
            if let Some(pos) = widgets.iter().position(|x| x.is(&calc_widget)) {
                widgets.remove(pos);
            }
        }

        // Remove sidebar row
        let sidebar_list = self.sidebar_view.getattr(py, "sidebar_list")?;
        let mut i = 0;
        let mut row_to_remove: Option<Py<PyAny>> = None;
        loop {
            let row = sidebar_list.call_method1(py, "get_row_at_index", (i,))?;
            if row.is_none(py) { break; }
            
            if row.bind(py).hasattr("calc_widget")? {
                let row_cw = row.getattr(py, "calc_widget")?;
                if row_cw.is(&calc_widget) {
                    row_to_remove = Some(row);
                    break;
                }
            }
            i += 1;
        }

        if let Some(row) = row_to_remove {
            sidebar_list.call_method1(py, "remove", (row,))?;
        }

        self.renumber_instances(py)?;

        let n_pages: i32 = self.tab_view.call_method0(py, "get_n_pages")?.extract(py)?;
        if n_pages == 0 {
             self.add_calculator_instance(py)?;
        }
        
        let mut count = self.instance_count.lock().map_err(|e| PyRuntimeError::new_err(format!("Lock poisoned: {}", e)))?;
        *count = n_pages;

        Ok(())
    }

    fn renumber_instances(&self, py: Python<'_>) -> PyResult<()> {
        let n_pages: i32 = self.tab_view.call_method0(py, "get_n_pages")?.extract(py)?;
        for i in 0..n_pages {
            let page = self.tab_view.call_method1(py, "get_nth_page", (i,))?;
            let new_number = i + 1;
            
            if page.bind(py).hasattr("calc_number")? {
                page.setattr(py, "calc_number", new_number)?;
                
                let calc_widget = page.getattr(py, "calc_widget")?;
                let logic = calc_widget.getattr(py, "logic")?;
                let history: Vec<String> = logic.call_method0(py, "get_history")?.extract(py)?;
                
                let title = if let Some(last) = history.last() {
                    let parts: Vec<&str> = last.split(" = ").collect();
                    let mut t = parts[0].to_string();
                    if t.len() > 20 {
                        t = format!("{}...", &t[..17]);
                    }
                    t
                } else {
                    format!("Calculator {}", new_number)
                };
                
                page.call_method1(py, "set_title", (&title,))?;

                // Update sidebar
                 let sidebar_list = self.sidebar_view.getattr(py, "sidebar_list")?;
                 let mut j = 0;
                 loop {
                     let row = sidebar_list.call_method1(py, "get_row_at_index", (j,))?;
                     if row.is_none(py) { break; }
                     if row.bind(py).hasattr("calc_widget")? {
                         let row_cw = row.getattr(py, "calc_widget")?;
                         if row_cw.is(&calc_widget) {
                             row.setattr(py, "calc_number", new_number)?;
                             if row.bind(py).hasattr("title_label")? {
                                 let tl = row.getattr(py, "title_label")?;
                                 tl.call_method1(py, "set_label", (&title,))?;
                             }
                             break;
                         }
                     }
                     j += 1;
                 }
            }
        }
        Ok(())
    }

    fn update_calculator_name(&self, py: Python<'_>, calc_widget: Py<PyAny>) -> PyResult<()> {
        let logic = calc_widget.getattr(py, "logic")?;
        let history: Vec<String> = logic.call_method0(py, "get_history")?.extract(py)?;
        
        if history.is_empty() { return Ok(()); }

        let n_pages: i32 = self.tab_view.call_method0(py, "get_n_pages")?.extract(py)?;
        for i in 0..n_pages {
            let page = self.tab_view.call_method1(py, "get_nth_page", (i,))?;
            if page.bind(py).hasattr("calc_widget")? {
                let page_cw = page.getattr(py, "calc_widget")?;
                if page_cw.is(&calc_widget) {
                    let last = history.last().unwrap();
                    let parts: Vec<&str> = last.split(" = ").collect();
                    let mut t = parts[0].to_string();
                    if t.len() > 20 {
                        t = format!("{}...", &t[..17]);
                    }
                    page.call_method1(py, "set_title", (&t,))?;
                    break;
                }
            }
        }
        Ok(())
    }
    
    fn on_tab_page_changed(&self, py: Python<'_>, tab_view: Py<PyAny>, _param: Py<PyAny>) -> PyResult<()> {
        let page = tab_view.call_method0(py, "get_selected_page")?;
        if !page.is_none(py) && page.bind(py).hasattr("calc_widget")? {
             let calc_widget = page.getattr(py, "calc_widget")?;
             self.display_manager.call_method1(py, "switch_display_for", (&calc_widget,))?;
             calc_widget.call_method0(py, "grab_focus")?;
        }
        Ok(())
    }

    fn on_sidebar_row_selected(&self, py: Python<'_>, _box: Py<PyAny>, row: Py<PyAny>) -> PyResult<()> {
        if !row.is_none(py) && row.bind(py).hasattr("calc_widget")? {
             let calc_widget = row.getattr(py, "calc_widget")?;
             let n_pages: i32 = self.tab_view.call_method0(py, "get_n_pages")?.extract(py)?;
             for i in 0..n_pages {
                 let page = self.tab_view.call_method1(py, "get_nth_page", (i,))?;
                 if page.bind(py).hasattr("calc_widget")? {
                     let page_cw = page.getattr(py, "calc_widget")?;
                     if page_cw.is(&calc_widget) {
                         self.tab_view.call_method1(py, "set_selected_page", (&page,))?;
                         break;
                     }
                 }
             }
        }
        Ok(())
    }
}
