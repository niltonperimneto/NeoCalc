from gi.repository import Gtk

class DisplayManager:
    """Manages the display area in the header."""
    
    def __init__(self, placeholder_box):
        self._placeholder = placeholder_box

    def switch_display_for(self, calc_widget):
        """Place the given calculator's display widget into the header placeholder."""
        if calc_widget is None:
            return
            
        display = calc_widget.get_display_widget()
        
        # Only reparent if the display is not already the child
        current_child = self._placeholder.get_first_child()
        if current_child is display:
            calc_widget.update_history_display()
            return
        
        # Remove existing children from placeholder
        child = self._placeholder.get_first_child()
        while child is not None:
            next_child = child.get_next_sibling()
            self._placeholder.remove(child)
            child = next_child

        # If the display is currently parented elsewhere, unparent first
        parent = display.get_parent()
        if parent is not None and parent is not self._placeholder:
            parent.remove(display)
        
        self._placeholder.append(display)
