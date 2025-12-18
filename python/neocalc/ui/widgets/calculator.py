import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk, GLib

from ..grids.scientific import ScientificGrid
from ..grids.standard import ButtonGrid
from ...core.backend import CalculatorLogic

from ..components.display import CalculatorDisplay

class CalculatorWidget(Gtk.Box):
    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0, **kwargs)
        
        self.parent_window = None  # Will be set by window when adding instance
        self.logic = CalculatorLogic() # Instance-specific logic
        
        # Initial display sync
        GLib.idle_add(self.update_display)

        # Key Controller for input handling
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self.on_key_pressed)
        self.add_controller(key_controller)

        # Display Component
        self.display = CalculatorDisplay()
        self.display.connect('user-edited', self.on_display_edited)
        self.display.connect('activated', self.on_display_activated)

        # Main content area with grids
        main_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        # Add minimal padding around grid
        main_content.set_margin_start(8)
        main_content.set_margin_end(8)
        main_content.set_margin_top(8)
        main_content.set_margin_bottom(8)

        # Grid box that expands to fill available space
        grid_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        grid_box.set_hexpand(True)
        grid_box.set_vexpand(True)
        main_content.append(grid_box)

        # View Switcher Title logic
        self.view_stack = Adw.ViewStack()

        # Standard Grid Page
        # Pass 'self' as the "calculator_window" interface
        button_grid = ButtonGrid(self)
        self.view_stack.add_titled(button_grid, "standard", "Standard")
        self.view_stack.get_page(button_grid).set_icon_name("view-grid-symbolic")

        # Scientific Grid Page
        scientific_grid = ScientificGrid(self)
        self.view_stack.add_titled(scientific_grid, "scientific", "Scientific")
        self.view_stack.get_page(scientific_grid).set_icon_name(
            "applications-science-symbolic"
        )

        grid_box.append(self.view_stack)
        
        grid_box.append(self.view_stack)
        
        # Append Content only (Display is handled by DisplayManager/Window)
        self.append(main_content)
        self.set_vexpand(True)

        # Ensure we can accept focus for key events
        self.set_focusable(True)

        # Callback for external listeners (like sidebar preview)
        self.on_expression_changed = None

    def get_stack(self):
        return self.view_stack

    def get_display_widget(self):
        """Return the display widget to be placed in the header/stack."""
        self.update_history_display()
        return self.display
    
    def update_history_display(self):
        """Update the history label with recent calculations."""
        history = self.logic.get_history()
        self.display.set_history(history)
    
    def trigger_name_update(self):
        """Trigger parent window to update calculator name"""
        if self.parent_window and hasattr(self.parent_window, 'update_calculator_name'):
            self.parent_window.update_calculator_name(self)

    # --- input interface for Grids ---
    def get_expression(self):
        return self.logic.get_buffer()

    def set_expression(self, text):
        """Called when logic updates (e.g. from buttons)"""
        self.display.set_value(text)
        if self.on_expression_changed:
            self.on_expression_changed(text)

    def insert_at_cursor(self, text):
        self.display.insert_at_cursor(text)

    def backspace_at_cursor(self):
        self.display.backspace_at_cursor()

    def update_display(self):
        # Pull from logic and update UI
        text = self.logic.get_buffer()
        self.display.set_value(text)
        if self.on_expression_changed:
            self.on_expression_changed(text)

    def on_display_edited(self, widget, text):
        self.logic.set_expression(text)
        if self.on_expression_changed:
            self.on_expression_changed(text)

    def on_display_activated(self, widget):
        self.logic.evaluate()
        self.update_display()
        self.update_history_display()
        self.trigger_name_update()

    # --- input handling ---
    def on_key_pressed(self, controller, keyval, keycode, state):
        # if entry has focus, let it handle the key
        if self.display.has_focus():
            return False 

        # Handle digits and operators directly (when entry doesn't have focus)
        from gi.repository import Gdk
        
        # Determine character
        key_char = Gdk.keyval_to_unicode(keyval)
        valid_chars = "0123456789.+-*/^%()"
        
        if key_char and chr(key_char) in valid_chars:
            self.insert_at_cursor(chr(key_char))
            return True
            
        name = Gdk.keyval_name(keyval)
        
        if name == "BackSpace":
             self.backspace_at_cursor()
             return True

        elif name in ("Return", "KP_Enter"):
            self.on_display_activated(None)
            return True
        
        elif name == "Escape":
            self.logic.clear()
            self.update_display()
            return True

        return False

