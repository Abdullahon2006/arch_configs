#!/usr/bin/env python3
import glob
import subprocess
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk
from popup import BasePopup

class BatteryMenu(BasePopup):
    def __init__(self):
        super().__init__(name="battery", width=300, margin_right=12, margin_top=46)

        cap, status = self.get_battery_info()
        current_profile = self.get_current_profile()

        # Header
        title = Gtk.Label(label=f"󰂄  Battery: {cap}% [{status}]")
        title.set_xalign(0.0)
        title.get_style_context().add_class("title-label")
        self.card.pack_start(title, False, False, 2)

        sub = Gtk.Label(label="Power Profile Selector")
        sub.set_xalign(0.0)
        sub.get_style_context().add_class("subtitle-label")
        self.card.pack_start(sub, False, False, 0)

        div = Gtk.Box()
        div.get_style_context().add_class("divider")
        self.card.pack_start(div, False, False, 3)

        profiles = [
            ("performance", "󰓅  Performance"),
            ("balanced",    "󰾆  Balanced"),
            ("power-saver", "󰾆  Power Saver"),
        ]

        for prof_id, label in profiles:
            is_active = (prof_id == current_profile)
            display_text = f"{label}  (Active) ✓" if is_active else label
            btn = Gtk.Button(label=display_text)
            btn.get_child().set_xalign(0.0)
            btn.get_style_context().add_class("menu-button")
            if is_active:
                btn.get_style_context().add_class("active-item")
            btn.connect("clicked", self.make_profile_handler(prof_id, label.split(" ")[-1]))
            self.card.pack_start(btn, False, False, 2)

    def get_battery_info(self):
        cap = "100"
        status = "Unknown"
        for p in glob.glob("/sys/class/power_supply/BAT*"):
            try:
                with open(f"{p}/capacity", "r") as f:
                    cap = f.read().strip()
                with open(f"{p}/status", "r") as f:
                    status = f.read().strip()
                break
            except Exception:
                pass
        return cap, status

    def get_current_profile(self):
        try:
            res = subprocess.check_output(["powerprofilesctl", "get"], text=True).strip()
            return res
        except Exception:
            return "balanced"

    def make_profile_handler(self, prof_id, prof_name):
        def handler(widget):
            self.close_popup()
            subprocess.run(["powerprofilesctl", "set", prof_id])
            subprocess.Popen([
                "notify-send", "Power Profile", f"Switched to {prof_name}",
                "-i", "preferences-system-power"
            ])
        return handler

if __name__ == "__main__":
    menu = BatteryMenu()
    menu.show_all()
    Gtk.main()
