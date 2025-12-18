import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version('Rsvg', '2.0')
from gi.repository import Adw, Gio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from neocalc.ui.windows.main_window import Calculator
import gettext

BASE_DIR = getattr(sys, 'frozen', False) and sys._MEIPASS or os.path.dirname(os.path.abspath(__file__))

# Initialize Localization
LOCALE_DIR = os.path.join(BASE_DIR, "locale")
# Fallback to ../locale if we are in python_gui/ and locale is in root (development mode)
if not os.path.exists(LOCALE_DIR):
    LOCALE_DIR = os.path.join(os.path.dirname(BASE_DIR), "locale")

try:
    # Try to load the user's locale
    trans = gettext.translation('neocalc', localedir=LOCALE_DIR, languages=None, fallback=True)
    trans.install() 
except Exception as e:
    print(f"Warning: Failed to load translations from {LOCALE_DIR}: {e}")
    gettext.install('neocalc', LOCALE_DIR) # Fallback


class CalculatorApp(Adw.Application):
    def __init__(self):
        # Oh look, another calculator. Because the world definitely needed one more
        # way to divide by zero and crash the economy.
        # Force NON_UNIQUE to ensure it runs even if DBus thinks another one exists
        super().__init__(application_id="com.nilton.calculator",
                         flags=Gio.ApplicationFlags.NON_UNIQUE)

    def do_activate(self):
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
