import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

class CalculatorGrid(Gtk.Grid):
    """Base class for calculator grids handling common button actions."""

    def __init__(self, calculator_window, **kwargs):
        super().__init__(row_spacing=3, column_spacing=3, **kwargs)
        self.calculator = calculator_window

    def create_buttons(self, buttons_info):
        """Creates buttons from a list of tuples and attaches them to the grid."""
        for label, callback, col, row, width, height in buttons_info:
            button = Gtk.Button(label=label)
            button.set_focusable(False)
            button.connect("clicked", callback)
            self._apply_button_styles(button, label)
            self._apply_button_layout(button, col)

            self.attach(button, col, row, width, height)

    def _apply_button_styles(self, button, label):
        """Applies CSS classes based on button label/type."""
        button.add_css_class("calc-grid-button")
        if label == "=":
            button.add_css_class("suggested-action")
            button.add_css_class("accent")
        elif label in ("C", "AC", "Delete", "⌫"):
            button.add_css_class("destructive-action")
            button.add_css_class("destructive")

    def _apply_button_layout(self, button, col):
        """Configures button expansion and sizing."""

        button.set_hexpand(True)
        button.set_vexpand(True)

    def on_button_clicked(self, button):
        """Handle standard digit and operator clicks."""
        self.calculator.insert_at_cursor(button.get_label())

    def on_equal_clicked(self, button):
        """Handle evaluation."""
        if self.calculator.logic:
             self.calculator.logic.evaluate()
             self.calculator.update_display()

        if hasattr(self.calculator, 'update_history_display'):
            self.calculator.update_history_display()

        if hasattr(self.calculator, 'trigger_name_update'):
            self.calculator.trigger_name_update()

    def on_clear_clicked(self, button):
        """Handle clear action."""
        if self.calculator.logic:
             self.calculator.logic.clear()
             self.calculator.update_display()

    def on_func_clicked(self, button):
        """Handle scientific function clicks."""
        self.calculator.insert_at_cursor(button.get_label())
