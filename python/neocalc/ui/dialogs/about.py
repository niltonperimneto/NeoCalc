import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw
import os

def present_about_dialog(parent):
    dialog = Adw.AboutWindow(transient_for=parent)
    dialog.set_application_name("NeoCalc")
    dialog.set_version("1.0")
    dialog.set_developer_name("Nilton Perim Neto")
    dialog.set_license_type(Gtk.License.GPL_3_0)
    dialog.set_comments(_("The calculator that judges you.\n(Forked & Broken for educational purposes)"))
    dialog.set_website("https://github.com/niltonperimneto/NeoCalc")
    dialog.set_issue_url("https://github.com/niltonperimneto/NeoCalc/issues")

    dialog.set_application_icon("model-source")

    dialog.add_credit_section(_("Original Code"), ["Nilton Perim Neto"])
    dialog.add_credit_section(_("New Code (Rust)"), ["Nilton Perim Neto"])
    dialog.add_credit_section(_("Purpose"), [_("To teach innocent kids Python"), _("To try to teach me Rust")])

    dialog.set_copyright("© 2025 Nilton Perim Neto")

    dialog.present()
