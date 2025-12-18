import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gdk, Adw
import os

class StyleManager:
    _base_provider = None
    _theme_provider = None

    @staticmethod
    def _get_themes_dir():
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, "themes")

    @staticmethod
    def get_available_themes():
        """Returns a list of available theme names (filenames without extension)."""
        themes_dir = StyleManager._get_themes_dir()
        if not os.path.exists(themes_dir):
            return []
        
        themes = []
        for f in os.listdir(themes_dir):
            if f.endswith(".css"):
                themes.append(f[:-4])  # Remove .css extension
        return sorted(themes)

    @staticmethod
    def load_css(theme_name=None):
        """
        Ensures base.css is loaded, and optionally loads a theme CSS on top.
        If theme_name is None, only base.css is loaded (default look).
        """
        display = Gdk.Display.get_default()
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Ensure base provider is loaded once
        if not StyleManager._base_provider:
            provider = Gtk.CssProvider()
            base_path = os.path.join(base_dir, "base.css")
            try:
                provider.load_from_path(base_path)
                Gtk.StyleContext.add_provider_for_display(
                    display,
                    provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_USER
                )
                StyleManager._base_provider = provider
                print(f"Loaded Base CSS from {base_path}")
            except Exception as e:
                print(f"Failed to load Base CSS: {e}")

        # Manage Theme Provider
        # Remove old theme provider first
        if StyleManager._theme_provider:
            Gtk.StyleContext.remove_provider_for_display(
                display,
                StyleManager._theme_provider
            )
            StyleManager._theme_provider = None

        if theme_name:
            provider = Gtk.CssProvider()
            css_path = os.path.join(base_dir, "themes", f"{theme_name}.css")
            
            try:
                provider.load_from_path(css_path)
                
                # Load with higher priority than base
                Gtk.StyleContext.add_provider_for_display(
                    display,
                    provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_USER + 1
                )
                StyleManager._theme_provider = provider
                print(f"Loaded Theme CSS from {css_path}")
            except Exception as e:
                print(f"Failed to load Theme CSS: {e}")

    @staticmethod
    def toggle_theme():
        """Toggle between light and dark application theme."""
        style_manager = Adw.StyleManager.get_default()
        is_dark = style_manager.get_dark()
        style_manager.set_color_scheme(
            Adw.ColorScheme.FORCE_LIGHT if is_dark else Adw.ColorScheme.FORCE_DARK
        )
        return not is_dark  # Return new state (True if dark)

    @staticmethod
    def import_theme(parent_window):
        """Opens a file chooser dialog to import a CSS theme."""
        dialog = Gtk.FileChooserNative(
            title="Import Theme",
            parent=parent_window,
            action=Gtk.FileChooserAction.OPEN
        )
        
        filter_css = Gtk.FileFilter()
        filter_css.set_name("CSS Files")
        filter_css.add_pattern("*.css")
        dialog.add_filter(filter_css)
        
        def on_response(dialog, response):
            if response == Gtk.ResponseType.ACCEPT:
                file = dialog.get_file()
                filepath = file.get_path()
                filename = os.path.basename(filepath)
                
                # Copy file to themes directory
                dest_dir = StyleManager._get_themes_dir()
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)
                    
                import shutil
                shutil.copy(filepath, os.path.join(dest_dir, filename))
                print(f"Imported theme: {filename}")
                
                # Reload themes in UI? (This part needs action feedback, likely reloading the menu or app state)
            dialog.destroy()
            
        dialog.connect("response", on_response)
        dialog.show()
