import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GLib, Gdk
import os

from ..dialogs.about import present_about_dialog
from ...styling.manager import StyleManager
from ...core.actions import ActionRegistry
from ..components.sidebar import SidebarView
from ..components.header import HeaderView
from ...core.backend import DisplayManager, CalculatorManager
from ..dialogs.preferences import PreferencesDialog

class Calculator(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("NeoCalc")
        self.set_default_size(300, 480)
        self.set_size_request(260, 380)
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
        """Initializes the main window layout without split view for now."""
        # Create a simple box to hold sidebar and content
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.set_content(self.main_box)
        
        ## Initialize the sidebar view (hidden by default)
        self.sidebar_view = SidebarView(self)
        self.sidebar_view.set_visible(False)
        self.main_box.append(self.sidebar_view)

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
        content_box.set_hexpand(True)
        content_box.set_vexpand(True)

        ## Container for the display area (where numbers are shown)
        calc_header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        calc_header.add_css_class("calculator-header-extension")
        calc_header.set_vexpand(True)

        ## Stack to switch between different calculator displays (standard/scientific)
        self.display_stack = Gtk.Stack()
        self.display_stack.add_css_class("calculator-display-header")
        calc_header.append(self.display_stack)

        content_box.append(calc_header)

        ## Tab view for handling multiple open calculator instances
        self.tab_view = Adw.TabView()
        self.tab_view.set_vexpand(True)
        self.tab_view.set_hexpand(True)
        content_box.append(self.tab_view)

        ## Set the main content of the toolbar view
        toolbar_view.set_content(content_box)

        ## Add to main box
        self.main_box.append(toolbar_view)

    def on_toggle_sidebar(self, button):
        """Toggles the sidebar visibility."""
        current_visible = self.sidebar_view.get_visible()
        self.sidebar_view.set_visible(not current_visible)

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
        
        pref_action = Gio.SimpleAction.new("show_preferences", None)
        pref_action.connect("activate", self.show_preferences)
        self.add_action(pref_action)
        
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.about)
        self.add_action(about_action)

        theme_action = Gio.SimpleAction.new("set_theme", GLib.VariantType.new("s"))
        theme_action.connect("activate", self.on_set_theme_action)
        self.add_action(theme_action)

        import_action = Gio.SimpleAction.new("import_theme", None)
        import_action.connect("activate", self.import_theme)
        self.add_action(import_action)

        shortcuts_action = Gio.SimpleAction.new("show_shortcuts", None)
        shortcuts_action.connect("activate", self.show_shortcuts)
        self.add_action(shortcuts_action)

        vars_action = Gio.SimpleAction.new("show_variables", None)
        vars_action.connect("activate", self.show_variables)
        self.add_action(vars_action)

    def show_preferences(self, action, param):
        dialog = PreferencesDialog(self)
        dialog.present()

    def about(self, action, param):
        present_about_dialog(self)

    def show_shortcuts(self, action, param):
        from ..dialogs.shortcuts import show_shortcuts_dialog
        show_shortcuts_dialog(self)

    def show_variables(self, action, param):
        """Show variables dialog."""
        page = self.tab_view.get_selected_page()
        if not page or not hasattr(page, 'calc_widget'):
            return
        
        from ..dialogs.variables import VariablesDialog
        dialog = VariablesDialog(self, page.calc_widget)
        dialog.present()

    def on_set_theme_action(self, action, param):
        theme_id = param.get_string()
        self.set_theme(theme_id)

    def set_theme(self, theme_id):
        StyleManager.apply_theme(theme_id)

    def import_theme(self, action, param):
        ## TODO: Implement file chooser
        pass

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
