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
        toggle_btn.add_css_class("header-btn")
        self.header_bar.pack_start(toggle_btn)

        self.setup_mode_switch()

        self.setup_menu()

    def setup_mode_switch(self):
        menu_model = Gio.Menu()
        menu_model.append(_("Standard"), "win.set_mode('standard')")
        menu_model.append(_("Scientific"), "win.set_mode('scientific')")

        self.split_button = Adw.SplitButton(label=_("Standard Mode"))
        self.split_button.set_icon_name("view-grid-symbolic")
        self.split_button.set_menu_model(menu_model)
        self.split_button.set_tooltip_text(_("Toggle Calculator Mode"))
        
        self.split_button.connect("clicked", self.main_window.on_split_button_clicked)
        
        self.header_bar.set_title_widget(self.split_button)

    def set_mode_display(self, mode_id):
        if mode_id == "standard":
            self.split_button.set_label(_("Standard Mode"))
            self.split_button.set_icon_name("view-grid-symbolic")
        elif mode_id == "scientific":
            self.split_button.set_label(_("Scientific Mode"))
            self.split_button.set_icon_name("applications-science-symbolic")

    def setup_menu(self):
        menu_model = Gio.Menu()

        themes_menu = Gio.Menu()

        themes_menu.append(_("Default"), "win.set_theme('default')")

        for theme_name in StyleManager.get_available_themes():

            display_name = theme_name.replace("_", " ").title()
            themes_menu.append(display_name, f"win.set_theme('{theme_name}')")

        themes_menu.append(_("Import Theme..."), "win.import_theme")

        menu_model.append_submenu(_("Themes"), themes_menu)

        menu_model.append(_("Keyboard Shortcuts"), "win.show_shortcuts")
        menu_model.append(_("About"), "win.about")

        menu_btn = Gtk.MenuButton()
        menu_btn.set_icon_name("open-menu-symbolic")
        menu_btn.set_menu_model(menu_model)
        menu_btn.add_css_class("header-btn")
        self.header_bar.pack_end(menu_btn)


