import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GLib
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

        # Placeholder for the display
        self._display_placeholder = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._display_placeholder.add_css_class("calculator-display-header")
        calc_header.append(self._display_placeholder)

        content_box.append(calc_header)

        # 3. Tab View (Content)
        self.tab_view = Adw.TabView()
        self.tab_view.set_vexpand(True)
        self.tab_view.set_hexpand(True)
        content_box.append(self.tab_view)
        
        # Attach to View
        nav_page = Adw.NavigationPage(child=content_box, title="Calculator")
        self.split_view.set_content(nav_page)

    def switch_display_for(self, calc_widget):
        """Place the given calculator's display widget into the header placeholder."""
        if calc_widget is None:
            return
            
        display = calc_widget.get_display_widget()
        
        # Only reparent if the display is not already the child
        current_child = self._display_placeholder.get_first_child()
        if current_child is display:
            calc_widget.update_history_display()
            return
        
        # Remove existing children from placeholder
        child = self._display_placeholder.get_first_child()
        while child is not None:
            next_child = child.get_next_sibling()
            self._display_placeholder.remove(child)
            child = next_child

        # If the display is currently parented elsewhere, unparent first
        parent = display.get_parent()
        if parent is not None and parent is not self._display_placeholder:
            parent.remove(display)
        
        self._display_placeholder.append(display)

    def on_toggle_sidebar(self, button):
        current_state = self.split_view.get_show_sidebar()
        new_state = not current_state
        
        if new_state:
            # Force window to expand by setting minimum size
            # This ensures allocation is sufficient before showing sidebar
            self.set_size_request(600, 500)
            
            # Use a slightly longer timeout to let the WM handle the resize
            GLib.timeout_add(150, self._show_sidebar_after_resize)
        else:
            self.split_view.set_show_sidebar(False)
            # Shrink back
            GLib.timeout_add(100, lambda: self.set_default_size(320, 500) or False)

    def _show_sidebar_after_resize(self):
        self.split_view.set_show_sidebar(True)
        # Reset minimum size to allow resizing smaller if needed (but keep logic consistent)
        self.set_size_request(320, 400)
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
        self.switch_display_for(calc_widget)
        
        calc_widget.entry.connect("changed", lambda e: preview_label.set_text(e.get_text() or "0"))

    def update_calculator_name(self, calc_widget):
        from ..backend import CalculatorLogic
        history = CalculatorLogic.get_history()
        
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
        tab_view.close_page(page)
        if self.tab_view.get_n_pages() == 0:
            self.add_calculator_instance()
            
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
            self.switch_display_for(page.calc_widget)

    def on_sidebar_row_selected(self, box, row):
        if row is not None and hasattr(row, 'calc_widget'):
            n_pages = self.tab_view.get_n_pages()
            for i in range(n_pages):
                page = self.tab_view.get_nth_page(i)
                if hasattr(page, 'calc_widget') and page.calc_widget is row.calc_widget:
                    self.tab_view.set_selected_page(page)
                    self.switch_display_for(row.calc_widget)
                    break

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

        # Placeholder for the display
        self._display_placeholder = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self._display_placeholder.add_css_class("calculator-display-header")
        calc_header.append(self._display_placeholder)

        content_box.append(calc_header)

        # 3. Tab View (Content)
        self.tab_view = Adw.TabView()
        self.tab_view.set_vexpand(True)
        self.tab_view.set_hexpand(True)
        content_box.append(self.tab_view)
        
        # Attach to View
        nav_page = Adw.NavigationPage(child=content_box, title="Calculator")
        self.split_view.set_content(nav_page)

    def switch_display_for(self, calc_widget):
        """Place the given calculator's display widget into the header placeholder."""
        if calc_widget is None:
            return
            
        display = calc_widget.get_display_widget()
        
        # Only reparent if the display is not already the child
        current_child = self._display_placeholder.get_first_child()
        if current_child is display:
            calc_widget.update_history_display()
            return
        
        # Remove existing children from placeholder
        child = self._display_placeholder.get_first_child()
        while child is not None:
            next_child = child.get_next_sibling()
            self._display_placeholder.remove(child)
            child = next_child

        # If the display is currently parented elsewhere, unparent first
        parent = display.get_parent()
        if parent is not None and parent is not self._display_placeholder:
            parent.remove(display)
        
        self._display_placeholder.append(display)

    def on_toggle_sidebar(self, button):
        current_state = self.split_view.get_show_sidebar()
        new_state = not current_state
        
        if new_state:
            # Force window to expand by setting minimum size
            # This ensures allocation is sufficient before showing sidebar
            self.set_size_request(600, 500)
            
            # Use a slightly longer timeout to let the WM handle the resize
            GLib.timeout_add(150, self._show_sidebar_after_resize)
        else:
            self.split_view.set_show_sidebar(False)
            # Shrink back
            GLib.timeout_add(100, lambda: self.set_default_size(320, 500) or False)

    def _show_sidebar_after_resize(self):
        self.split_view.set_show_sidebar(True)
        # Reset minimum size to allow resizing smaller if needed (but keep logic consistent)
        self.set_size_request(320, 400)
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
        self.switch_display_for(calc_widget)
        
        calc_widget.entry.connect("changed", lambda e: preview_label.set_text(e.get_text() or "0"))

    def update_calculator_name(self, calc_widget):
        from ..backend import CalculatorLogic
        history = CalculatorLogic.get_history()
        
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
        tab_view.close_page(page)
        if self.tab_view.get_n_pages() == 0:
            self.add_calculator_instance()
            
    def on_close_calculator_from_sidebar(self, calc_widget):
        n_pages = self.tab_view.get_n_pages()
        for i in range(n_pages):
            page = self.tab_view.get_nth_page(i)
            if hasattr(page, 'calc_widget') and page.calc_widget is calc_widget:
                self.tab_view.close_page(page)
                break
        
        if self.tab_view.get_n_pages() == 0:
            self.add_calculator_instance()

    def setup_actions(self):
        # Actions setup remains largely similar
        actions = [
            ("new_calc", self.on_new_calculator_action, ["<Control>t"]),
            ("toggle_dark", self.on_toggle_mode_action, ["<Control>d"]),
            ("about", self.on_about_action, None),
            ("show_shortcuts", self.on_show_shortcuts, ["<Control>h"]),
            ("switch_scientific", self.on_switch_scientific, ["<Control>s"]),
            ("switch_standard", self.on_switch_standard, ["<Control>r"]),
        ]
        
        app = self.get_application()
        for name, callback, accel in actions:
            action = Gio.SimpleAction.new(name, None)
            action.connect("activate", callback)
            self.add_action(action)
            if accel and app:
                app.set_accels_for_action(f"win.{name}", accel)

        # Switch nums
        for i in range(1, 10):
            action = Gio.SimpleAction.new(f"switch_calc_{i}", None)
            action.connect("activate", self.on_switch_calculator, i)
            self.add_action(action)
            if app:
                app.set_accels_for_action(f"win.switch_calc_{i}", [f"<Alt>{i}"])

    def on_new_calculator_action(self, action, param):
        self.add_calculator_instance()

    def on_about_action(self, action, param):
        present_about_dialog(self)

    def on_show_shortcuts(self, action, param):
        from ..shortcuts import show_shortcuts_dialog
        show_shortcuts_dialog(self)

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

    def on_toggle_mode_action(self, action, param):
        if StyleManager.toggle_theme():
            print("Switched to Dark Mode")
        else:
            print("Switched to Light Mode")
            
        # Ensure connections (idempotent or check if already connected?)
        # Actually these should be connected once probably, but matching original logic:
        # Re-connecting signals might duplicate them if not careful, but original code did this.
        # Let's fix it by checking or doing it in init if possible. 
        # Actually, let's just do it cleanly in init/add_page logic, but logic was:
        try:
            self.tab_view.disconnect_by_func(self.on_tab_page_changed)
            self.tab_view.disconnect_by_func(self.on_close_calculator_clicked)
        except:
            pass
        self.tab_view.connect("notify::selected-page", self.on_tab_page_changed)
        self.tab_view.connect("close-page", self.on_close_calculator_clicked)

    def on_tab_page_changed(self, tab_view, param):
        page = tab_view.get_selected_page()
        if page and hasattr(page, 'calc_widget'):
            self.switch_display_for(page.calc_widget)

    def on_sidebar_row_selected(self, box, row):
        if row is not None and hasattr(row, 'calc_widget'):
            n_pages = self.tab_view.get_n_pages()
            for i in range(n_pages):
                page = self.tab_view.get_nth_page(i)
                if hasattr(page, 'calc_widget') and page.calc_widget is row.calc_widget:
                    self.tab_view.set_selected_page(page)
                    self.switch_display_for(row.calc_widget)
                    break

    def on_switch_scientific(self, action, param):
        self.header_view.set_selected_type(1)

    def on_switch_standard(self, action, param):
        self.header_view.set_selected_type(0)

    def on_switch_calculator(self, action, param, calc_number):
        if calc_number <= self.tab_view.get_n_pages():
            page = self.tab_view.get_nth_page(calc_number - 1)
            if page:
                self.tab_view.set_selected_page(page)
                if hasattr(page, 'calc_widget'):
                    self.switch_display_for(page.calc_widget)
