import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GObject

class VariablesDialog(Adw.Window):
    """
    Dialog to show defined variables.
    """
    def __init__(self, parent, calc_widget):
        super().__init__(transient_for=parent)
        self.set_title("Variables")
        self.set_modal(True)
        self.set_default_size(320, 400)
        
        self.calc_widget = calc_widget
        
        self.setup_ui()
        self.load_variables()

    def setup_ui(self):
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        # Header
        header = Adw.HeaderBar()
        content.append(header)
        
        # List
        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.list_box.add_css_class("boxed-list")
        
        # Add frame/scroll
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(self.list_box)
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        
        # Clamp content width
        clamp = Adw.Clamp()
        clamp.set_maximum_size(400)
        clamp.set_child(scrolled)
        
        content.append(clamp)
        
        self.set_content(content)

    def load_variables(self):
        variables = self.calc_widget.get_variables()
        
        # Clear existing
        while True:
            child = self.list_box.get_first_child()
            if not child: break
            self.list_box.remove(child)
            
        if not variables:
            # Empty state
            row = Adw.ActionRow(title="No variables defined")
            self.list_box.append(row)
            return

        for name, value in variables.items():
            row = Adw.ActionRow(title=name, subtitle=str(value))
            
            # Insert Button
            insert_btn = Gtk.Button(icon_name="edit-paste-symbolic")
            insert_btn.set_tooltip_text(f"Insert {name}")
            insert_btn.add_css_class("flat")
            insert_btn.connect("clicked", self.on_insert, name)
            
            row.add_suffix(insert_btn)
            self.list_box.append(row)

    def on_insert(self, button, name):
        """Insert variable name into calculator."""
        self.calc_widget.insert_at_cursor(name)
        self.close()
