from gi.repository import Gtk, Adw

def show_shortcuts_dialog(parent_window):
    """Show a shortcuts window with all keyboard shortcuts"""
    builder = Gtk.Builder()

    shortcuts_ui = """
<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <object class="GtkShortcutsWindow" id="shortcuts_window">
    <property name="modal">1</property>
    <child>
      <object class="GtkShortcutsSection">
        <property name="section-name">shortcuts</property>
        <property name="max-height">12</property>
        <child>
          <object class="GtkShortcutsGroup">
            <property name="title" translatable="yes">Keyboard Shortcuts</property>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">New Calculator</property>
                <property name="accelerator">&lt;Control&gt;t</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">Toggle Dark Mode</property>
                <property name="accelerator">&lt;Control&gt;d</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">Switch to Scientific Mode</property>
                <property name="accelerator">&lt;Control&gt;s</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">Switch to Standard Mode</property>
                <property name="accelerator">&lt;Control&gt;r</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">Switch to Calculator 1-9</property>
                <property name="accelerator">&lt;Alt&gt;1...9</property>
              </object>
            </child>
            <child>
              <object class="GtkShortcutsShortcut">
                <property name="title" translatable="yes">Show Keyboard Shortcuts</property>
                <property name="accelerator">&lt;Control&gt;h</property>
              </object>
            </child>
          </object>
        </child>
      </object>
    </child>
  </object>
</interface>
"""

    builder.set_translation_domain("neocalc")
    builder.add_from_string(shortcuts_ui)
    shortcuts_window = builder.get_object("shortcuts_window")
    shortcuts_window.set_transient_for(parent_window)
    shortcuts_window.present()
