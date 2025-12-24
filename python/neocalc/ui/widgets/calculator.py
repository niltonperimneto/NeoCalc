import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, GLib, Gtk

from ...core.backend import CalculatorLogic
from ..components.display import CalculatorDisplay
from ..grids.financial import FinancialGrid
from ..grids.programming import ProgrammingGrid
from ..grids.scientific import ScientificGrid
from ..grids.standard import ButtonGrid


class CalculatorWidget(Gtk.Box):
    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0, **kwargs)

        self.parent_window = None
        self.logic = CalculatorLogic()

        self.on_expression_changed = None
        GLib.idle_add(self.update_display)

        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self.on_key_pressed)
        self.add_controller(key_controller)

        self.display = CalculatorDisplay()
        self.display.connect("user-edited", self.on_display_edited)
        self.display.connect("activated", self.on_display_activated)

        main_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        main_content.set_margin_start(8)
        main_content.set_margin_end(8)
        main_content.set_margin_top(8)
        main_content.set_margin_bottom(8)

        grid_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        grid_box.set_hexpand(True)
        grid_box.set_vexpand(True)
        main_content.append(grid_box)

        self.view_stack = Adw.ViewStack()

        from ..grids.standard import ButtonGrid

        button_grid = ButtonGrid(self)
        self.view_stack.add_titled(button_grid, "standard", "Standard")
        self.view_stack.get_page(button_grid).set_icon_name("view-grid-symbolic")

        from ..grids.scientific import ScientificGrid

        scientific_grid = ScientificGrid(self)
        self.view_stack.add_titled(scientific_grid, "scientific", "Scientific")
        self.view_stack.get_page(scientific_grid).set_icon_name(
            "applications-science-symbolic"
        )

        programming_grid = ProgrammingGrid(self)
        self.view_stack.add_titled(programming_grid, "programming", "Programming")
        self.view_stack.get_page(programming_grid).set_icon_name(
            "applications-engineering-symbolic"
        )

        financial_grid = FinancialGrid(self)
        self.view_stack.add_titled(financial_grid, "financial", "Financial")
        self.view_stack.get_page(financial_grid).set_icon_name("money-symbolic")

        grid_box.append(self.view_stack)

        self.append(main_content)
        self.set_vexpand(True)

        self.set_focusable(True)

        self.on_expression_changed = None

    def get_stack(self):
        return self.view_stack

    def get_display_widget(self):
        """Return the display widget to be placed in the header/stack."""
        self.update_history_display()
        return self.display

    def update_history_display(self):
        """Update the history label with recent calculations."""
        history = self.logic.get_history()
        self.display.set_history(history)

    def trigger_name_update(self):
        """Trigger parent window to update calculator name"""
        if self.parent_window and hasattr(self.parent_window, "update_calculator_name"):
            self.parent_window.update_calculator_name(self)

    def get_expression(self):
        return self.logic.get_buffer()

    def set_expression(self, text):
        """Called when logic updates (e.g. from buttons)"""
        self.display.set_value(text)
        if self.on_expression_changed:
            self.on_expression_changed(text)
        self.update_preview(text)

    def insert_at_cursor(self, text):
        self.display.insert_at_cursor(text)

    def backspace_at_cursor(self):
        self.display.backspace_at_cursor()

    def update_display(self):
        text = self.logic.get_buffer()
        self.display.set_value(text)
        if self.on_expression_changed:
            self.on_expression_changed(text)
        self.update_preview(text)

    def update_preview(self, text):
        """Calculate and show preview result."""
        if not text:
            self.display.set_preview("")
            return

        try:
            # Avoid preview for simple numbers
            if text.replace(".", "", 1).isdigit():
                self.display.set_preview("")
                return

            # Use the new preview method from the backend which respects variables
            result = self.logic.preview(text)

            # If result is same as input (no calc happened), hide it
            if result == text or result == "Error" or not result:
                self.display.set_preview("")
            else:
                self.display.set_preview(result)
        except Exception:
            self.display.set_preview("")

    def get_variables(self):
        """Retrieve defined variables from the backend."""
        try:
            return self.logic.get_variables()
        except Exception:
            return {}

    def on_display_edited(self, widget, text):
        self.logic.set_expression(text)
        if self.on_expression_changed:
            self.on_expression_changed(text)

    def on_display_activated(self, widget):
        ## Use non-blocking evaluation to keep UI responsive
        self.logic.evaluate_non_blocking(
            on_success=self._on_eval_success, on_error=self._on_eval_error
        )

    def _on_eval_success(self, result):
        """Called when async evaluation completes successfully."""
        self.update_display()
        self.update_history_display()
        self.trigger_name_update()

    def _on_eval_error(self, error_msg):
        """Called when async evaluation fails."""
        ## For now, just show the error in the display like the sync version did
        ## (The backend usually captures errors as strings in the buffer,
        ## but if an exception bubble up, we handle it here)
        self.display.set_value("Error")
        print(f"Evaluation error: {error_msg}")

    def on_key_pressed(self, controller, keyval, keycode, state):
        if self.display.has_focus():
            return False

        from gi.repository import Gdk

        key_char = Gdk.keyval_to_unicode(keyval)
        valid_chars = "0123456789.+-*/^%()abcdefABCDEFxb"

        if key_char:
            char = chr(key_char)
            if char in valid_chars or char.isalpha():
                self.insert_at_cursor(char)
                return True

        name = Gdk.keyval_name(keyval)

        if name == "BackSpace":
            self.backspace_at_cursor()
            return True

        elif name in ("Return", "KP_Enter", "ISO_Enter", "equal"):
            self.on_display_activated(None)
            return True

        elif name == "Escape":
            self.logic.clear()
            self.update_display()
            return True

        return False
