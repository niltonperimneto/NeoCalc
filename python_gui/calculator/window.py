import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gdk, Adw, Gio
import os

from .grid_standard import ButtonGrid
from .about import present_about_dialog
from .view import CalculatorWidget
from .styling import StyleManager



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Calculator(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("NeoCalc")
        self.set_default_size(500, 700)
        self.set_resizable(True)
        self.dark_mode = False

        # --- Setup Logic ---
        self.setup_actions()
        self.setup_layout()
        
        # --- Initialization ---
        self.instance_count = 0
        self.add_calculator_instance()
        
        # --- Styling ---
        StyleManager.load_css()

    def setup_layout(self):
        """Initializes the main window layout using OverlaySplitView."""
        self.split_view = Adw.OverlaySplitView()
        self.split_view.set_collapsed(True)
        self.set_content(self.split_view)

        # Create and Attach Sections
        self.setup_sidebar()
        self.setup_content()

    def setup_sidebar(self):
        """Constructs the sidebar with calculator list."""
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        sidebar_box.add_css_class("sidebar")
        
        # 1. Header
        sidebar_header = Adw.HeaderBar()
        sidebar_header.set_show_end_title_buttons(False)
        sidebar_header.set_show_start_title_buttons(False)
        
        # New Calculator Button (+)
        add_btn = Gtk.Button(icon_name="list-add-symbolic")
        add_btn.set_tooltip_text("New Calculator")
        add_btn.set_action_name("win.new_calc")
        sidebar_header.pack_end(add_btn)
        
        sidebar_box.append(sidebar_header)

        # 2. List
        self.sidebar_list = Gtk.ListBox()
        self.sidebar_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.sidebar_list.connect("row-selected", self.on_sidebar_row_selected)
        self.sidebar_list.set_vexpand(True)
        self.sidebar_list.add_css_class("navigation-sidebar")

        scrolled_sidebar = Gtk.ScrolledWindow()
        scrolled_sidebar.set_child(self.sidebar_list)
        scrolled_sidebar.set_vexpand(True)
        
        sidebar_box.append(scrolled_sidebar)
        
        # Attach to View
        self.split_view.set_sidebar(sidebar_box)

    def setup_content(self):
        """Constructs the main content area."""
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        # 1. Header
        header = Adw.HeaderBar()
        self.switcher_title = Adw.ViewSwitcherTitle()
        self.switcher_title.set_title("NeoCalc")
        header.set_title_widget(self.switcher_title)

        # Sidebar Toggle
        toggle_btn = Gtk.Button(icon_name="sidebar-show-symbolic")
        toggle_btn.set_tooltip_text("Toggle Sidebar")
        toggle_btn.connect("clicked", self.on_toggle_sidebar)
        header.pack_start(toggle_btn)

        # Main Menu
        menu_model = Gio.Menu()
        menu_model.append("Dark Mode", "win.toggle_dark")
        menu_model.append("About", "win.about")
        
        menu_btn = Gtk.MenuButton()
        menu_btn.set_icon_name("open-menu-symbolic")
        menu_btn.set_menu_model(menu_model)
        header.pack_end(menu_btn)
        
        content_box.append(header)

        # 2. Main Stack
        self.main_stack = Gtk.Stack()
        self.main_stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.main_stack.set_hexpand(True)
        self.main_stack.set_vexpand(True)
        content_box.append(self.main_stack)

        # Attach to View
        self.split_view.set_content(content_box)

    def on_toggle_sidebar(self, button):
        # Toggle show-sidebar
        self.split_view.set_show_sidebar(not self.split_view.get_show_sidebar())

    def add_calculator_instance(self):
        self.instance_count += 1
        title = f"Calculator {self.instance_count}"
        
        # Create Widget
        calc_widget = CalculatorWidget()
        name = f"calc_{self.instance_count}"
        self.main_stack.add_named(calc_widget, name)
        
        # Add to sidebar
        row = Gtk.ListBoxRow()
        row.add_css_class("sidebar-row")
        
        row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        label = Gtk.Label(label=title, xalign=0)
        label.set_hexpand(True)
        row_box.append(label)
        
        close_btn = Gtk.Button(icon_name="window-close-symbolic")
        close_btn.add_css_class("flat")
        close_btn.connect("clicked", self.on_close_calculator_clicked, row)
        row_box.append(close_btn)
        
        row.set_child(row_box)
        
        # Store metadata
        row.calc_name = name 
        row.calc_widget = calc_widget
        
        self.sidebar_list.append(row)
        self.sidebar_list.select_row(row)
        
        # If successfully added, maybe close sidebar if on mobile? 
        # For now, keep as is.

    def on_close_calculator_clicked(self, button, row):
        # Remove from stack
        page = self.main_stack.get_child_by_name(row.calc_name)
        if page:
            self.main_stack.remove(page)
        
        # Remove from sidebar
        self.sidebar_list.remove(row)
        
        # If list empty?
        if self.instance_count > 0:
            # Note: instance_count just keeps incrementing for unique names, 
            # checking list children count implies getting them logic 
            pass 

    def setup_actions(self):
        # New Calc
        action_new = Gio.SimpleAction.new("new_calc", None)
        action_new.connect("activate", self.on_new_calculator_action)
        self.add_action(action_new)

        # Toggle Dark
        action_dark = Gio.SimpleAction.new("toggle_dark", None)
        action_dark.connect("activate", self.on_toggle_mode_action)
        self.add_action(action_dark)

        # About
        action_about = Gio.SimpleAction.new("about", None)
        action_about.connect("activate", self.on_about_action)
        self.add_action(action_about)
        
        # Shortcuts
        app = self.get_application()
        app.set_accels_for_action("win.new_calc", ["<Control>n"])
        app.set_accels_for_action("win.toggle_dark", ["<Control>d"])

    def on_new_calculator_action(self, action, param):
        self.add_calculator_instance()

    def on_about_action(self, action, param):
        present_about_dialog(self)

    def on_toggle_mode_action(self, action, param):
        style_manager = Adw.StyleManager.get_default()
        self.dark_mode = not self.dark_mode
        style_manager.set_color_scheme(
            Adw.ColorScheme.FORCE_DARK if self.dark_mode else Adw.ColorScheme.FORCE_LIGHT
        )

    # Legacy cleanup (removing old handlers if unused, keeping sidebar logic)

    def on_sidebar_row_selected(self, box, row):
        if row is not None:
            self.main_stack.set_visible_child_name(row.calc_name)
            self.switcher_title.set_stack(row.calc_widget.get_stack())

    # Removed old button handlers

