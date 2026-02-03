import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GObject
from ...styling.manager import StyleManager

class PreferencesDialog(Adw.PreferencesWindow):
    def __init__(self, parent):
        super().__init__()
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_default_size(500, 400)
        
        self.setup_ui()
        
    def setup_ui(self):
        page = Adw.PreferencesPage()
        page.set_title(_("Appearance"))
        page.set_icon_name("preferences-desktop-appearance-symbolic")
        self.add(page)
        
        group = Adw.PreferencesGroup()
        group.set_title(_("Theme"))
        group.set_description(_("Select the visual style of the application."))
        page.add(group)
        
        ## Theme Selector
        self.theme_row = Adw.ComboRow()
        self.theme_row.set_title(_("Application Theme"))
        self.theme_row.set_icon_name("applications-graphics-symbolic")
        
        ## Populate themes
        themes = StyleManager.get_available_themes()
        model = Gtk.StringList()
        model.append(_("Default"))
        
        self.theme_map = ["default"]
        
        for theme in themes:
            model.append(theme.replace("_", " ").title())
            self.theme_map.append(theme)
            
        self.theme_row.set_model(model)
        
        ## Set current selection
        current = StyleManager.current_theme if hasattr(StyleManager, 'current_theme') else "default"
        try:
            index = self.theme_map.index(current)
            self.theme_row.set_selected(index)
        except ValueError:
            self.theme_row.set_selected(0)
            
        self.theme_row.connect("notify::selected", self.on_theme_changed)
        group.add(self.theme_row)
        
        ## Import Theme Action
        import_row = Adw.ActionRow()
        import_row.set_title(_("Import Theme"))
        import_row.set_subtitle(_("Load a custom CSS file."))
        import_row.set_activatable(True)
        import_row.connect("activated", self.on_import_clicked)
        group.add(import_row)
        
        icon = Gtk.Image(icon_name="document-open-symbolic")
        import_row.add_suffix(icon)

        ## Calculation Settings
        calc_group = Adw.PreferencesGroup()
        calc_group.set_title(_("Calculation"))
        calc_group.set_description(_("Configure calculation behavior."))
        page.add(calc_group)

        ## Decimal Mode Switch
        from ...config import ConfigManager
        self.config = ConfigManager()
        
        decimal_row = Adw.SwitchRow()
        decimal_row.set_title(_("Decimal Results"))
        decimal_row.set_subtitle(_("Show results as decimals (0.5) instead of fractions (1/2)."))
        decimal_row.set_active(self.config.get("use_decimals", False))
        decimal_row.connect("notify::active", self.on_decimal_mode_changed)
        calc_group.add(decimal_row)

    def on_theme_changed(self, row, param):
        index = row.get_selected()
        if index < len(self.theme_map):
            theme_id = self.theme_map[index]
            self.get_transient_for().set_theme(theme_id)

    def on_decimal_mode_changed(self, row, param):
        is_active = row.get_active()
        self.config.set("use_decimals", is_active)
        
        main_window = self.get_transient_for()
        if hasattr(main_window, 'tab_view'):
            n_pages = main_window.tab_view.get_n_pages()
            for i in range(n_pages):
                page = main_window.tab_view.get_nth_page(i)
                if hasattr(page, 'calc_widget'):
                    page.calc_widget.logic.set_decimal_mode(is_active)

    def on_import_clicked(self, row):
        parent = self.get_transient_for()
        if hasattr(parent, 'import_theme'):
             parent.import_theme(None, None)
