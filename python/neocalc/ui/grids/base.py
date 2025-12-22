import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk
from dataclasses import dataclass, field
from typing import Callable, List, Optional

@dataclass
class GridButton:
    label: str
    callback: Callable
    col: int
    row: int
    width: int = 1
    height: int = 1
    style_classes: List[str] = field(default_factory=list)
    insert_text: Optional[str] = None

class CalculatorGrid(Gtk.Grid):
    """Base class for calculator grids handling common button actions."""

    def __init__(self, calculator_window, **kwargs):
        super().__init__(row_spacing=3, column_spacing=3, **kwargs)
        self.calculator = calculator_window

    def create_buttons(self, buttons: List[GridButton]):
        """Creates buttons from a list of GridButton objects and attaches them to the grid."""
        for btn_def in buttons:
            button = Gtk.Button(label=btn_def.label)
            button.set_focusable(False)
            
            # Store insert_text on the button widget for callbacks to use
            button.insert_text = btn_def.insert_text if btn_def.insert_text else btn_def.label
            
            button.connect("clicked", btn_def.callback)
            
            self._apply_button_styles(button, btn_def)
            self._apply_button_layout(button)

            self.attach(button, btn_def.col, btn_def.row, btn_def.width, btn_def.height)

    def _apply_button_styles(self, button, btn_def: GridButton):
        """Applies CSS classes based on button definition."""
        button.add_css_class("calc-grid-button")
        
        # Auto-apply numeric style for digits if not specified? 
        # Standard HIG: Action buttons vs Content buttons.
        # But let's trust explicit classes first.
        
        for style in btn_def.style_classes:
            button.add_css_class(style)

    def _apply_button_layout(self, button):
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
        text = getattr(button, "insert_text", button.get_label())
        self.calculator.insert_at_cursor(text)

    def on_convert_clicked(self, button):
        """Handle base conversion."""
        label = button.get_label()
        new_val = None
        if label == "Hex":
            new_val = self.calculator.logic.convert_to_hex()
        elif label == "Bin":
            new_val = self.calculator.logic.convert_to_bin()
        
        if new_val:
            self.calculator.display.set_value(new_val)
