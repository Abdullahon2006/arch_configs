#!/usr/bin/env python3
import subprocess
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk
from popup import BasePopup

class PowerMenu(BasePopup):
    def __init__(self):
        super().__init__(name="power", width=240, margin_right=12, margin_top=46)

        title = Gtk.Label(label="󰐥  Session & Power")
        title.set_xalign(0.0)
        title.get_style_context().add_class("title-label")
        self.card.pack_start(title, False, False, 2)

        div = Gtk.Box()
        div.get_style_context().add_class("divider")
        self.card.pack_start(div, False, False, 2)

        actions = [
            ("󰐥  Power Off", "systemctl poweroff"),
            ("󰜉  Restart", "systemctl reboot"),
            ("󰤄  Suspend", "systemctl suspend"),
            ("󰒲  Hibernate", "systemctl hibernate"),
            ("󰌾  Lock Screen", "hyprlock"),
            ("󰍃  Log Out", "hyprctl dispatch 'hl.dsp.exit()'"),
        ]

        for label, cmd in actions:
            btn = Gtk.Button(label=label)
            btn.get_child().set_xalign(0.0)
            btn.get_style_context().add_class("menu-button")
            btn.connect("clicked", self.make_action_handler(cmd))
            self.card.pack_start(btn, False, False, 1)

    def make_action_handler(self, cmd):
        def handler(widget):
            self.close_popup()
            subprocess.Popen(cmd, shell=True)
        return handler

if __name__ == "__main__":
    menu = PowerMenu()
    menu.show_all()
    Gtk.main()
