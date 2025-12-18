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

        self.history_label = Gtk.Label()
        self.history_label.set_xalign(1.0)
        self.history_label.set_justify(Gtk.Justification.RIGHT)
        self.history_label.set_wrap(True)
        self.history_label.set_selectable(True)
        self.history_label.add_css_class("calc-history")
        self.history_label.set_text("")

        self.history_scroll = Gtk.ScrolledWindow()
        self.history_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.history_scroll.set_vexpand(True)
        self.history_scroll.set_child(self.history_label)
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

        self.append(self.history_scroll)
        self.append(self.display_entry)

    def get_text(self):
        return self.display_entry.get_text()

    def set_value(self, text):
        """Set the display value programmatically (does not emit user-edited)."""
        self._internal_update = True
        self.display_entry.set_text(text)
        self.display_entry.set_position(-1)
        self._internal_update = False

    def set_history(self, history_list):
        if history_list:
            recent = history_list[-5:]
            self.history_label.set_text("\n".join(recent))
        else:
            self.history_label.set_text("")

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
