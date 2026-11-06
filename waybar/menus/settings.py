#!/usr/bin/env python3
import json
import os
import subprocess
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk
from popup import BasePopup

SETTINGS_FILE = os.path.expanduser("~/.config/hypr/settings.json")

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {"taskbar_scope": "workspace", "fullscreen_bar": "visible"}
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"taskbar_scope": "workspace", "fullscreen_bar": "visible"}

def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=2)

class SettingsMenu(BasePopup):
    def __init__(self):
        super().__init__(name="settings", width=320, margin_right=80, margin_top=42)
        self.settings = load_settings()

        title = Gtk.Label(label="󰒓  Desktop & Window Preferences")
        title.set_xalign(0.0)
        title.get_style_context().add_class("title-label")
        self.card.pack_start(title, False, False, 2)

        subtitle = Gtk.Label(label="Live toggles for top bar, spaces & session")
        subtitle.set_xalign(0.0)
        subtitle.get_style_context().add_class("subtitle-label")
        self.card.pack_start(subtitle, False, False, 2)

        div1 = Gtk.Box()
        div1.get_style_context().add_class("divider")
        self.card.pack_start(div1, False, False, 4)

        # Taskbar Scope Toggle
        self.btn_taskbar = Gtk.Button()
        self.update_taskbar_label()
        self.btn_taskbar.get_child().set_xalign(0.0)
        self.btn_taskbar.get_style_context().add_class("menu-button")
        self.btn_taskbar.connect("clicked", self.toggle_taskbar_scope)
        self.card.pack_start(self.btn_taskbar, False, False, 2)

        # Fullscreen Bar Toggle
        self.btn_fs = Gtk.Button()
        self.update_fs_label()
        self.btn_fs.get_child().set_xalign(0.0)
        self.btn_fs.get_style_context().add_class("menu-button")
        self.btn_fs.connect("clicked", self.toggle_fs_bar)
        self.card.pack_start(self.btn_fs, False, False, 2)

        div2 = Gtk.Box()
        div2.get_style_context().add_class("divider")
        self.card.pack_start(div2, False, False, 4)

        # Wallpaper Quick Picker
        btn_wall = Gtk.Button(label="🖼️  Select Wallpaper (sharedDavid)")
        btn_wall.get_child().set_xalign(0.0)
        btn_wall.get_style_context().add_class("menu-button")
        btn_wall.connect("clicked", self.open_wallpaper_picker)
        self.card.pack_start(btn_wall, False, False, 2)

        # Switch User Button
        btn_switch = Gtk.Button(label="👥  Switch User (Keep Session Active)")
        btn_switch.get_child().set_xalign(0.0)
        btn_switch.get_style_context().add_class("menu-button")
        btn_switch.connect("clicked", self.switch_user)
        self.card.pack_start(btn_switch, False, False, 2)

        # Lock Screen Button
        btn_lock = Gtk.Button(label="󰌾  Lock Screen (macOS / Win Style)")
        btn_lock.get_child().set_xalign(0.0)
        btn_lock.get_style_context().add_class("menu-button")
        btn_lock.connect("clicked", self.lock_screen)
        self.card.pack_start(btn_lock, False, False, 2)

    def update_taskbar_label(self):
        scope = self.settings.get("taskbar_scope", "workspace")
        state_txt = "Current Workspace" if scope == "workspace" else "All Workspaces"
        self.btn_taskbar.set_label(f"🪟  Taskbar Scope:  <b>{state_txt}</b>")
        self.btn_taskbar.get_child().set_use_markup(True)

    def toggle_taskbar_scope(self, widget):
        curr = self.settings.get("taskbar_scope", "workspace")
        new_val = "all" if curr == "workspace" else "workspace"
        self.settings["taskbar_scope"] = new_val
        save_settings(self.settings)
        self.update_taskbar_label()
        subprocess.Popen("pkill -SIGUSR2 waybar || true", shell=True)

    def update_fs_label(self):
        mode = self.settings.get("fullscreen_bar", "visible")
        state_txt = "Keep Visible" if mode == "visible" else "Auto-Hide"
        self.btn_fs.set_label(f"⤢  Fullscreen Bar:  <b>{state_txt}</b>")
        self.btn_fs.get_child().set_use_markup(True)

    def toggle_fs_bar(self, widget):
        curr = self.settings.get("fullscreen_bar", "visible")
        new_val = "autohide" if curr == "visible" else "visible"
        self.settings["fullscreen_bar"] = new_val
        save_settings(self.settings)
        self.update_fs_label()

    def open_wallpaper_picker(self, widget):
        self.close_popup()
        subprocess.Popen("bash ~/.config/rofi/theme-switcher.sh", shell=True)

    def switch_user(self, widget):
        self.close_popup()
        subprocess.Popen("qdbus org.freedesktop.DisplayManager /org/freedesktop/DisplayManager/Seat0 org.freedesktop.DisplayManager.Seat.SwitchToGreeter 2>/dev/null || loginctl activate 6 || true", shell=True)

    def lock_screen(self, widget):
        self.close_popup()
        subprocess.Popen("python3 ~/.config/hypr/scripts/lockscreen.py", shell=True)

if __name__ == "__main__":
    menu = SettingsMenu()
    menu.show_all()
    Gtk.main()
