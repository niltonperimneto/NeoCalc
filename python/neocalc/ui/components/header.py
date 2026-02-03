import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GObject
from ...styling.manager import StyleManager



class HeaderView(Adw.Bin):
    """Handles the application header bar, including dropdown and menu."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.header_bar = Adw.HeaderBar()
        self.set_child(self.header_bar)
        self.setup_ui()

    def setup_ui(self):
        toggle_btn = Gtk.Button(icon_name="sidebar-show-symbolic")
        toggle_btn.set_tooltip_text(_("Toggle Sidebar"))
        toggle_btn.connect("clicked", self.main_window.on_toggle_sidebar)
        self.header_bar.pack_start(toggle_btn)

        self.setup_mode_switch()
        self.setup_menu()

    def setup_mode_switch(self):
        menu_model = Gio.Menu()
        menu_model.append(_("Standard"), "win.set_mode('standard')")
        menu_model.append(_("Scientific"), "win.set_mode('scientific')")
        menu_model.append(_("Programming"), "win.set_mode('programming')")
        menu_model.append(_("Financial"), "win.set_mode('financial')")

        self.split_button = Adw.SplitButton()
        self.split_button.set_icon_name("view-grid-symbolic")
        self.split_button.set_menu_model(menu_model)
        self.split_button.set_tooltip_text(_("Calculator Mode"))
        self.split_button.connect("clicked", self.main_window.on_split_button_clicked)
        
        # force icon only
        # self.split_button.set_label("") # SplitButton doesn't support empty label easily if it has text from action?
        # Actually SplitButton has no label property directly exposed like Button sometimes.
        # But wait, did I set a label? No, just icon_name set in init.
        
        # Pack at start for compact layout
        self.header_bar.pack_start(self.split_button)
        
        # Use empty label as title widget to hide default app title
        self.header_bar.set_title_widget(Gtk.Label(label=""))

    def set_mode_display(self, mode_id):
        icons = {
            "standard": "view-grid-symbolic",
            "scientific": "applications-science-symbolic",
            "programming": "applications-engineering-symbolic",
            "financial": "money-symbolic"
        }
        self.split_button.set_icon_name(icons.get(mode_id, "view-grid-symbolic"))

    def setup_menu(self):
        menu_model = Gio.Menu()
        menu_model.append(_("Variables"), "win.show_variables")
        menu_model.append(_("Preferences"), "win.show_preferences")
        menu_model.append(_("Keyboard Shortcuts"), "win.show_shortcuts")
        menu_model.append(_("About"), "win.about")

        menu_btn = Gtk.MenuButton()
        menu_btn.set_icon_name("open-menu-symbolic")
        menu_btn.set_menu_model(menu_model)
        self.header_bar.pack_end(menu_btn)

