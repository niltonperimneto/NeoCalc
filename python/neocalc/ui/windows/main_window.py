import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GLib, Gdk
import os

from ..dialogs.about import present_about_dialog
from ..widgets.calculator import CalculatorWidget
from ...styling.manager import StyleManager
from ...core.actions import ActionRegistry
from ..components.sidebar import SidebarView
from ..components.header import HeaderView
from ...core.backend import DisplayManager, CalculatorManager

class Calculator(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("NeoCalc")
        self.set_default_size(320, 540)
        self.set_size_request(300, 500)
        self.set_resizable(True)

        # --- Setup Logic ---
        self.action_registry = ActionRegistry(self)
        self.setup_layout()
        
        # --- Managers (Rust Powered) ---
        self.display_manager = DisplayManager(self.display_stack)
        self.calc_manager = CalculatorManager(self, self.tab_view, self.sidebar_view, self.display_manager)
        
        # Connect signals for Rust manager (it delegates back to its own methods)
        self.calc_manager.setup_signals(self.calc_manager)
        # --- Shortcuts Controller (Override) ---
        self.setup_keyboard_controller()
        
        # --- Initialization ---
        self.calc_manager.add_calculator_instance()
        
        # --- Styling ---
        StyleManager.load_css()

    def setup_layout(self):
        """Initializes the main window layout using OverlaySplitView."""
        self.split_view = Adw.OverlaySplitView()
        self.split_view.set_show_sidebar(False)

        # Breakpoint for responsive sidebar (collapsed < 600px)
        breakpoint = Adw.Breakpoint.new(
            Adw.BreakpointCondition.new_length(Adw.BreakpointConditionLengthType.MAX_WIDTH, 600, Adw.LengthUnit.SP)
        )
        breakpoint.add_setter(self.split_view, "collapsed", True)
        self.add_breakpoint(breakpoint)

        self.set_content(self.split_view)

        # 1. Sidebar (Using new SidebarView)
        self.sidebar_view = SidebarView(self)
        self.split_view.set_sidebar(self.sidebar_view)
        
        # 2. Sidebar List Reference
        self.sidebar_list = self.sidebar_view.sidebar_list

        # 3. Content Area
        self.setup_content()

    def setup_content(self):
        """Constructs the main content area using Adw.ToolbarView."""
        toolbar_view = Adw.ToolbarView()
        
        # 1. Header (Using new HeaderView)
        self.header_view = HeaderView(self)
        # Add to top bars, not content
        toolbar_view.add_top_bar(self.header_view)
        # Expose type dropdown for actions to control it
        self.type_dropdown = self.header_view.type_dropdown

        # Content Box for the rest
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        # 2. Calculator Header Extension: display only
        calc_header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        calc_header.add_css_class("calculator-header-extension")
        # Critical: Display takes all available vertical space (3/4 goal)
        calc_header.set_vexpand(True)

        # Placeholder for the display - NOW A STACK
        self.display_stack = Gtk.Stack()
        self.display_stack.add_css_class("calculator-display-header")
        calc_header.append(self.display_stack)

        content_box.append(calc_header)

        # 3. Tab View (Content - The Grid)
        self.tab_view = Adw.TabView()
        # Rust backend handles: self.tab_view.connect("notify::selected-page", self.on_tab_page_changed)
        # Critical: Grid only takes what it needs (min-height ~1/4 goal)
        self.tab_view.set_vexpand(False)
        self.tab_view.set_hexpand(True)
        content_box.append(self.tab_view)
        
        # Set Content
        toolbar_view.set_content(content_box)
        
        # Attach to View
        nav_page = Adw.NavigationPage(child=toolbar_view, title="Calculator")
        self.split_view.set_content(nav_page)

    def on_toggle_sidebar(self, button):
        """Toggles the sidebar visibility, letting AdwOverlaySplitView handle the animation/mode."""
        current_state = self.split_view.get_show_sidebar()
        self.split_view.set_show_sidebar(not current_state)

    def setup_keyboard_controller(self):
        # We now rely on standard Actions for Alt+N shortcuts.
        # No manual controller needed.
        pass

    # --- Delegation to Managers (for compatibility/signaling) ---
    def add_calculator_instance(self):
        self.calc_manager.add_calculator_instance()
        
    def on_sidebar_row_selected(self, box, row):
        self.calc_manager.on_sidebar_row_selected(box, row)
        
    def update_calculator_name(self, calc_widget):
        self.calc_manager.update_calculator_name(calc_widget)
        
    def switch_display_for(self, calc_widget):
        self.display_manager.switch_display_for(calc_widget)

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
                    self.display_manager.switch_display_for(page.calc_widget)
