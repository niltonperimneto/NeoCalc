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
            button.connect("clicked", callback)
            button.add_css_class("calc-grid-button")
            
            if label == "=":
                button.add_css_class("suggested-action")
            elif label == "C":
                button.add_css_class("destructive-action")
            
            # Special layout handling for operators in standard grid (Col 3)
            # This is a bit specific but safe to generalize or keep flexible
            if col == 3 and not self.get_column_homogeneous(): 
                 # Only if we are not homogeneous (Standard Grid)
                 # Check if this column is meant to be thin
                 button.set_hexpand(False)
                 button.set_size_request(70, -1)
            else:
                 button.set_hexpand(True)

            button.set_vexpand(True)
            self.attach(button, col, row, width, height)

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
