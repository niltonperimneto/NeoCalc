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
        menu_model.append(_("Programming"), "win.set_mode('programming')")
        menu_model.append(_("Financial"), "win.set_mode('financial')")

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
        elif mode_id == "programming":
            self.split_button.set_label(_("Programming Mode"))
            self.split_button.set_icon_name("applications-engineering-symbolic")
        elif mode_id == "financial":
            self.split_button.set_label(_("Financial Mode"))
            self.split_button.set_icon_name("money-symbolic")

    def setup_menu(self):
        menu_model = Gio.Menu()

        menu_model.append(_("Preferences"), "win.show_preferences")
        menu_model.append(_("Keyboard Shortcuts"), "win.show_shortcuts")
        menu_model.append(_("About"), "win.about")

        menu_btn = Gtk.MenuButton()
        menu_btn.set_icon_name("open-menu-symbolic")
        menu_btn.set_menu_model(menu_model)
        menu_btn.add_css_class("header-btn")
        self.header_bar.pack_end(menu_btn)

        self.setup_variables_button()

    def setup_variables_button(self):
        self.vars_popover = Gtk.Popover()
        self.vars_list = Gtk.ListBox()
        self.vars_list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.vars_list.add_css_class("rich-list")
        
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_min_content_height(150)
        scroll.set_min_content_width(200)
        scroll.set_child(self.vars_list)
        
        self.vars_popover.set_child(scroll)
        self.vars_popover.connect("notify::visible", self.on_popover_visibility_changed)
        
        vars_btn = Gtk.MenuButton(icon_name="x-office-spreadsheet-symbolic")
        vars_btn.set_tooltip_text(_("Variables"))
        vars_btn.set_popover(self.vars_popover)
        vars_btn.add_css_class("header-btn")
        
        self.header_bar.pack_end(vars_btn)

    def on_popover_visibility_changed(self, popover, param):
        if popover.get_visible():
            self.refresh_variables()

    def refresh_variables(self):
        """Populate variables list."""
        ## Clear list
        while True:
            child = self.vars_list.get_first_child()
            if not child: break
            self.vars_list.remove(child)

        ## Get active calculator
        page = self.main_window.tab_view.get_selected_page()
        if not page or not hasattr(page, 'calc_widget'):
            self._add_placeholder(_("No active calculator"))
            return

        calc_widget = page.calc_widget
        variables = calc_widget.get_variables()

        if not variables:
            self._add_placeholder(_("No variables defined"))
            return

        for name, value in sorted(variables.items()):
            row = Gtk.ListBoxRow()
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            box.set_margin_start(12)
            box.set_margin_end(12)
            box.set_margin_top(8)
            box.set_margin_bottom(8)

            name_lbl = Gtk.Label(label=name)
            name_lbl.add_css_class("heading")
            name_lbl.set_hexpand(True)
            name_lbl.set_xalign(0)

            val_lbl = Gtk.Label(label=value)
            val_lbl.add_css_class("dim-label")
            val_lbl.set_xalign(1)

            box.append(name_lbl)
            box.append(val_lbl)
            row.set_child(box)
            self.vars_list.append(row)

    def _add_placeholder(self, text):
        row = Gtk.ListBoxRow()
        lbl = Gtk.Label(label=text)
        lbl.set_margin_top(12)
        lbl.set_margin_bottom(12)
        lbl.add_css_class("dim-label")
        row.set_child(lbl)
        self.vars_list.append(row)


