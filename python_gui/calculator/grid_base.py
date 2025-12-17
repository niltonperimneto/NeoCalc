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
        current = self.calculator.get_expression()
        new_text = self.calculator.logic.append_text(current, button.get_label())
        self.calculator.set_expression(new_text)

    def on_equal_clicked(self, button):
        """Handle evaluation."""
        expression = self.calculator.get_expression()
        result_text = self.calculator.logic.evaluate(expression)
        self.calculator.set_expression(result_text)
        
        # Update history display
        if hasattr(self.calculator, 'update_history_display'):
            self.calculator.update_history_display()
        
        # Update calculator name in sidebar
        if hasattr(self.calculator, 'trigger_name_update'):
            self.calculator.trigger_name_update()

    def on_clear_clicked(self, button):
        """Handle clear action."""
        self.calculator.set_expression(self.calculator.logic.clear())

    def on_func_clicked(self, button):
        """Handle scientific function clicks."""
        current = self.calculator.get_expression()
        new_text = self.calculator.logic.append_function(current, button.get_label())
        self.calculator.set_expression(new_text)
