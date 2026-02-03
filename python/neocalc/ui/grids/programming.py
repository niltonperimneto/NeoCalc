# -*- coding: utf-8 -*-
from .base import CalculatorGrid, GridButton


class ProgrammingGrid(CalculatorGrid):
    def __init__(self, calculator_window):
        super().__init__(calculator_window)

        buttons = [
            # Row 0
            GridButton("(", self.on_button_clicked, 0, 0),
            GridButton(")", self.on_button_clicked, 1, 0),
            GridButton("bnot", self.on_func_clicked, 2, 0, insert_text="bnot("),
            GridButton("mod", self.on_button_clicked, 3, 0, insert_text="%"),
            GridButton(
                "C",
                self.on_clear_clicked,
                4,
                0,
                style_classes=["destructive-action", "destructive"],
            ),
            GridButton("÷", self.on_button_clicked, 5, 0),
            GridButton("×", self.on_button_clicked, 6, 0),
            GridButton("⌫", self.on_backspace_clicked, 7, 0, style_classes=["destructive-action", "destructive"]),

            # Row 1
            GridButton("band", self.on_func_clicked, 0, 1, insert_text="band("),
            GridButton("bor", self.on_func_clicked, 1, 1, insert_text="bor("),
            GridButton("bxor", self.on_func_clicked, 2, 1, insert_text="bxor("),
            GridButton("A", self.on_button_clicked, 3, 1),
            GridButton("7", self.on_button_clicked, 4, 1),
            GridButton("8", self.on_button_clicked, 5, 1),
            GridButton("9", self.on_button_clicked, 6, 1),
            GridButton("−", self.on_button_clicked, 7, 1),
            # Row 2
            GridButton("lsh", self.on_func_clicked, 0, 2, insert_text="lsh("),
            GridButton("rsh", self.on_func_clicked, 1, 2, insert_text="rsh("),
            GridButton("rol", self.on_func_clicked, 2, 2, insert_text="rol("),
            GridButton("ror", self.on_func_clicked, 3, 2, insert_text="ror("),
            GridButton("4", self.on_button_clicked, 4, 2),
            GridButton("5", self.on_button_clicked, 5, 2),
            GridButton("6", self.on_button_clicked, 6, 2),
            GridButton("+", self.on_button_clicked, 7, 2),
            # Row 3
            GridButton("Hex", self.on_convert_clicked, 0, 3),  # Base conversion
            GridButton("Bin", self.on_convert_clicked, 1, 3),
            GridButton("B", self.on_button_clicked, 2, 3),
            GridButton("C", self.on_button_clicked, 3, 3), # Hex digit C
            GridButton("1", self.on_button_clicked, 4, 3),
            GridButton("2", self.on_button_clicked, 5, 3),
            GridButton("3", self.on_button_clicked, 6, 3),
            GridButton(
                "=",
                self.on_equal_clicked,
                7,
                3,
                height=2,
                style_classes=["suggested-action", "accent"],
            ),

            # Row 4
            GridButton("D", self.on_button_clicked, 0, 4),
            GridButton("E", self.on_button_clicked, 1, 4),
            GridButton("F", self.on_button_clicked, 2, 4),
            GridButton("0x", self.on_button_clicked, 3, 4),
            GridButton("0", self.on_button_clicked, 4, 4, width=2),
            GridButton(".", self.on_button_clicked, 6, 4),
        ]

        self.create_buttons(buttons)
