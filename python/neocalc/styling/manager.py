import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gdk, Adw
import os
import shutil
import logging

logger = logging.getLogger(__name__)

class StyleManager:
    _base_provider = None
    _theme_provider = None

    ## Return the full path to the directory containing theme CSS files
    @staticmethod
    def _get_themes_dir():
        """Returns accessibility path to themes directory."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, "themes")

    @staticmethod
    def get_available_themes():
        """Returns a list of available theme names (filenames without extension)."""
        themes_dir = StyleManager._get_themes_dir()
        if not os.path.exists(themes_dir):
            return []

        ## List all .css files in the themes directory and remove extension
        themes = []
        try:
            for f in os.listdir(themes_dir):
                if f.endswith(".css"):
                    themes.append(f[:-4])
        except OSError as e:
            logger.error(f"Failed to list themes: {e}")
            return []

        return sorted(themes)

    @staticmethod
    def _load_css_provider(display, path, priority):
        """Helper to create, load, and attach a CSS provider."""
        provider = Gtk.CssProvider()
        try:
            ## Load CSS file data into a new provider
            provider.load_from_path(path)
            ## Attach the provider to the display with specified priority
            Gtk.StyleContext.add_provider_for_display(
                display,
                provider,
                priority
            )
            return provider
        except Exception as e:
            logger.error(f"Failed to load CSS from {path}: {e}")
            return None

    @staticmethod
    def load_css(theme_name=None):
        """
        Ensures base.css is loaded, and optionally loads a theme CSS on top.
        Always reloads base to ensure cascade order is preserved.
        """
        display = Gdk.Display.get_default()
        base_dir = os.path.dirname(os.path.abspath(__file__))

        ## Clear any previously loaded custom theme provider
        if StyleManager._theme_provider:
            Gtk.StyleContext.remove_provider_for_display(
                display,
                StyleManager._theme_provider
            )
            StyleManager._theme_provider = None

        if StyleManager._base_provider:
             Gtk.StyleContext.remove_provider_for_display(
                 display,
                 StyleManager._base_provider
             )
             StyleManager._base_provider = None

        ## Load the base styles (always required)
        base_path = os.path.join(base_dir, "base.css")
        StyleManager._base_provider = StyleManager._load_css_provider(
            display,
            base_path,
            Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

        ## If a theme is selected, load it on top with higher priority
        if theme_name and theme_name != 'default':
            theme_path = os.path.join(base_dir, "themes", f"{theme_name}.css")
            StyleManager._theme_provider = StyleManager._load_css_provider(
                display,
                theme_path,
                Gtk.STYLE_PROVIDER_PRIORITY_USER + 1
            )

    @staticmethod
    def toggle_theme():
        """Toggle between light and dark application theme."""
        style_manager = Adw.StyleManager.get_default()
        is_dark = style_manager.get_dark()
        ## Force the opposite color scheme
        style_manager.set_color_scheme(
            Adw.ColorScheme.FORCE_LIGHT if is_dark else Adw.ColorScheme.FORCE_DARK
        )
        return not is_dark

    @staticmethod
    def import_theme(parent_window):
        """Opens a file chooser dialog to import a CSS theme."""
        ## Create a native file picker dialog
        dialog = Gtk.FileChooserNative(
            title=_("Import Theme"),
            transient_for=parent_window,
            action=Gtk.FileChooserAction.OPEN
        )

        dialog.set_title("Import Theme")

        filter_css = Gtk.FileFilter()
        filter_css.set_name("CSS Files")
        filter_css.add_pattern("*.css")
        dialog.add_filter(filter_css)

        def on_response(dialog, response):
            if response == Gtk.ResponseType.ACCEPT:
                file = dialog.get_file()
                filepath = file.get_path()
                filename = os.path.basename(filepath)

                dest_dir = StyleManager._get_themes_dir()
                if not os.path.exists(dest_dir):
                    try:
                        os.makedirs(dest_dir)
                    except OSError as e:
                        logger.error(f"Failed to create themes dir: {e}")
                        return

                try:
                    shutil.copy(filepath, os.path.join(dest_dir, filename))
                    logger.info(f"Imported theme: {filename}")
                except Exception as e:
                     logger.error(f"Failed to copy theme file: {e}")

            dialog.destroy()

        dialog.connect("response", on_response)
        dialog.show()
