import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version('Rsvg', '2.0')
from gi.repository import Adw, Gio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from calculator.ui.window import Calculator

BASE_DIR = getattr(sys, 'frozen', False) and sys._MEIPASS or os.path.dirname(os.path.abspath(__file__))
BASE_DIR = getattr(sys, 'frozen', False) and sys._MEIPASS or os.path.dirname(os.path.abspath(__file__))

class CalculatorApp(Adw.Application):
    def __init__(self):
        # Force NON_UNIQUE to ensure it runs even if DBus thinks another one exists
        super().__init__(application_id="com.nilton.calculator",
                         flags=Gio.ApplicationFlags.NON_UNIQUE)

    def do_activate(self, app=None):
        Calculator(self).present()

def main():
    import sys
    # Ensure argv is valid for GApplication
    argv = sys.argv
    if not argv or not argv[0]:
        argv = ["neocalc"]
        
    CalculatorApp().run(argv)

if __name__ == "__main__":
    main()
