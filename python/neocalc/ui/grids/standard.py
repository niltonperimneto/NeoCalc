import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from .base import CalculatorGrid

class ButtonGrid(CalculatorGrid):
    def __init__(self, calculator_window):
        super().__init__(calculator_window)
        self.set_row_homogeneous(False)
        self.set_column_homogeneous(False)

        from .base import GridButton

        buttons = [
            GridButton("C", self.on_clear_clicked, 0, 0, style_classes=["destructive-action", "destructive"]),
            GridButton("÷", self.on_button_clicked, 1, 0),
            GridButton("×", self.on_button_clicked, 2, 0),
            GridButton("−", self.on_button_clicked, 3, 0),

            GridButton("7", self.on_button_clicked, 0, 1),
            GridButton("8", self.on_button_clicked, 1, 1),
            GridButton("9", self.on_button_clicked, 2, 1),
            GridButton("+", self.on_button_clicked, 3, 1, height=2),

            GridButton("4", self.on_button_clicked, 0, 2),
            GridButton("5", self.on_button_clicked, 1, 2),
            GridButton("6", self.on_button_clicked, 2, 2),

            GridButton("1", self.on_button_clicked, 0, 3),
            GridButton("2", self.on_button_clicked, 1, 3),
            GridButton("3", self.on_button_clicked, 2, 3),
            GridButton("=", self.on_equal_clicked, 3, 3, height=2, style_classes=["suggested-action", "accent"]),

            GridButton("0", self.on_button_clicked, 0, 4, width=2),
            GridButton(".", self.on_button_clicked, 2, 4),
        ]

        self.create_buttons(buttons)
