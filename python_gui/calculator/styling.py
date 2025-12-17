import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gdk, Adw
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

    @staticmethod
    def toggle_theme():
        """Toggle between light and dark application theme."""
        style_manager = Adw.StyleManager.get_default()
        is_dark = style_manager.get_dark()
        style_manager.set_color_scheme(
            Adw.ColorScheme.FORCE_LIGHT if is_dark else Adw.ColorScheme.FORCE_DARK
        )
        return not is_dark  # Return new state (True if dark)
