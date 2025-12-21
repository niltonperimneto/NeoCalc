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

        ## Initialize registry for handling user actions and shortcuts
        self.action_registry = ActionRegistry(self)
        self.register_custom_actions()
        self.setup_layout()

        ## Set up managers for display logic (what is shown) and calculation logic
        self.display_manager = DisplayManager(self.display_stack)
        self.calc_manager = CalculatorManager(self, self.tab_view, self.sidebar_view, self.display_manager)

        ## Connect the necessary signals for interaction
        self.calc_manager.setup_signals(self.calc_manager)

        self.setup_keyboard_controller()

        ## Add the first default calculator instance
        self.calc_manager.add_calculator_instance()

        ## Apply the CSS styles on startup
        StyleManager.load_css()

    def setup_layout(self):
        """Initializes the main window layout using OverlaySplitView."""
        self.split_view = Adw.OverlaySplitView()
        self.split_view.set_show_sidebar(False)

        ## Automatically collapse the sidebar if the window width is small (< 600px)
        breakpoint = Adw.Breakpoint.new(
            Adw.BreakpointCondition.new_length(Adw.BreakpointConditionLengthType.MAX_WIDTH, 600, Adw.LengthUnit.SP)
        )
        breakpoint.add_setter(self.split_view, "collapsed", True)
        self.add_breakpoint(breakpoint)

        self.set_content(self.split_view)

        ## Initialize the sidebar view and attach it to the split view
        self.sidebar_view = SidebarView(self)
        self.split_view.set_sidebar(self.sidebar_view)

        ## Keep a reference to the sidebar list box
        self.sidebar_list = self.sidebar_view.sidebar_list

        self.setup_content()

    def setup_content(self):
        """Constructs the main content area using Adw.ToolbarView."""
        toolbar_view = Adw.ToolbarView()

        ## Create and add the header bar (contains window controls and menu)
        self.header_view = HeaderView(self)

        toolbar_view.add_top_bar(self.header_view)

        ## Main container for calculator content
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        ## Container for the display area (where numbers are shown)
        calc_header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        calc_header.add_css_class("calculator-header-extension")
        ## Allow the header to expand vertically to fill space if needed
        calc_header.set_vexpand(True)

        ## Stack to switch between different calculator displays (standard/scientific)
        self.display_stack = Gtk.Stack()
        self.display_stack.add_css_class("calculator-display-header")
        calc_header.append(self.display_stack)

        content_box.append(calc_header)

        ## Tab view for handling multiple open calculator instances
        self.tab_view = Adw.TabView()
        ## Tab view should not expand vertically here as it's just the container logic
        ## But practically, this holds the keypad widget which is in the page content
        self.tab_view.set_vexpand(False)
        self.tab_view.set_hexpand(True)
        content_box.append(self.tab_view)

        ## Set the main content of the toolbar view
        toolbar_view.set_content(content_box)

        ## Wrap in a NavigationPage (required for split view content)
        nav_page = Adw.NavigationPage(child=toolbar_view, title="Calculator")
        self.split_view.set_content(nav_page)

    def on_toggle_sidebar(self, button):
        """Toggles the sidebar visibility, letting AdwOverlaySplitView handle the animation/mode."""
        current_state = self.split_view.get_show_sidebar()
        self.split_view.set_show_sidebar(not current_state)

    def setup_keyboard_controller(self):

        pass

    def add_calculator_instance(self):
        self.calc_manager.add_calculator_instance()

    def on_sidebar_row_selected(self, box, row):
        self.calc_manager.on_sidebar_row_selected(box, row)

    def update_calculator_name(self, calc_widget):
        self.calc_manager.update_calculator_name(calc_widget)

    def switch_display_for(self, calc_widget):
        self.display_manager.switch_display_for(calc_widget)

    def register_custom_actions(self):
        action = Gio.SimpleAction.new("set_mode", GLib.VariantType.new("s"))
        action.connect("activate", self.on_set_mode_action)
        self.add_action(action)

    def on_set_mode_action(self, action, param):
        mode_id = param.get_string()
        self.apply_mode(mode_id)

    def on_split_button_clicked(self, button):
        ## Toggle between 'standard' and 'scientific'
        current_page = self.tab_view.get_selected_page()
        if not current_page or not hasattr(current_page, 'calc_widget'):
            return

        calc_widget = current_page.calc_widget
        current_visible = calc_widget.get_stack().get_visible_child_name()
        
        new_mode = "scientific" if current_visible == "standard" else "standard"
        self.apply_mode(new_mode)

    def apply_mode(self, mode_id):
        page = self.tab_view.get_selected_page()
        if page and hasattr(page, 'calc_widget'):
            calc_widget = page.calc_widget
            if hasattr(calc_widget, 'get_stack'):
                calc_widget.get_stack().set_visible_child_name(mode_id)
        
        ## Update header display
        self.header_view.set_mode_display(mode_id)

    def on_switch_scientific(self, action, param):
        self.apply_mode("scientific")

    def on_switch_standard(self, action, param):
        self.apply_mode("standard")

    def on_switch_calculator(self, action, param, calc_number):
        if calc_number <= self.tab_view.get_n_pages():
            page = self.tab_view.get_nth_page(calc_number - 1)
            if page:
                self.tab_view.set_selected_page(page)
                if hasattr(page, 'calc_widget'):
                    self.display_manager.switch_display_for(page.calc_widget)
