import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

class SidebarView(Adw.NavigationPage):
    """Handles the sidebar visualization and interaction logic."""
    
    def __init__(self, main_window):
        # We wrap the content in a ToolbarView inside the NavigationPage
        super().__init__(title="Calculators")
        self.main_window = main_window
        self.set_size_request(280, -1)
        self.setup_ui()
        
    def setup_ui(self):
        toolbar_view = Adw.ToolbarView()
        
        # Header for sidebar
        sidebar_header = Adw.HeaderBar()
        sidebar_header.set_show_end_title_buttons(False)
        sidebar_header.set_show_start_title_buttons(False)
        
        # Add button in sidebar header
        add_btn = Gtk.Button(icon_name="list-add-symbolic")
        add_btn.set_tooltip_text("New Calculator")
        add_btn.connect("clicked", lambda b: self.main_window.add_calculator_instance())
        sidebar_header.pack_end(add_btn)
        
        toolbar_view.add_top_bar(sidebar_header)
        
        # Create a ListBox for sidebar calculator list
        self.sidebar_list = Gtk.ListBox()
        self.sidebar_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.sidebar_list.add_css_class("sidebar-list")
        self.sidebar_list.connect("row-selected", self.main_window.on_sidebar_row_selected)
        
        # Wrap in scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_child(self.sidebar_list)
        scrolled.set_vexpand(True)
        
        toolbar_view.set_content(scrolled)
        self.set_child(toolbar_view)

    def add_row(self, row):
        """Add a row to the sidebar list."""
        self.sidebar_list.append(row)
        
    def select_row(self, row):
        """Select a specific row."""
        self.sidebar_list.select_row(row)
        
    def get_first_row(self):
        return self.sidebar_list.get_first_child()
