import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class CalculatorGrid(Gtk.Grid):
    """Base class for calculator grids handling common button actions."""
    
    def __init__(self, calculator_window, **kwargs):
        super().__init__(row_spacing=3, column_spacing=3, **kwargs)
        self.calculator = calculator_window

    def on_button_clicked(self, button):
        """Handle standard digit and operator clicks."""
        if self.calculator.logic:
             self.calculator.logic.input(button.get_label())
             self.calculator.update_display()
        else:
             # Fallback (shouldn't happen)
             pass

    def on_equal_clicked(self, button):
        """Handle evaluation."""
        if self.calculator.logic:
             self.calculator.logic.evaluate()
             self.calculator.update_display()
        
        # Update history display
        if hasattr(self.calculator, 'update_history_display'):
            self.calculator.update_history_display()
        
        # Update calculator name in sidebar
        if hasattr(self.calculator, 'trigger_name_update'):
            self.calculator.trigger_name_update()

    def on_clear_clicked(self, button):
        """Handle clear action."""
        if self.calculator.logic:
             self.calculator.logic.clear()
             self.calculator.update_display()

    def on_func_clicked(self, button):
        """Handle scientific function clicks."""
        if self.calculator.logic:
             self.calculator.logic.input(button.get_label())
             self.calculator.update_display()
