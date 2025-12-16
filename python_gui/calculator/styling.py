import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk
import os

class StyleManager:
    @staticmethod
    def load_css():
        css_provider = Gtk.CssProvider()
        
        # Calculate path to style.css relative to this file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        css_path = os.path.join(base_dir, "style.css")
        
        try:
            css_provider.load_from_path(css_path)
            
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(),
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_USER
            )
            print(f"Loaded CSS from {css_path}")
        except Exception as e:
            print(f"Failed to load CSS: {e}")
