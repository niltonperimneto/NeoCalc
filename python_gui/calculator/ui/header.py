import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio, GObject

class CalcType(GObject.GObject):
    def __init__(self, label, icon):
        super().__init__()
        self.label = label
        self.icon = icon

class HeaderView(Adw.Bin):
    """Handles the application header bar, including dropdown and menu."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.header_bar = Adw.HeaderBar()
        self.set_child(self.header_bar)
        self.setup_ui()
        
    def setup_ui(self):
        # Toggle Sidebar Button
        toggle_btn = Gtk.Button(icon_name="sidebar-show-symbolic")
        toggle_btn.set_tooltip_text("Toggle Sidebar")
        toggle_btn.connect("clicked", self.main_window.on_toggle_sidebar)
        toggle_btn.add_css_class("header-btn")
        self.header_bar.pack_start(toggle_btn)
        
        # Calculator Type Dropdown
        self.setup_dropdown()
        
        # Menu Button
        self.setup_menu()
        
    def setup_dropdown(self):
        type_model = Gio.ListStore(item_type=GObject.Object)
        type_model.append(CalcType("Standard", "view-grid-symbolic"))
        type_model.append(CalcType("Scientific", "applications-science-symbolic"))

        factory = Gtk.SignalListItemFactory()
        def setup_factory(factory, list_item):
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            icon = Gtk.Image()
            icon.set_pixel_size(18)
            box.append(icon)
            label = Gtk.Label()
            label.set_xalign(0)
            box.append(label)
            list_item.set_child(box)
            
        def bind_factory(factory, list_item):
            item = list_item.get_item()
            box = list_item.get_child()
            icon = box.get_first_child()
            label = icon.get_next_sibling()
            icon.set_from_icon_name(item.icon)
            label.set_text(item.label)
            
        factory.connect("setup", setup_factory)
        factory.connect("bind", bind_factory)

        self.type_dropdown = Gtk.DropDown(model=type_model, factory=factory)
        self.type_dropdown.set_selected(0)
        self.type_dropdown.set_hexpand(False)
        self.type_dropdown.set_halign(Gtk.Align.CENTER)
        self.type_dropdown.add_css_class("center-dropdown")
        self.type_dropdown.connect("notify::selected", self.main_window.on_type_dropdown_changed)
        self.header_bar.set_title_widget(self.type_dropdown)
        
    def setup_menu(self):
        menu_model = Gio.Menu()
        menu_model.append("Toggle theme", "win.toggle_dark")
        menu_model.append("Keyboard Shortcuts", "win.show_shortcuts")
        menu_model.append("About", "win.about")
        
        menu_btn = Gtk.MenuButton()
        menu_btn.set_icon_name("open-menu-symbolic")
        menu_btn.set_menu_model(menu_model)
        menu_btn.add_css_class("header-btn")
        self.header_bar.pack_end(menu_btn)

    def set_selected_type(self, index):
        self.type_dropdown.set_selected(index)
