import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw
import os

from neocalc._version import __version__

def present_about_dialog(parent):
    dialog = Adw.AboutWindow(transient_for=parent)
    dialog.set_application_name("NeoCalc")
    dialog.set_version(__version__)
    dialog.set_developer_name("Nilton Perim Neto")
    dialog.set_license_type(Gtk.License.GPL_3_0)
    dialog.set_comments(_("A modern, powerful calculator built with GTK4 and Rust.\nDesigned for GNOME."))
    dialog.set_website("https://github.com/niltonperimneto/neocalc")
    dialog.set_issue_url("https://github.com/niltonperimneto/neocalc/issues")

    dialog.set_application_icon("com.nilton.neocalc")

    dialog.add_credit_section(_("Created By"), ["Nilton Perim Neto"])
    dialog.add_credit_section(_("Contributions"), ["Welcome at GitHub!"])
    
    # Add a specific link for contributions if needed, or rely on website
    # Adw.AboutWindow shows website as "Website" button.
    
    dialog.set_copyright("© 2025 Nilton Perim Neto")

    dialog.present()
