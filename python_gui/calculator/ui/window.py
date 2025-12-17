import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GLib, Gdk
import os

from ..about import present_about_dialog
from ..view import CalculatorWidget
from ..styling import StyleManager
from ..actions import ActionRegistry
from .sidebar import SidebarView
from .header import HeaderView

class Calculator(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("NeoCalc")
        self.set_default_size(320, 500)
        self.set_size_request(320, 400)
        self.set_resizable(True)

        # --- Setup Logic ---
        self.action_registry = ActionRegistry(self)
        self.setup_layout()
        
        # --- Shortcuts Controller (Override) ---
        self.setup_keyboard_controller()
        
        # --- Initialization ---
        self.instance_count = 0
        self.calculator_widgets = []
        self.add_calculator_instance()
        
        # --- Styling ---
        StyleManager.load_css()

    def setup_layout(self):
        """Initializes the main window layout using OverlaySplitView."""
        self.split_view = Adw.OverlaySplitView()
        self.split_view.set_show_sidebar(False)
        self.set_content(self.split_view)

        # 1. Sidebar (Using new SidebarView)
        self.sidebar_view = SidebarView(self)
        self.split_view.set_sidebar(self.sidebar_view)
        
        # 2. Sidebar List Reference (for access if needed, though view handles it)
        # We might need direct access for row traversing in 'on_close_current_clicked'
        self.sidebar_list = self.sidebar_view.sidebar_list

        # 3. Content Area
        self.setup_content()

    def setup_content(self):
        """Constructs the main content area."""
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        # 1. Header (Using new HeaderView)
        self.header_view = HeaderView(self)
        content_box.append(self.header_view)
        # Expose type dropdown for actions to control it
        self.type_dropdown = self.header_view.type_dropdown

        # 2. Calculator Header Extension: display only
        calc_header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        calc_header.add_css_class("calculator-header-extension")

        # Placeholder for the display - NOW A STACK
        self.display_stack = Gtk.Stack()
        self.display_stack.add_css_class("calculator-display-header")
        calc_header.append(self.display_stack)

        content_box.append(calc_header)

        # 3. Tab View (Content)
        self.tab_view = Adw.TabView()
        self.tab_view.connect("notify::selected-page", self.on_tab_page_changed)
        self.tab_view.set_vexpand(True)
        self.tab_view.set_hexpand(True)
        content_box.append(self.tab_view)
        
        # Attach to View
        nav_page = Adw.NavigationPage(child=content_box, title="Calculator")
        self.split_view.set_content(nav_page)

    # switch_display_for is REMOVED
    pass

    def setup_keyboard_controller(self):
        # We now rely on standard Actions for Alt+N shortcuts.
        # No manual controller needed.
        pass

    def on_toggle_sidebar(self, button):
        current_state = self.split_view.get_show_sidebar()
        new_state = not current_state
        self.split_view.set_show_sidebar(new_state)

    def _show_sidebar_after_resize(self):
        # Deprecated logic removed
        return False

    def add_calculator_instance(self):
        self.instance_count += 1
        title = f"Calculator {self.instance_count}"
        
        # Create Widget
        calc_widget = CalculatorWidget()
        calc_widget.parent_window = self
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
        
        # Add to sidebar list via SidebarView helper (or manual construction if complex)
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
        
        self.sidebar_view.add_row(row)
        self.calculator_widgets.append(calc_widget)
        
        self.sidebar_view.select_row(row)
        
        # Add display to stack
        self.display_stack.add_named(calc_widget.get_display_widget(), name)
        
        # If this is the selected page, show it
        if self.tab_view.get_selected_page() == page:
            self.display_stack.set_visible_child_name(name)
            calc_widget.grab_focus()
        
        calc_widget.on_expression_changed = lambda text: preview_label.set_text(text or "0")

    def update_calculator_name(self, calc_widget):
        from ..backend import CalculatorLogic
        if not hasattr(calc_widget, 'logic'):
            return
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

    def on_close_calculator_clicked(self, tab_view, page):
        # Prevent recursion: DO NOT Call tab_view.close_page(page)
        # Note: at this point, page is NOT yet detached from model list? 
        # Actually 'close-page' allows checking strictness.
        # But 'page-detached' is where we should sync the sidebar.
        pass
            
    def on_close_calculator_from_sidebar(self, calc_widget):
        n_pages = self.tab_view.get_n_pages()
        for i in range(n_pages):
            page = self.tab_view.get_nth_page(i)
            if hasattr(page, 'calc_widget') and page.calc_widget is calc_widget:
                self.tab_view.close_page(page)
                break
        
        if self.tab_view.get_n_pages() == 0:
            self.add_calculator_instance()

    def on_type_dropdown_changed(self, dropdown, param):
        idx = dropdown.get_selected()
        page = self.tab_view.get_selected_page()
        if page and hasattr(page, 'calc_widget'):
            calc_widget = page.calc_widget
            if hasattr(calc_widget, 'get_stack'):
                if idx == 0:
                    calc_widget.get_stack().set_visible_child_name('standard')
                elif idx == 1:
                    calc_widget.get_stack().set_visible_child_name('scientific')

    def on_tab_page_changed(self, tab_view, param):
        page = tab_view.get_selected_page()
        if page and hasattr(page, 'calc_widget'):
            calc_widget = page.calc_widget
            if hasattr(page, 'calc_name'):
                self.display_stack.set_visible_child_name(page.calc_name)
            
            # Important: Grab focus for keyboard input!
            calc_widget.grab_focus()

    def on_sidebar_row_selected(self, box, row):
        if row is not None and hasattr(row, 'calc_widget'):
            n_pages = self.tab_view.get_n_pages()
            for i in range(n_pages):
                page = self.tab_view.get_nth_page(i)
                if hasattr(page, 'calc_widget') and page.calc_widget is row.calc_widget:
                    self.tab_view.set_selected_page(page)
