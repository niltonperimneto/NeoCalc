use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::sync::{Arc, Mutex};

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
        // child = self.placeholder.get_first_child()
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
}

#[pymethods]
impl CalculatorManager {
    #[new]
    fn new(
        window: Py<PyAny>,
        tab_view: Py<PyAny>,
        sidebar_view: Py<PyAny>,
        display_manager: Py<PyAny>,
    ) -> Self {
        CalculatorManager {
            window,
            tab_view,
            sidebar_view,
            display_manager,
            instance_count: Arc::new(Mutex::new(0)),
            calculator_widgets: Arc::new(Mutex::new(Vec::new())),
        }
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
            let mut count = self.instance_count.lock().unwrap();
            *count = new_count;
        }

        let title = format!("Calculator {}", new_count);
        let name = format!("calc_{}", new_count);

        let view_mod = py.import("python_gui.calculator.view")?;
        let calc_widget_class = view_mod.getattr("CalculatorWidget")?;
        
        let locals = PyDict::new(py);
        locals.set_item("CalculatorWidget", &calc_widget_class)?;
        let code = std::ffi::CString::new("CalculatorWidget()").unwrap();
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

        // Create sidebar row
        let row = self._create_sidebar_row(py, &title, &name, calc_widget.clone_ref(py), new_count)?;
        
        self.sidebar_view.bind(py).call_method1("add_row", (&row,))?;

        {
            let mut widgets = self.calculator_widgets.lock().unwrap();
            widgets.push(calc_widget.clone_ref(py));
        }

        self.sidebar_view.bind(py).call_method1("select_row", (&row,))?;

        self.display_manager.bind(py).call_method1("switch_display_for", (&calc_widget,))?;

        // connect entry changed
        let row_preview_label = row.bind(py).getattr("preview_label")?;
        
        let locals = PyDict::new(py);
        locals.set_item("preview_label", &row_preview_label)?;
        // Use default argument to capture preview_label
        let code = std::ffi::CString::new("lambda e, pl=preview_label: pl.set_text(e.get_text() or '0')").unwrap();
        let lambda = py.eval(&code, None, Some(&locals))?;
        
        let entry = calc_widget.bind(py).getattr("entry")?;
        entry.call_method("connect", ("changed", lambda), None)?;

        Ok(())
    }

    fn _create_sidebar_row(&self, py: Python<'_>, title: &str, name: &str, calc_widget: Py<PyAny>, count: i32) -> PyResult<Py<PyAny>> {
        let gtk = py.import("gi.repository.Gtk")?;
        
        let row = gtk.call_method0("ListBoxRow")?;
        let row_box = gtk.call_method0("Box")?;
        // call_method1 passes tuple (arg,)
        row_box.call_method1("set_orientation", (gtk.getattr("Orientation")?.getattr("VERTICAL")?,))?;
        row_box.call_method1("set_spacing", (4,))?;
        row_box.setattr("margin_start", 4)?;
        row_box.setattr("margin_end", 4)?;
        row_box.setattr("margin_top", 4)?;
        row_box.setattr("margin_bottom", 4)?;

        let header_box = gtk.call_method0("Box")?;
        header_box.call_method1("set_orientation", (gtk.getattr("Orientation")?.getattr("HORIZONTAL")?,))?;
        header_box.call_method1("set_spacing", (4,))?;

        // Label() then set_label(title) because Gtk.Label(str) is not supported
        let title_label = gtk.call_method0("Label")?;
        title_label.call_method1("set_label", (title,))?;
        title_label.call_method1("set_xalign", (0.0,))?;
        title_label.call_method1("set_hexpand", (true,))?;
        title_label.call_method1("add_css_class", ("heading",))?;
        header_box.call_method1("append", (&title_label,))?;

        let close_btn = gtk.call_method0("Button")?;
        close_btn.call_method1("set_icon_name", ("window-close-symbolic",))?;
        close_btn.call_method1("add_css_class", ("flat",))?;
        close_btn.call_method1("add_css_class", ("circular",))?;
        close_btn.call_method1("set_tooltip_text", ("Close Calculation",))?;

        let locals = PyDict::new(py);
        locals.set_item("cw", &calc_widget)?;
        // Use default argument `cw=cw` to capture it in the lambda closure
        let code = std::ffi::CString::new("lambda b, cw=cw: cw.parent_window.calc_manager.on_close_calculator_from_sidebar(cw)").unwrap();
        let close_lambda = py.eval(&code, None, Some(&locals))?;
        close_btn.call_method("connect", ("clicked", close_lambda), None)?;

        header_box.call_method1("append", (&close_btn,))?;
        row_box.call_method1("append", (&header_box,))?;

        let preview_label = gtk.call_method0("Label")?;
        preview_label.call_method1("set_label", ("0",))?;
        preview_label.call_method1("set_xalign", (1.0,))?;
        preview_label.call_method1("add_css_class", ("calc-preview",))?;
        preview_label.call_method1("set_wrap", (true,))?;
        preview_label.call_method1("set_max_width_chars", (20,))?;
        row_box.call_method1("append", (&preview_label,))?;

        row.call_method1("set_child", (&row_box,))?;

        // Metadata
        row.setattr("calc_widget", calc_widget)?;
        row.setattr("calc_name", name)?;
        row.setattr("calc_number", count)?;
        row.setattr("preview_label", &preview_label)?;
        row.setattr("title_label", &title_label)?;

        Ok(row.into())
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
            let mut widgets = self.calculator_widgets.lock().unwrap();
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

        // If last one closed (and N=0), create new. BUT we prevent closing last one.
        // However, if we detach for other reasons?
        // Let's keep logic:
        let n_pages: i32 = self.tab_view.call_method0(py, "get_n_pages")?.extract(py)?;
        if n_pages == 0 {
             self.add_calculator_instance(py)?;
        }
        
        let mut count = self.instance_count.lock().unwrap();
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
