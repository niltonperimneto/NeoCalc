import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version('Rsvg', '2.0')
from gi.repository import Adw
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from calculator.ui.window import Calculator

BASE_DIR = getattr(sys, 'frozen', False) and sys._MEIPASS or os.path.dirname(os.path.abspath(__file__))
BASE_DIR = getattr(sys, 'frozen', False) and sys._MEIPASS or os.path.dirname(os.path.abspath(__file__))

class CalculatorApp(Adw.Application):
    def __init__(self):
        # Oh look, another calculator. Because the world definitely needed one more 
        # way to divide by zero and crash the economy.
        super().__init__(application_id="com.nilton.calculator")

    def do_activate(self, app=None):
        Calculator(self).present()

def main():
    CalculatorApp().run()

if __name__ == "__main__":
    # The entry point of our doom.
    main()
