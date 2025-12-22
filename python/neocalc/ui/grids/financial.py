import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from .base import CalculatorGrid, GridButton

class FinancialGrid(CalculatorGrid):
    def __init__(self, calculator_window):
        super().__init__(calculator_window)
        self.set_row_homogeneous(True)
        self.set_column_homogeneous(True)

        from .base import GridButton

        buttons = [
            # Row 0
            GridButton("(", self.on_button_clicked, 0, 0),
            GridButton(")", self.on_button_clicked, 1, 0),
            GridButton("%", self.on_button_clicked, 2, 0),
            # CF is removed as per instruction comments.
            
            GridButton("C", self.on_clear_clicked, 4, 0, style_classes=["destructive-action", "destructive"]),
            GridButton("÷", self.on_button_clicked, 5, 0),
            GridButton("×", self.on_button_clicked, 6, 0),
            GridButton("⌫", self.on_button_clicked, 7, 0),

            # Row 1
            GridButton("fv", self.on_func_clicked, 0, 1, insert_text="fv("),
            GridButton("pv", self.on_func_clicked, 1, 1, insert_text="pv("),
            GridButton("pmt", self.on_func_clicked, 2, 1, insert_text="pmt("),
            GridButton("nper", self.on_func_clicked, 3, 1, insert_text="nper("),
            GridButton("7", self.on_button_clicked, 4, 1),
            GridButton("8", self.on_button_clicked, 5, 1),
            GridButton("9", self.on_button_clicked, 6, 1),
            GridButton("−", self.on_button_clicked, 7, 1),

            # Row 2
            GridButton("rate", self.on_func_clicked, 0, 2, insert_text="rate("),
            GridButton("npv", self.on_func_clicked, 1, 2, insert_text="npv("),
            GridButton("irr", self.on_func_clicked, 2, 2, insert_text="irr("),
            # Col 3 Row 2 was "db" placeholder. Removing it as not implemented.
            
            GridButton("4", self.on_button_clicked, 4, 2),
            GridButton("5", self.on_button_clicked, 5, 2),
            GridButton("6", self.on_button_clicked, 6, 2),
            GridButton("+", self.on_button_clicked, 7, 2),

            # Row 3
            # Col 0-3 Row 3 empty
            GridButton("1", self.on_button_clicked, 4, 3),
            GridButton("2", self.on_button_clicked, 5, 3),
            GridButton("3", self.on_button_clicked, 6, 3),
            GridButton("=", self.on_equal_clicked, 7, 3, height=2, style_classes=["suggested-action", "accent"]),

            # Row 4
            # Col 0-3 Row 4 empty
            GridButton("0", self.on_button_clicked, 4, 4, width=2),
            GridButton(".", self.on_button_clicked, 6, 4),
        ]

        self.create_buttons(buttons)
