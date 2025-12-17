import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from .grid_base import CalculatorGrid


class ButtonGrid(CalculatorGrid):
    def __init__(self, calculator_window):
        super().__init__(calculator_window)
        self.set_row_homogeneous(False)  # Allow tall buttons like scientific grid
        self.set_column_homogeneous(False)  # Columns 0-2 wide, Col 3 thin

        # Match scientific grid: tall + and = buttons, wide 0 button
        buttons_info = [
            # Row 0
            ("C", self.on_clear_clicked, 0, 0, 1, 1),
            ("÷", self.on_button_clicked, 1, 0, 1, 1),
            ("×", self.on_button_clicked, 2, 0, 1, 1),
            ("−", self.on_button_clicked, 3, 0, 1, 1),
            # Row 1
            ("7", self.on_button_clicked, 0, 1, 1, 1),
            ("8", self.on_button_clicked, 1, 1, 1, 1),
            ("9", self.on_button_clicked, 2, 1, 1, 1),
            ("+", self.on_button_clicked, 3, 1, 1, 2),  # Tall + (rows 1-2)
            # Row 2
            ("4", self.on_button_clicked, 0, 2, 1, 1),
            ("5", self.on_button_clicked, 1, 2, 1, 1),
            ("6", self.on_button_clicked, 2, 2, 1, 1),
            # Row 3
            ("1", self.on_button_clicked, 0, 3, 1, 1),
            ("2", self.on_button_clicked, 1, 3, 1, 1),
            ("3", self.on_button_clicked, 2, 3, 1, 1),
            ("=", self.on_equal_clicked, 3, 3, 1, 2),  # Tall = (rows 3-4)
            # Row 4
            ("0", self.on_button_clicked, 0, 4, 2, 1),  # Wide 0 (cols 0-1)
            (".", self.on_button_clicked, 2, 4, 1, 1),
        ]

        for label, callback, col, row, width, height in buttons_info:
            button = Gtk.Button(label=label)
            button.connect("clicked", callback)
            button.add_css_class("calc-grid-button")
            
            if label == "=":
                button.add_css_class("suggested-action")
            elif label == "C":
                button.add_css_class("destructive-action")
            
            # Layout Sizing:
            # Columns 0, 1, 2 (Numbers) -> Expand to fill space (Wide)
            # Column 3 (Operators -, +, =) -> Don't expand, fixed width (Thin)
            if col == 3:
                button.set_hexpand(False)
                button.set_size_request(70, -1) # Fixed width for operators (approx scientific width)
            else:
                button.set_hexpand(True)
            
            button.set_vexpand(True)
            self.attach(button, col, row, width, height)

