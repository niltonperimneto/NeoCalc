import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from .base import CalculatorGrid

class ScientificGrid(CalculatorGrid):
    def __init__(self, calculator_window):
        super().__init__(calculator_window)
        self.set_row_homogeneous(True)
        self.set_column_homogeneous(True)

        from .base import GridButton

        buttons = [
            GridButton("(", self.on_button_clicked, 0, 0),
            GridButton(")", self.on_button_clicked, 1, 0),
            GridButton("π", self.on_button_clicked, 2, 0),
            GridButton("im", self.on_func_clicked, 3, 0), # 'im' is for complex numbers, treated as unit 'i'? No, i is separate. im(z) returns imaginary part. So it needs (.
            # Wait, line 21 says GridButton("im", self.on_func_clicked, 3, 0)
            # If "im" is a function, it needs "im(". If it's the constant 'i', it's redundant with line 30 "i".
            # backend/src/engine/functions/mod.rs: "im" | "lm" => ... complex_ops::im.
            # So it IS a function.
            GridButton("im", self.on_func_clicked, 3, 0, insert_text="im("),
            GridButton("C", self.on_clear_clicked, 4, 0, style_classes=["destructive-action", "destructive"]),
            GridButton("÷", self.on_button_clicked, 5, 0),
            GridButton("×", self.on_button_clicked, 6, 0),
            GridButton("−", self.on_button_clicked, 7, 0),

            GridButton("sin", self.on_func_clicked, 0, 1, insert_text="sin("),
            GridButton("cos", self.on_func_clicked, 1, 1, insert_text="cos("),
            GridButton("tan", self.on_func_clicked, 2, 1, insert_text="tan("),
            GridButton("i", self.on_button_clicked, 3, 1), # Constant 'i'
            GridButton("7", self.on_button_clicked, 4, 1),
            GridButton("8", self.on_button_clicked, 5, 1),
            GridButton("9", self.on_button_clicked, 6, 1),
            GridButton("+", self.on_button_clicked, 7, 1, height=2),

            GridButton("asin", self.on_func_clicked, 0, 2, insert_text="asin("),
            GridButton("acos", self.on_func_clicked, 1, 2, insert_text="acos("),
            GridButton("atan", self.on_func_clicked, 2, 2, insert_text="atan("),
            GridButton("^", self.on_button_clicked, 3, 2),
            GridButton("4", self.on_button_clicked, 4, 2),
            GridButton("5", self.on_button_clicked, 5, 2),
            GridButton("6", self.on_button_clicked, 6, 2),

            GridButton("sinh", self.on_func_clicked, 0, 3, insert_text="sinh("),
            GridButton("cosh", self.on_func_clicked, 1, 3, insert_text="cosh("),
            GridButton("tanh", self.on_func_clicked, 2, 3, insert_text="tanh("),
            GridButton("√", self.on_func_clicked, 3, 3, insert_text="sqrt("),
            GridButton("1", self.on_button_clicked, 4, 3),
            GridButton("2", self.on_button_clicked, 5, 3),
            GridButton("3", self.on_button_clicked, 6, 3),
            GridButton("=", self.on_equal_clicked, 7, 3, height=2, style_classes=["suggested-action", "accent"]),

            GridButton("log", self.on_func_clicked, 0, 4, insert_text="log("),
            GridButton("ln", self.on_func_clicked, 1, 4, insert_text="ln("),
            GridButton("abs", self.on_func_clicked, 2, 4, insert_text="abs("),
            GridButton("conj", self.on_func_clicked, 3, 4, insert_text="conj("),
            GridButton("0", self.on_button_clicked, 4, 4, width=2),
            GridButton(".", self.on_button_clicked, 6, 4),
        ]

        self.create_buttons(buttons)
