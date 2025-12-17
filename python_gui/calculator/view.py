import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk

from .grid_scientific import ScientificGrid
from .grid_standard import ButtonGrid
from .backend import CalculatorLogic


class CalculatorWidget(Gtk.Box):
    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0, **kwargs)
        
        self.parent_window = None  # Will be set by window when adding instance

        # Model entry (kept hidden) and a separate display label
        # Grids interact with `self.entry` as before; we update the
        # header display label when the entry changes.
        self.entry = Gtk.Entry()
        self.entry.set_hexpand(True)
        self.entry.set_vexpand(False)
        self.entry.set_alignment(1.0)  # Right align
        self.entry.add_css_class("calc-entry")

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

        # Create the display box once (not on every get_display_widget call)
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

        # Keep the entry as the data model; update label on changes
        self.entry.connect(
            "changed", lambda e: self.display_label.set_text(e.get_text())
        )

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

        # View Switcher Title logic is tricky inside a widget because the title is in the Window Header.
        # However, the ViewStack is here.
        # We need to expose the ViewStack so the Window can bind its SwitcherTitle to it.

        self.view_stack = Adw.ViewStack()

        # Standard Grid Page
        standard_page = Adw.ViewStackPage()

        # Pass 'self' as the "calculator_window" expected by Grids
        # The Grids expect `self.calculator` to have an `entry`.
        # Since 'self' here is CalculatorWidget and it has 'entry', it handles the interface implicitly.
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

    def get_stack(self):
        return self.view_stack

    def get_display_widget(self):
        """Return the widget suitable for placing in the header title area."""
        # Update history display and return the pre-created display box
        self.update_history_display()
        return self.display_box
    
    def update_history_display(self):
        """Update the history label with recent calculations."""
        history = CalculatorLogic.get_history()
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

