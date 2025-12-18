import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk, GLib

from .grid_scientific import ScientificGrid
from .grid_standard import ButtonGrid
from .backend import CalculatorLogic


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

        # History display label (shows previous calculations)
        self.history_label = Gtk.Label()
        self.history_label.set_xalign(1.0)
        self.history_label.set_justify(Gtk.Justification.RIGHT)
        self.history_label.set_wrap(True)
        self.history_label.set_selectable(True)
        self.history_label.add_css_class("calc-history")
        self.history_label.set_text("")  # Initially empty

        # Header display label (multiline capable)
        self.display_label = Gtk.Label()
        self.display_label.set_xalign(1.0)
        self.display_label.set_justify(Gtk.Justification.RIGHT)
        self.display_label.set_wrap(True)
        self.display_label.add_css_class("calc-entry-display")
        self.display_label.set_text("0")

        # Create the display box once
        self.display_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        
        # Scrolled window for history
        history_scroll = Gtk.ScrolledWindow()
        history_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        history_scroll.set_max_content_height(150)
        history_scroll.set_propagate_natural_height(True)
        history_scroll.set_child(self.history_label)
        history_scroll.add_css_class("calc-history-scroll")
        
        self.display_box.append(history_scroll)
        self.display_box.append(self.display_label)

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
        self.append(main_content)
        self.set_vexpand(True)

        # Ensure we can accept focus for key events
        self.set_focusable(True)

        # Callback for external listeners (like sidebar preview)
        self.on_expression_changed = None

    def get_stack(self):
        return self.view_stack

    def get_display_widget(self):
        """Return the widget suitable for placing in the header title area."""
        self.update_history_display()
        return self.display_box
    
    def update_history_display(self):
        """Update the history label with recent calculations."""
        history = self.logic.get_history()
        if history:
            # Show last 5 entries
            recent_history = history[-5:]
            self.history_label.set_text("\n".join(recent_history))
        else:
            self.history_label.set_text("")
    
    def trigger_name_update(self):
        """Trigger parent window to update calculator name"""
        if self.parent_window and hasattr(self.parent_window, 'update_calculator_name'):
            self.parent_window.update_calculator_name(self)

    # --- input interface for Grids ---
    def get_expression(self):
        # Delegate to logic
        return self.logic.get_buffer()

    def set_expression(self, text):
        # Legacy hook, ideally we call logic directly.
        # But if grids call this with a string, we might desync if we don't handle it carefully.
        # Actually grids assume they are managing state via set_expression(result).
        # We should update grids too.
        # For now, if this is called with a result (from evaluate), we update display.
        # But if it's called with "text" from append... 
        # Refactor: this method just updates display.
        self.display_label.set_text(text)
        if self.on_expression_changed:
            self.on_expression_changed(text)

    def update_display(self):
        text = self.logic.get_buffer()
        self.display_label.set_text(text)
        if self.on_expression_changed:
            self.on_expression_changed(text)

    # --- input handling ---
    def on_key_pressed(self, controller, keyval, keycode, state):
        # Handle digits and operators directly
        from gi.repository import Gdk, GLib
        
        # Determine character
        key_char = Gdk.keyval_to_unicode(keyval)
        valid_chars = "0123456789.+-*/^%()"
        
        if key_char and chr(key_char) in valid_chars:
            self.logic.input(chr(key_char))
            self.update_display()
            return True
            
        name = Gdk.keyval_name(keyval)
        
        if name == "BackSpace":
             self.logic.backspace()
             self.update_display()
             return True

        elif name in ("Return", "KP_Enter"):
            # Evaluate
            self.logic.evaluate() # No arg uses buffer
            self.update_display() 
            self.update_history_display()
            self.trigger_name_update()
            return True
        
        elif name == "Escape":
            self.logic.clear()
            self.update_display()
            return True

        return False

