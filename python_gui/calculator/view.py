import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gdk, Adw, GObject

from .grid_standard import ButtonGrid
from .grid_scientific import ScientificGrid

class CalculatorWidget(Gtk.Box):
    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10, **kwargs)
        
        self.set_margin_start(20)
        self.set_margin_end(20)
        self.set_margin_top(20)
        self.set_margin_bottom(20)

        frame = Gtk.AspectFrame(ratio=0.7, obey_child=False)
        self.append(frame)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        frame.set_child(main_box)

        self.entry = Gtk.Entry()
        self.entry.set_hexpand(True)
        self.entry.set_vexpand(False)
        self.entry.set_margin_bottom(10)
        self.entry.set_size_request(-1, 80)
        self.entry.set_alignment(1.0) # Right align
        self.entry.add_css_class("calc-entry")

        # We load CSS provider once in main or window, but ensuring it here doesn't hurt if check duplicates
        # Actually better to do it in main app or window to avoid re-adding provider multiple times.
        # Assuming window handles global CSS.

        main_box.append(self.entry)
        
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
        self.view_stack.get_page(scientific_grid).set_icon_name("applications-science-symbolic")
        
        main_box.append(self.view_stack)

    def get_stack(self):
        return self.view_stack
