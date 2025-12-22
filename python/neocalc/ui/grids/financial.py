import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from .base import CalculatorGrid, GridButton

class FinancialGrid(CalculatorGrid):
    def __init__(self, calculator_window):
        super().__init__(calculator_window)
        self.set_row_homogeneous(True)
        self.set_column_homogeneous(True)

        buttons_info = [
            # Row 0
            # Row 0
            ("(", self.on_button_clicked, 0, 0, 1, 1),
            (")", self.on_button_clicked, 1, 0, 1, 1),
            ("%", self.on_button_clicked, 2, 0, 1, 1),
            ("", None, 3, 0, 1, 1),
            ("C", self.on_clear_clicked, 4, 0, 1, 1),
            ("÷", self.on_button_clicked, 5, 0, 1, 1),
            ("×", self.on_button_clicked, 6, 0, 1, 1),
            ("⌫", self.on_button_clicked, 7, 0, 1, 1),

            # Row 1
            ("fv", self.on_func_clicked, 0, 1, 1, 1),
            ("pv", self.on_func_clicked, 1, 1, 1, 1),
            ("", None, 2, 1, 1, 1),
            ("", None, 3, 1, 1, 1),
            ("7", self.on_button_clicked, 4, 1, 1, 1),
            ("8", self.on_button_clicked, 5, 1, 1, 1),
            ("9", self.on_button_clicked, 6, 1, 1, 1),
            ("−", self.on_button_clicked, 7, 1, 1, 1),

            # Row 2
            ("", None, 0, 2, 1, 1),
            ("", None, 1, 2, 1, 1),
            ("", None, 2, 2, 1, 1),
            ("", None, 3, 2, 1, 1),
            ("4", self.on_button_clicked, 4, 2, 1, 1),
            ("5", self.on_button_clicked, 5, 2, 1, 1),
            ("6", self.on_button_clicked, 6, 2, 1, 1),
            ("+", self.on_button_clicked, 7, 2, 1, 1),

            # Row 3
            ("", None, 0, 3, 1, 1),
            ("", None, 1, 3, 1, 1),
            ("", None, 2, 3, 1, 1),
            ("", None, 3, 3, 1, 1),
            ("1", self.on_button_clicked, 4, 3, 1, 1),
            ("2", self.on_button_clicked, 5, 3, 1, 1),
            ("3", self.on_button_clicked, 6, 3, 1, 1),
            ("=", self.on_equal_clicked, 7, 3, 1, 2),

            # Row 4
            ("", None, 0, 4, 1, 1),
            ("", None, 1, 4, 1, 1),
            ("", None, 2, 4, 1, 1),
            ("", None, 3, 4, 1, 1),
            ("0", self.on_button_clicked, 4, 4, 2, 1),
            (".", self.on_button_clicked, 6, 4, 1, 1),
        ]

        # Filter out None callbacks
        buttons_info = [b for b in buttons_info if b[1] is not None]

        # Convert tuples to GridButton objects
        buttons = [
            GridButton(
                label=b[0],
                callback=b[1],
                col=b[2],
                row=b[3],
                width=b[4],
                height=b[5],
                style_classes=["numeric"] if b[0].isdigit() else ["function"]
            )
            for b in buttons_info
        ]

        self.create_buttons(buttons)
