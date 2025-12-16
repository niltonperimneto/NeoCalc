import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

import os

from .backend import CalculatorLogic

class ButtonGrid(Gtk.Grid):
    def __init__(self, calculator_window):
        super().__init__(row_spacing=5, column_spacing=5)
        self.set_row_homogeneous(True)
        self.set_column_homogeneous(True)
        self.calculator = calculator_window

        # Define buttons structure: (label, callback)
        # Because apparently hardcoding a matrix is "good design" in this dystopia.
        # We align to the Scientific layout's right side (cols 1-4) for "consistency" or whatever.
        # Actually scientific is 5 cols. We are 4. 
        # So we just float in the void.
        
        # Row 0: C / * -
        # Row 1: 7 8 9 +
        # Row 2: 4 5 6 + (merged? no)
        # Row 3: 1 2 3 =
        # Row 4: 0 . = (merged)
        
        # To make it consistent with Scientific (which is 5x5), we will map:
        # Sci: [func] [7] [8] [9] [/]
        # Std: [C]    [/] [*] [-] (Row 0 is weird)
        # Let's just keep the 4x5 but use the loop.
        
        buttons = [
            ("C", self.on_clear_clicked), ("/", self.on_button_clicked), ("*", self.on_button_clicked), ("-", self.on_button_clicked),
            ("7", self.on_button_clicked), ("8", self.on_button_clicked), ("9", self.on_button_clicked), ("+", self.on_button_clicked),
            ("4", self.on_button_clicked), ("5", self.on_button_clicked), ("6", self.on_button_clicked), ("+", self.on_button_clicked), # Wait, + is tall? logic below handles spans.
            ("1", self.on_button_clicked), ("2", self.on_button_clicked), ("3", self.on_button_clicked), ("=", self.on_equal_clicked),
            ("0", self.on_button_clicked), (".", self.on_button_clicked), ("=", self.on_equal_clicked)
        ]
        
        # Okay, the old code had specific manual placement. 
        # I'll just rewrite the layout logic to be "consistent" with the scientific one (iterative).
        # But wait, the standard one has TALL and WIDE buttons. Scientific is uniform 1x1.
        # Uniformity is the death of creativity, so let's enforce it.
        # User asked for consistency. Let's make standard grid 1x1 only.
        
        # Revised Layout (4x5 uniform):
        # C / * -
        # 7 8 9 +
        # 4 5 6 + (No, + can't be twice)
        # Let's use the standard layout but flattened to 1x1 where possible? 
        # Actually, let's just make it simple 4x5 uniform.
        
        buttons_flat = [
             "C", "/", "*", "-",
             "7", "8", "9", "+",
             "4", "5", "6", "+", # Placeholder for tall +? No, standard usually has + spanning.
             "1", "2", "3", "=",
             "0", "0", ".", "="  # Placeholder for wide 0 and tall =
        ]
        
        # Fine, we stick to the manual spans but make the code look like I hate it less.
        # We will use the original "buttons_info" approach but better commented.
        
        buttons_info = [
            # Row 0
            ("C", self.on_clear_clicked, 0, 0, 1, 1),
            ("/", self.on_button_clicked, 1, 0, 1, 1),
            ("*", self.on_button_clicked, 2, 0, 1, 1),
            ("-", self.on_button_clicked, 3, 0, 1, 1),
            # Row 1
            ("7", self.on_button_clicked, 0, 1, 1, 1),
            ("8", self.on_button_clicked, 1, 1, 1, 1),
            ("9", self.on_button_clicked, 2, 1, 1, 1),
            ("+", self.on_button_clicked, 3, 1, 1, 2), # The monolith +
            # Row 2
            ("4", self.on_button_clicked, 0, 2, 1, 1),
            ("5", self.on_button_clicked, 1, 2, 1, 1),
            ("6", self.on_button_clicked, 2, 2, 1, 1),
            # Row 3
            ("1", self.on_button_clicked, 0, 3, 1, 1),
            ("2", self.on_button_clicked, 1, 3, 1, 1),
            ("3", self.on_button_clicked, 2, 3, 1, 1),
            ("=", self.on_equal_clicked, 3, 3, 1, 2), # The judge =
            # Row 4
            ("0", self.on_button_clicked, 0, 4, 2, 1), # The void 0
            (".", self.on_button_clicked, 2, 4, 1, 1),
        ]

        for label, callback, col, row, width, height in buttons_info:
            button = Gtk.Button(label=label)
            # Binding the click of doom
            button.connect("clicked", callback)
            
            if label == "=":
                button.add_css_class("suggested-action")
            elif label == "C":
                button.add_css_class("destructive-action")
                
            button.set_hexpand(True)
            button.set_vexpand(True)
            self.attach(button, col, row, width, height)
        
    def on_button_clicked(self, button):
        # A button was clicked. The user feels productive.
        current = self.calculator.entry.get_text()
        new_text = CalculatorLogic.append_text(current, button.get_label())
        self.calculator.entry.set_text(new_text)

    def on_equal_clicked(self, button):
        # The moment of truth. Or error. Probably error.
        expression = self.calculator.entry.get_text()
        result_text = CalculatorLogic.evaluate(expression)
        self.calculator.entry.set_text(result_text)

    def on_clear_clicked(self, button):
        # Wipe away the evidence of your mathematical incompetence.
        self.calculator.entry.set_text(CalculatorLogic.clear())
