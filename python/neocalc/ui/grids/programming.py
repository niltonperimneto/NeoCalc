import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from .base import CalculatorGrid, GridButton

class ProgrammingGrid(CalculatorGrid):
    def __init__(self, calculator_window):
        super().__init__(calculator_window)
        self.set_row_homogeneous(True)
        self.set_column_homogeneous(True)

        buttons_info = [
            # Row 0
            ("(", self.on_button_clicked, 0, 0, 1, 1),
            (")", self.on_button_clicked, 1, 0, 1, 1),
            ("bnot", self.on_func_clicked, 2, 0, 1, 1),
            ("mod", self.on_button_clicked, 3, 0, 1, 1),
            ("C", self.on_clear_clicked, 4, 0, 1, 1),
            ("÷", self.on_button_clicked, 5, 0, 1, 1),
            ("×", self.on_button_clicked, 6, 0, 1, 1),
            ("⌫", self.on_button_clicked, 7, 0, 1, 1),

            # Row 1
            ("band", self.on_func_clicked, 0, 1, 1, 1),
            ("bor", self.on_func_clicked, 1, 1, 1, 1),
            ("bxor", self.on_func_clicked, 2, 1, 1, 1),
            ("A", self.on_button_clicked, 3, 1, 1, 1),
            ("7", self.on_button_clicked, 4, 1, 1, 1),
            ("8", self.on_button_clicked, 5, 1, 1, 1),
            ("9", self.on_button_clicked, 6, 1, 1, 1),
            ("−", self.on_button_clicked, 7, 1, 1, 1),

            # Row 2
            ("lsh", self.on_func_clicked, 0, 2, 1, 1),
            ("rsh", self.on_func_clicked, 1, 2, 1, 1),
            ("rol", self.on_func_clicked, 2, 2, 1, 1),
            ("ror", self.on_func_clicked, 3, 2, 1, 1), # B is conflicting with ror position in previous, need to move B. Ah, I see B was at 4,2
            
            # Re-aligning with 8-col standard
            # Left 4 cols are funcs/Hex digits
            # Right 4 cols are numbers
            
            # Wait, Programming mode has extra hex digits A-F.
            # I will put A-F on the left side.
            
            # Row 1 (already done bitwise) -> A is at 3,1. Correct.
            
            # Row 2
            # lsh, rsh, rol, ror at 0,1,2,3
            ("4", self.on_button_clicked, 4, 2, 1, 1),
            ("5", self.on_button_clicked, 5, 2, 1, 1),
            ("6", self.on_button_clicked, 6, 2, 1, 1),
            ("+", self.on_button_clicked, 7, 2, 1, 1),

            # Row 3
            ("Hex", self.on_convert_clicked, 0, 3, 1, 1),
            ("Bin", self.on_convert_clicked, 1, 3, 1, 1),
            ("B", self.on_button_clicked, 2, 3, 1, 1),
            ("C", self.on_button_clicked, 3, 3, 1, 1),
            ("1", self.on_button_clicked, 4, 3, 1, 1),
            ("2", self.on_button_clicked, 5, 3, 1, 1),
            ("3", self.on_button_clicked, 6, 3, 1, 1),
            ("=", self.on_equal_clicked, 7, 3, 1, 2),

            # Row 4
            ("D", self.on_button_clicked, 0, 4, 1, 1),
            ("E", self.on_button_clicked, 1, 4, 1, 1),
            ("F", self.on_button_clicked, 2, 4, 1, 1),
            ("0x", self.on_button_clicked, 3, 4, 1, 1), # Little awkward but consistent
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
