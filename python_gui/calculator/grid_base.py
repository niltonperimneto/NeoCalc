import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from .backend import CalculatorLogic

class CalculatorGrid(Gtk.Grid):
    """Base class for calculator grids handling common button actions."""
    
    def __init__(self, calculator_window, **kwargs):
        super().__init__(row_spacing=3, column_spacing=3, **kwargs)
        self.calculator = calculator_window

    def on_button_clicked(self, button):
        """Handle standard digit and operator clicks."""
        current = self.calculator.entry.get_text()
        new_text = CalculatorLogic.append_text(current, button.get_label())
        self.calculator.entry.set_text(new_text)

    def on_equal_clicked(self, button):
        """Handle evaluation."""
        expression = self.calculator.entry.get_text()
        result_text = CalculatorLogic.evaluate(expression)
        self.calculator.entry.set_text(result_text)
        
        # Update history display
        if hasattr(self.calculator, 'update_history_display'):
            self.calculator.update_history_display()
        
        # Update calculator name in sidebar
        if hasattr(self.calculator, 'trigger_name_update'):
            self.calculator.trigger_name_update()

    def on_clear_clicked(self, button):
        """Handle clear action."""
        self.calculator.entry.set_text(CalculatorLogic.clear())

    def on_func_clicked(self, button):
        """Handle scientific function clicks."""
        current = self.calculator.entry.get_text()
        new_text = CalculatorLogic.append_function(current, button.get_label())
        self.calculator.entry.set_text(new_text)
