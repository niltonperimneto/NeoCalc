from gi.repository import Gtk, Adw
from ..view import CalculatorWidget

class CalculatorManager:
    """Manages calculator instances, sidebar rows, and tab pages."""
    
    def __init__(self, window, tab_view, sidebar_view, display_manager):
        self.window = window
        self.tab_view = tab_view
        self.sidebar_view = sidebar_view
        self.display_manager = display_manager
        
        self.instance_count = 0
        self.calculator_widgets = []
        
        # Connect tab signals
        self.tab_view.connect("notify::selected-page", self.on_tab_page_changed)
        self.tab_view.connect("close-page", self.on_close_calculator_clicked)
        self.tab_view.connect("page-detached", self.on_page_detached)

    def add_calculator_instance(self):
        self.instance_count += 1
        title = f"Calculator {self.instance_count}"
        
        # Create Widget
        calc_widget = CalculatorWidget()
        calc_widget.parent_window = self.window
        name = f"calc_{self.instance_count}"
        
        # Add to tab view
        page = self.tab_view.add_page(calc_widget)
        page.set_title(title)
        page.set_indicator_icon(None)
        
        # Store metadata
        page.calc_name = name
        page.calc_widget = calc_widget
        page.calc_number = self.instance_count
        
        self.tab_view.set_selected_page(page)
        
        # Add to sidebar list via SidebarView helper
        row = self._create_sidebar_row(title, name, calc_widget)
        
        self.sidebar_view.add_row(row)
        self.calculator_widgets.append(calc_widget)
        
        self.sidebar_view.select_row(row)
        self.display_manager.switch_display_for(calc_widget)
        
        if hasattr(row, 'preview_label'):
             calc_widget.entry.connect("changed", lambda e: row.preview_label.set_text(e.get_text() or "0"))

    def _create_sidebar_row(self, title, name, calc_widget):
        row = Gtk.ListBoxRow()
        row_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        row_box.set_margin_start(4)
        row_box.set_margin_end(4)
        row_box.set_margin_top(4)
        row_box.set_margin_bottom(4)
        
        # Row Header (Title + Close Button)
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        
        title_label = Gtk.Label(label=title)
        title_label.set_xalign(0)
        title_label.set_hexpand(True)
        title_label.add_css_class("heading")
        header_box.append(title_label)
        
        close_btn = Gtk.Button(icon_name="window-close-symbolic")
        close_btn.add_css_class("flat")
        close_btn.add_css_class("circular")
        close_btn.set_tooltip_text("Close Calculation")
        # Prevent row selection when clicking close
        close_btn.connect("clicked", lambda b: self.on_close_calculator_from_sidebar(calc_widget))
        header_box.append(close_btn)
        
        row_box.append(header_box)
        
        preview_label = Gtk.Label(label="0")
        preview_label.set_xalign(1)
        preview_label.add_css_class("calc-preview")
        preview_label.set_wrap(True)
        preview_label.set_max_width_chars(20)
        row_box.append(preview_label)
        
        row.set_child(row_box)
        
        # Store references
        row.calc_widget = calc_widget
        row.calc_name = name
        row.calc_number = self.instance_count
        row.preview_label = preview_label
        row.title_label = title_label
        
        return row

    def update_calculator_name(self, calc_widget):
        history = calc_widget.logic.get_history()
        
        if not history:
            return
        
        n_pages = self.tab_view.get_n_pages()
        for i in range(n_pages):
            page = self.tab_view.get_nth_page(i)
            if hasattr(page, 'calc_widget') and page.calc_widget is calc_widget:
                latest = history[-1].split(' = ')[0]
                if len(latest) > 20:
                    latest = latest[:17] + "..."
                page.set_title(latest if latest else f"Calculator {page.calc_number}")
                break

    def on_page_detached(self, tab_view, page, position):
        """Called when a page is removed from the tab view. Clean up sidebar."""
        if not hasattr(page, 'calc_widget'):
            return

        calc_widget = page.calc_widget
        
        # Remove from list
        if calc_widget in self.calculator_widgets:
            self.calculator_widgets.remove(calc_widget)
            
        # Remove sidebar row
        row_to_remove = None
        
        i = 0
        while True:
             row = self.sidebar_view.sidebar_list.get_row_at_index(i)
             if row is None:
                 break
             
             if hasattr(row, 'calc_widget') and row.calc_widget is calc_widget:
                 row_to_remove = row
                 break
             i += 1
             
        if row_to_remove:
            self.sidebar_view.sidebar_list.remove(row_to_remove)

        # If last one closed, create new
        if self.tab_view.get_n_pages() == 0:
            self.add_calculator_instance()

    def on_close_calculator_clicked(self, tab_view, page):
        # Allow default handler to close the page
        return False
            
    def on_close_calculator_from_sidebar(self, calc_widget):
        n_pages = self.tab_view.get_n_pages()
        for i in range(n_pages):
            page = self.tab_view.get_nth_page(i)
            if hasattr(page, 'calc_widget') and page.calc_widget is calc_widget:
                self.tab_view.close_page(page)
                break
            
    def on_tab_page_changed(self, tab_view, param):
        page = tab_view.get_selected_page()
        if page and hasattr(page, 'calc_widget'):
            self.display_manager.switch_display_for(page.calc_widget)
            page.calc_widget.grab_focus()

    def on_sidebar_row_selected(self, box, row):
        if row is not None and hasattr(row, 'calc_widget'):
            n_pages = self.tab_view.get_n_pages()
            for i in range(n_pages):
                page = self.tab_view.get_nth_page(i)
                if hasattr(page, 'calc_widget') and page.calc_widget is row.calc_widget:
                    self.tab_view.set_selected_page(page)
                    # self.display_manager.switch_display_for(row.calc_widget) # Redundant?
                    break
