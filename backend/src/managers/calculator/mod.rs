pub mod ui;
pub mod constants;
pub mod helpers;

use pyo3::prelude::*;
use std::sync::{Arc, Mutex};
use pyo3::exceptions::PyRuntimeError;

use constants::*;
use gettextrs::gettext;

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
    _rt: tokio::runtime::Runtime,
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
            _rt: rt,
        })
    }

    fn setup_signals(&self, py: Python<'_>, pyself: Py<PyAny>) -> PyResult<()> {
        let on_tab_page_changed = pyself.getattr(py, "on_tab_page_changed")?;
        self.tab_view.bind(py).call_method(METHOD_CONNECT, (EVENT_NOTIFY_SELECTED_PAGE, on_tab_page_changed), None)?;
        
        let on_close_page = pyself.getattr(py, "on_close_calculator_clicked")?;
        self.tab_view.bind(py).call_method(METHOD_CONNECT, (EVENT_CLOSE_PAGE, on_close_page), None)?;

        let on_page_detached = pyself.getattr(py, "on_page_detached")?;
        self.tab_view.bind(py).call_method(METHOD_CONNECT, (EVENT_PAGE_DETACHED, on_page_detached), None)?;

        Ok(())
    }

    fn add_calculator_instance(&self, py: Python<'_>) -> PyResult<()> {
        let n_pages: i32 = self.tab_view.bind(py).call_method0(METHOD_GET_N_PAGES)?.extract()?;
        let new_count = n_pages + 1;
        
        {
            let mut count = helpers::lock_mutex(&self.instance_count)?;
            *count = new_count;
        }

        let title = format!("{} {}", gettext("Calculator"), new_count);
        let name = format!("calc_{}", new_count);

        // 1. Create Python Widget
        let calc_widget = helpers::create_calculator_widget(py, &self.window)?;

        // 2. Add to TabView
        let page = helpers::add_to_tab_view(py, &self.tab_view, &calc_widget, &title, &name, new_count)?;

        // 3. Create Sidebar Row
        let row = ui::create_sidebar_row(py, &title, &name, calc_widget.clone_ref(py), new_count)?;
        self.sidebar_view.bind(py).call_method1(METHOD_ADD_ROW, (&row,))?;
        
        // 4. Update internal tracking
        {
            let mut widgets = helpers::lock_mutex(&self.calculator_widgets)?;
            widgets.push(calc_widget.clone_ref(py));
        }

        // 5. Select new instance
        self.sidebar_view.bind(py).call_method1(METHOD_SELECT_ROW, (&row,))?;
        self.tab_view.bind(py).call_method1(METHOD_SET_SELECTED_PAGE, (&page,))?;

        // 6. Connect dynamic label signals (preview update)
        helpers::connect_widget_signals(py, &calc_widget, &row)?;

        // 7. Initialize Display Stack
        self.display_manager.bind(py).call_method1(METHOD_SWITCH_DISPLAY, (&calc_widget,))?;

        Ok(())
    }

    fn on_close_calculator_from_sidebar(&self, py: Python<'_>, calc_widget: Py<PyAny>) -> PyResult<()> {
        let n_pages: i32 = self.tab_view.call_method0(py, METHOD_GET_N_PAGES)?.extract(py)?;
        if n_pages <= 1 {
            return Ok(());
        }

        if let Some((_, page)) = helpers::find_page_by_widget(py, &self.tab_view, &calc_widget)? {
            self.tab_view.call_method1(py, METHOD_CLOSE_PAGE, (&page,))?;
        }
        Ok(())
    }

    fn on_close_calculator_clicked(&self, py: Python<'_>, _tab_view: Py<PyAny>, _page: Py<PyAny>) -> PyResult<bool> {
        let n_pages: i32 = self.tab_view.call_method0(py, METHOD_GET_N_PAGES)?.extract(py)?;
        Ok(n_pages <= 1) 
    }

    fn on_page_detached(&self, py: Python<'_>, _tab_view: Py<PyAny>, page: Py<PyAny>, _position: Py<PyAny>) -> PyResult<()> {
        if !page.bind(py).hasattr(ATTR_CALC_WIDGET)? { return Ok(()); }
        let calc_widget = page.getattr(py, ATTR_CALC_WIDGET)?;

        // Remove from widgets list
        {
            let mut widgets = helpers::lock_mutex(&self.calculator_widgets)?;
            if let Some(pos) = widgets.iter().position(|x| x.is(&calc_widget)) {
                widgets.remove(pos);
            }
        }

        // Remove sidebar row
        if let Some(row) = helpers::find_sidebar_row_by_widget(py, &self.sidebar_view, &calc_widget)? {
             let sidebar_list = self.sidebar_view.getattr(py, ATTR_SIDEBAR_LIST)?;
             sidebar_list.call_method1(py, METHOD_REMOVE, (row,))?;
        }

        helpers::renumber_instances(py, &self.tab_view, &self.sidebar_view)?;

        let n_pages: i32 = self.tab_view.call_method0(py, METHOD_GET_N_PAGES)?.extract(py)?;
        if n_pages == 0 {
             self.add_calculator_instance(py)?;
        }
        
        let mut count = helpers::lock_mutex(&self.instance_count)?;
        *count = if n_pages == 0 { 1 } else { n_pages };

        Ok(())
    }

    fn update_calculator_name(&self, py: Python<'_>, calc_widget: Py<PyAny>) -> PyResult<()> {
        let logic = calc_widget.getattr(py, ATTR_LOGIC)?;
        let history: Vec<String> = logic.call_method0(py, METHOD_GET_HISTORY)?.extract(py)?;
        
        if history.is_empty() { return Ok(()); }

        if let Some((_, page)) = helpers::find_page_by_widget(py, &self.tab_view, &calc_widget)? {
            // SAFE UNWRAP Replacement
            if let Some(last) = history.last() {
                let title = helpers::format_title(last);
                page.call_method1(py, METHOD_SET_TITLE, (&title,))?;
                
                if let Some(row) = helpers::find_sidebar_row_by_widget(py, &self.sidebar_view, &calc_widget)? {
                    if row.bind(py).hasattr(ATTR_TITLE_LABEL)? {
                         let tl = row.getattr(py, ATTR_TITLE_LABEL)?;
                         tl.call_method1(py, METHOD_SET_LABEL, (&title,))?;
                    }
                }
            }
        }
        Ok(())
    }
    
    fn on_tab_page_changed(&self, py: Python<'_>, tab_view: Py<PyAny>, _param: Py<PyAny>) -> PyResult<()> {
        let page = tab_view.call_method0(py, METHOD_GET_SELECTED_PAGE)?;
        if !page.is_none(py) && page.bind(py).hasattr(ATTR_CALC_WIDGET)? {
             let calc_widget = page.getattr(py, ATTR_CALC_WIDGET)?;
             self.display_manager.call_method1(py, METHOD_SWITCH_DISPLAY, (&calc_widget,))?;
             calc_widget.call_method0(py, METHOD_GRAB_FOCUS)?;
             
             // Sync Sidebar Selection
             if let Some(row) = helpers::find_sidebar_row_by_widget(py, &self.sidebar_view, &calc_widget)? {
                 let sidebar_list = self.sidebar_view.getattr(py, ATTR_SIDEBAR_LIST)?;
                 let selected_row = sidebar_list.call_method0(py, "get_selected_row")?;
                 
                 // Only select if not already selected to avoid loops/redundancy
                 if selected_row.is_none(py) || !selected_row.is(&row) {
                     sidebar_list.call_method1(py, METHOD_SELECT_ROW, (&row,))?;
                 }
             }
        }
        Ok(())
    }

    fn on_sidebar_row_selected(&self, py: Python<'_>, _box: Py<PyAny>, row: Py<PyAny>) -> PyResult<()> {
        if !row.is_none(py) && row.bind(py).hasattr(ATTR_CALC_WIDGET)? {
             let calc_widget = row.getattr(py, ATTR_CALC_WIDGET)?;
             if let Some((_, page)) = helpers::find_page_by_widget(py, &self.tab_view, &calc_widget)? {
                 self.tab_view.call_method1(py, METHOD_SET_SELECTED_PAGE, (&page,))?;
             }
        }
        Ok(())
    }
}
