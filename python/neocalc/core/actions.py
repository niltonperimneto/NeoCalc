from gi.repository import Gio, GLib
from ..ui.dialogs.about import present_about_dialog
from ..styling.manager import StyleManager

class ActionRegistry:
    def __init__(self, window):
        ## Initialize the registry with the main window reference
        self.window = window
        ## Set up all application actions and shortcuts
        self.setup_actions()

    def setup_actions(self):
        ## Define list of actions: name, callback, and optional keyboard shortcut
        actions = [
            ("new_calc", self.on_new_calculator_action, ["<Control>t"]),
            ("toggle_dark", self.on_toggle_mode_action, ["<Control>d"]),
            ("about", self.on_about_action, None),
            ("show_shortcuts", self.on_show_shortcuts, ["<Control>h"]),
            ("switch_scientific", self.on_switch_scientific, ["<Control>s"]),
            ("switch_standard", self.on_switch_standard, ["<Control>r"]),
            ("switch_programming", self.on_switch_programming, ["<Control>p"]),
            ("switch_financial", self.on_switch_financial, ["<Control>f"]),
        ]

        ## Register each action with the window and set accelerators if app is present
        app = self.window.get_application()
        for name, callback, accel in actions:
            action = Gio.SimpleAction.new(name, None)
            action.connect("activate", callback)
            self.window.add_action(action)
            if accel and app:
                app.set_accels_for_action(f"win.{name}", accel)

        ## Create actions for switching tabs using Alt+Number
        for i in range(1, 10):
            action = Gio.SimpleAction.new(f"switch_calc_{i}", None)
            action.connect("activate", self.on_switch_calculator, i)
            self.window.add_action(action)
            if app:
                app.set_accels_for_action(f"win.switch_calc_{i}", [f"<Alt>{i}"])

        ## Action to import a theme from a file
        action_import = Gio.SimpleAction.new("import_theme", None)
        action_import.connect("activate", self.on_import_theme)
        self.window.add_action(action_import)

        ## Action to apply a specific theme by name
        action_set_theme = Gio.SimpleAction.new("set_theme", GLib.VariantType.new("s"))
        action_set_theme.connect("activate", self.on_set_theme)
        self.window.add_action(action_set_theme)

    def on_new_calculator_action(self, action, param):
        self.window.add_calculator_instance()

    def on_about_action(self, action, param):
        present_about_dialog(self.window)

    def on_show_shortcuts(self, action, param):
        from ..ui.dialogs.shortcuts import show_shortcuts_dialog
        show_shortcuts_dialog(self.window)

    def on_toggle_mode_action(self, action, param):
        ## Toggle the theme and handle result (implementation deferred in styling manager)
        if StyleManager.toggle_theme():
            pass
        else:
            pass

        ## Re-attach signals if needed after theme toggle (workaround for potential signal loss)
        try:
            self.window.tab_view.disconnect_by_func(self.window.calc_manager.on_tab_page_changed)
            self.window.tab_view.disconnect_by_func(self.window.calc_manager.on_close_calculator_clicked)
        except:
            pass
        self.window.tab_view.connect("notify::selected-page", self.window.calc_manager.on_tab_page_changed)
        self.window.tab_view.connect("close-page", self.window.calc_manager.on_close_calculator_clicked)

    def on_switch_scientific(self, action, param):
        self.window.apply_mode("scientific")

    def on_switch_standard(self, action, param):
        self.window.apply_mode("standard")

    def on_switch_programming(self, action, param):
        self.window.apply_mode("programming")

    def on_switch_financial(self, action, param):
        self.window.apply_mode("financial")

    def on_switch_calculator(self, action, param, calc_number):
        ## Switch to the Nth calculator tab if it exists
        if calc_number <= self.window.tab_view.get_n_pages():
            page = self.window.tab_view.get_nth_page(calc_number - 1)
            if page:
                self.window.tab_view.set_selected_page(page)
            ## Ensure the display is updated for the new active calculator
            if hasattr(page, 'calc_widget'):
                    self.window.switch_display_for(page.calc_widget)

    def on_import_theme(self, action, param):
        StyleManager.import_theme(self.window)

    def on_set_theme(self, action, param):
        ## Apply the selected theme, or revert to default if specified
        theme_name = param.get_string()
        if theme_name == "default":
            StyleManager.load_css(None)
        else:
            StyleManager.load_css(theme_name)
