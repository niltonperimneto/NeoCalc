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

## Define location of locale files for translations, ensuring fallback to parent dir
LOCALE_DIR = os.path.join(BASE_DIR, "locale")

if not os.path.exists(LOCALE_DIR):
    LOCALE_DIR = os.path.join(os.path.dirname(BASE_DIR), "locale")

try:
    ## Attempt to load translations for current system locale
    trans = gettext.translation('neocalc', localedir=LOCALE_DIR, languages=None, fallback=True)
    trans.install()
except Exception as e:
    print(f"Warning: Failed to load translations from {LOCALE_DIR}: {e}")
    gettext.install('neocalc', LOCALE_DIR)

class CalculatorApp(Adw.Application):
    def __init__(self):
        ## Initialize the Adwaita application
        ## application_id must be unique and match the desktop file

        super().__init__(application_id="com.nilton.calculator",
                         flags=Gio.ApplicationFlags.NON_UNIQUE)

    def do_activate(self):
        ## On activation, create and present the main window
        Calculator(self).present()

def main():
    import sys
    ## Ensure correct argument handling (used by some packaging tools)
    argv = sys.argv
    if not argv or not argv[0]:
        argv = ["neocalc"]

    ## Run the application
    CalculatorApp().run(argv)

if __name__ == "__main__":
    main()
