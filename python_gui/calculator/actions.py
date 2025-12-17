from gi.repository import Gio
from .about import present_about_dialog
from .styling import StyleManager

class ActionRegistry:
    def __init__(self, window):
        self.window = window
        self.setup_actions()

    def setup_actions(self):
        actions = [
            ("new_calc", self.on_new_calculator_action, ["<Control>t"]),
            ("toggle_dark", self.on_toggle_mode_action, ["<Control>d"]),
            ("about", self.on_about_action, None),
            ("show_shortcuts", self.on_show_shortcuts, ["<Control>h"]),
            ("switch_scientific", self.on_switch_scientific, ["<Control>s"]),
            ("switch_standard", self.on_switch_standard, ["<Control>r"]),
        ]
        
        app = self.window.get_application()
        for name, callback, accel in actions:
            action = Gio.SimpleAction.new(name, None)
            action.connect("activate", callback)
            self.window.add_action(action)
            if accel and app:
                app.set_accels_for_action(f"win.{name}", accel)

        # Switch nums
        for i in range(1, 10):
            action = Gio.SimpleAction.new(f"switch_calc_{i}", None)
            action.connect("activate", self.on_switch_calculator, i)
            self.window.add_action(action)
            if app:
                app.set_accels_for_action(f"win.switch_calc_{i}", [f"<Alt>{i}"])

    def on_new_calculator_action(self, action, param):
        self.window.add_calculator_instance()

    def on_about_action(self, action, param):
        present_about_dialog(self.window)

    def on_show_shortcuts(self, action, param):
        from .shortcuts import show_shortcuts_dialog
        show_shortcuts_dialog(self.window)

    def on_toggle_mode_action(self, action, param):
        if StyleManager.toggle_theme():
            print("Switched to Dark Mode")
        else:
            print("Switched to Light Mode")
            
        try:
            self.window.tab_view.disconnect_by_func(self.window.on_tab_page_changed)
            self.window.tab_view.disconnect_by_func(self.window.on_close_calculator_clicked)
        except:
            pass
        self.window.tab_view.connect("notify::selected-page", self.window.on_tab_page_changed)
        self.window.tab_view.connect("close-page", self.window.on_close_calculator_clicked)

    def on_switch_scientific(self, action, param):
        self.window.header_view.set_selected_type(1)
        # We need to trigger the dropdown change to update the view
        # or we can update the dropdown which triggers the change
        # The original code just set the dropdown.
        # Let's verify what set_selected_type does in header.py.
        # It updates the dropdown selection.

    def on_switch_standard(self, action, param):
        self.window.header_view.set_selected_type(0)

    def on_switch_calculator(self, action, param, calc_number):
        if calc_number <= self.window.tab_view.get_n_pages():
            page = self.window.tab_view.get_nth_page(calc_number - 1)
            if page:
                self.window.tab_view.set_selected_page(page)
                if hasattr(page, 'calc_widget'):
                    self.window.switch_display_for(page.calc_widget)
