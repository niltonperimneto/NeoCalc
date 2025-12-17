import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from .grid_base import CalculatorGrid


class ScientificGrid(CalculatorGrid):
    def __init__(self, calculator_window):
        super().__init__(calculator_window)
        self.set_row_homogeneous(True)
        self.set_column_homogeneous(True)

        # Layout: 8 columns.
        # Cols 0-3: Scientific Functions (Expanded)
        # Cols 4-7: Standard Calculator Layout

        buttons_info = [
            # Row 0
            ("(", self.on_button_clicked, 0, 0, 1, 1),
            (")", self.on_button_clicked, 1, 0, 1, 1),
            ("π", self.on_button_clicked, 2, 0, 1, 1),
            ("im", self.on_func_clicked, 3, 0, 1, 1),
            ("C", self.on_clear_clicked, 4, 0, 1, 1),
            ("÷", self.on_button_clicked, 5, 0, 1, 1),
            ("×", self.on_button_clicked, 6, 0, 1, 1),
            ("−", self.on_button_clicked, 7, 0, 1, 1),
            
            # Row 1
            ("sin", self.on_func_clicked, 0, 1, 1, 1),
            ("cos", self.on_func_clicked, 1, 1, 1, 1),
            ("tan", self.on_func_clicked, 2, 1, 1, 1),
            ("i", self.on_button_clicked, 3, 1, 1, 1),
            ("7", self.on_button_clicked, 4, 1, 1, 1),
            ("8", self.on_button_clicked, 5, 1, 1, 1),
            ("9", self.on_button_clicked, 6, 1, 1, 1),
            ("+", self.on_button_clicked, 7, 1, 1, 2),  # Tall +

            # Row 2
            ("asin", self.on_func_clicked, 0, 2, 1, 1),
            ("acos", self.on_func_clicked, 1, 2, 1, 1),
            ("atan", self.on_func_clicked, 2, 2, 1, 1),
            ("^", self.on_button_clicked, 3, 2, 1, 1),
            ("4", self.on_button_clicked, 4, 2, 1, 1),
            ("5", self.on_button_clicked, 5, 2, 1, 1),
            ("6", self.on_button_clicked, 6, 2, 1, 1),
            
            # Row 3
            ("sinh", self.on_func_clicked, 0, 3, 1, 1),
            ("cosh", self.on_func_clicked, 1, 3, 1, 1),
            ("tanh", self.on_func_clicked, 2, 3, 1, 1),
            ("√", self.on_func_clicked, 3, 3, 1, 1),
            ("1", self.on_button_clicked, 4, 3, 1, 1),
            ("2", self.on_button_clicked, 5, 3, 1, 1),
            ("3", self.on_button_clicked, 6, 3, 1, 1),
            ("=", self.on_equal_clicked, 7, 3, 1, 2),  # Tall =

            # Row 4
            ("log", self.on_func_clicked, 0, 4, 1, 1),
            ("ln", self.on_func_clicked, 1, 4, 1, 1),
            ("abs", self.on_func_clicked, 2, 4, 1, 1),
            ("conj", self.on_func_clicked, 3, 4, 1, 1),
            ("0", self.on_button_clicked, 4, 4, 2, 1),  # Wide 0 matches standard 200% width of singe col? No, 2 cols.
            (".", self.on_button_clicked, 6, 4, 1, 1),
        ]

        for label, callback, col, row, width, height in buttons_info:
            button = Gtk.Button(label=label)
            button.connect("clicked", callback)
            button.add_css_class("calc-grid-button")
            if label == "=":
                button.add_css_class("suggested-action")
            elif label == "C":
                button.add_css_class("destructive-action")
            
            # Layout optimization: Scientific side might need styling distinction?
            # For now, just homogeneous grid.
            button.set_hexpand(True)
            button.set_vexpand(True)
            self.attach(button, col, row, width, height)

