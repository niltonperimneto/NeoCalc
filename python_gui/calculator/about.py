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
    dialog.set_comments("The calculator that judges you.\n(Forked &amp; Broken for educational purposes)")
    dialog.set_website("https://github.com/niltonperimneto/NeoCalc")
    dialog.set_issue_url("https://github.com/niltonperimneto/NeoCalc/issues")
    
    # Identity
    dialog.set_application_icon("model-source") 
    
    # Credits
    dialog.add_credit_section("Original Code", ["Nilton Perim Neto"])
    dialog.add_credit_section("New Code (Rust)", ["Nilton Perim Neto"])
    dialog.add_credit_section("Purpose", ["To teach innocent kids Python", "To try to teach me Rust"])
    
    # Copyright
    dialog.set_copyright("© 2025 Nilton Perim Neto")
    
    dialog.present()
