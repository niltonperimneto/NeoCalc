import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

import os

from .backend import CalculatorLogic

class ScientificGrid(Gtk.Grid):
    def __init__(self, calculator_window):
        super().__init__(row_spacing=5, column_spacing=5)
        self.set_row_homogeneous(True)
        self.set_column_homogeneous(True)
        self.calculator = calculator_window

        # Layout: 6 columns.
        # Cols 0-1: Scientific Functions
        # Cols 2-5: Standard Calculator Layout (aligned perfectly)

        buttons_info = [
            # Row 0
            ("(", self.on_button_clicked, 0, 0, 1, 1),
            (")", self.on_button_clicked, 1, 0, 1, 1),
            ("C", self.on_clear_clicked, 2, 0, 1, 1),
            ("/", self.on_button_clicked, 3, 0, 1, 1),
            ("*", self.on_button_clicked, 4, 0, 1, 1),
            ("-", self.on_button_clicked, 5, 0, 1, 1),
            
            # Row 1
            ("sin", self.on_func_clicked, 0, 1, 1, 1),
            ("^", self.on_button_clicked, 1, 1, 1, 1),
            ("7", self.on_button_clicked, 2, 1, 1, 1),
            ("8", self.on_button_clicked, 3, 1, 1, 1),
            ("9", self.on_button_clicked, 4, 1, 1, 1),
            ("+", self.on_button_clicked, 5, 1, 1, 2), # Tall +
            
            # Row 2
            ("cos", self.on_func_clicked, 0, 2, 1, 1),
            ("sqrt", self.on_func_clicked, 1, 2, 1, 1),
            ("4", self.on_button_clicked, 2, 2, 1, 1),
            ("5", self.on_button_clicked, 3, 2, 1, 1),
            ("6", self.on_button_clicked, 4, 2, 1, 1),
            
            # Row 3
            ("tan", self.on_func_clicked, 0, 3, 2, 1), # Wide tan
            ("1", self.on_button_clicked, 2, 3, 1, 1),
            ("2", self.on_button_clicked, 3, 3, 1, 1),
            ("3", self.on_button_clicked, 4, 3, 1, 1),
            ("=", self.on_equal_clicked, 5, 3, 1, 2), # Tall =
            
            # Row 4
            ("log", self.on_func_clicked, 0, 4, 2, 1), # Wide log
            ("0", self.on_button_clicked, 2, 4, 2, 1), # Wide 0
            (".", self.on_button_clicked, 4, 4, 1, 1),
        ]

        for label, callback, col, row, width, height in buttons_info:
            button = Gtk.Button(label=label)
            button.connect("clicked", callback)
            
            if label == "=":
                button.add_css_class("suggested-action")
            elif label == "C":
                button.add_css_class("destructive-action")
            
            button.set_hexpand(True)
            button.set_vexpand(True)
            # Use attach instead of deprecated attach_next_to or grid positions logic
            self.attach(button, col, row, width, height)

    def on_button_clicked(self, button):
        current = self.calculator.entry.get_text()
        new_text = CalculatorLogic.append_text(current, button.get_label())
        self.calculator.entry.set_text(new_text)

    def on_func_clicked(self, button):
        current = self.calculator.entry.get_text()
        new_text = CalculatorLogic.append_function(current, button.get_label())
        self.calculator.entry.set_text(new_text)

    def on_equal_clicked(self, button):
        expression = self.calculator.entry.get_text()
        result_text = CalculatorLogic.evaluate(expression)
        self.calculator.entry.set_text(result_text)

    def on_clear_clicked(self, button):
        self.calculator.entry.set_text(CalculatorLogic.clear())
