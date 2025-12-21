import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GObject

class CalculatorDisplay(Gtk.Box):
    """
    A widget acting as the calculator's display.
    Combines a history label and an editable entry.
    """

    __gsignals__ = {
        'user-edited': (GObject.SignalFlags.RUN_FIRST, None, (str,)),
        'activated': (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    INPUT_MAPPINGS = {
        "÷": "/",
        "×": "*",
        "−": "-",
        "π": "pi",
        "√": "sqrt(",
    }

    AUTO_PAREN_FUNCTIONS = {
        "sin", "cos", "tan", "asin", "acos", "atan",
        "sinh", "cosh", "tanh", "log", "ln", "sqrt", "abs"
    }

    def __init__(self, **kwargs):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=4, **kwargs)

        self._internal_update = False

        self.history_list = Gtk.ListBox()
        self.history_list.set_selection_mode(Gtk.SelectionMode.NONE)
        self.history_list.add_css_class("calc-history-list")
        self.history_list.connect("row-activated", self._on_history_row_activated)

        self.history_scroll = Gtk.ScrolledWindow()
        self.history_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.history_scroll.set_vexpand(True)
        self.history_scroll.set_child(self.history_list)
        self.history_scroll.add_css_class("calc-history-scroll")

        self.display_entry = Gtk.Entry()
        self.display_entry.set_alignment(1.0)
        self.display_entry.add_css_class("calc-entry-display")
        self.display_entry.set_text("0")
        self.display_entry.set_hexpand(True)
        self.display_entry.set_width_chars(1)
        self.display_entry.set_max_width_chars(0)

        self.display_entry.connect("changed", self._on_entry_changed)
        self.display_entry.connect("activate", self._on_entry_activate)

        self.preview_label = Gtk.Label()
        self.preview_label.set_xalign(1.0)
        self.preview_label.add_css_class("calc-preview")
        self.preview_label.set_text("")

        self.append(self.history_scroll)
        self.append(self.display_entry)
        self.append(self.preview_label)

    def get_text(self):
        return self.display_entry.get_text()

    def set_value(self, text):
        """Set the display value programmatically (does not emit user-edited)."""
        self._internal_update = True
        self.display_entry.set_text(text)
        self.display_entry.set_position(-1)
        self._internal_update = False

    def set_preview(self, text):
        """Set the preview label text."""
        self.preview_label.set_text(text)

    def set_history(self, history_list):
        """Update history listbox."""
        ## Clear existing children
        while True:
            child = self.history_list.get_first_child()
            if not child:
                break
            self.history_list.remove(child)

        if history_list:
            ## Show recent items
            for item_text in history_list[-10:]:
                row = Gtk.ListBoxRow()
                label = Gtk.Label(label=item_text)
                label.set_xalign(1.0)
                label.add_css_class("calc-history-item")
                row.set_child(label)
                self.history_list.append(row)
    
    def _on_history_row_activated(self, box, row):
        """Handle history item click."""
        label = row.get_child()
        if label:
             text = label.get_text()
             ## Extract result (basic assumption: "expr = result")
             if "=" in text:
                 result = text.split("=")[-1].strip()
                 self.insert_at_cursor(result)
             else:
                 self.insert_at_cursor(text)

    def insert_at_cursor(self, text):
        """Insert text at current cursor position, handling mapping."""

        text = self.INPUT_MAPPINGS.get(text, text)

        if text in self.AUTO_PAREN_FUNCTIONS:
            text += "("

        current_text = self.display_entry.get_text()
        pos = self.display_entry.get_position()

        new_text = current_text[:pos] + text + current_text[pos:]
        new_pos = pos + len(text)

        self._internal_update = True
        self.display_entry.set_text(new_text)
        self.display_entry.set_position(new_pos)
        self._internal_update = False

        self.emit('user-edited', new_text)

    def backspace_at_cursor(self):
        """Delete character before cursor."""
        current_text = self.display_entry.get_text()
        pos = self.display_entry.get_position()

        start, end = self.display_entry.get_selection_bounds()
        new_text = current_text
        new_pos = pos

        if start != end:
             min_pos = min(start, end)
             max_pos = max(start, end)
             new_text = current_text[:min_pos] + current_text[max_pos:]
             new_pos = min_pos
        elif pos > 0:
             new_text = current_text[:pos-1] + current_text[pos:]
             new_pos = pos - 1
        else:
             return

        self._internal_update = True
        self.display_entry.set_text(new_text)
        self.display_entry.set_position(new_pos)
        self._internal_update = False

        self.emit('user-edited', new_text)

    def _on_entry_changed(self, entry):
        if self._internal_update:
            return
        self.emit('user-edited', entry.get_text())

    def _on_entry_activate(self, entry):
        self.emit('activated')

    def has_focus(self):
         root = self.get_root()
         if root:
             return root.get_focus() == self.display_entry
         return False
