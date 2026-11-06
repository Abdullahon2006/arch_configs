#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GtkLayerShell

EVERFOREST_CSS = b"""
* {
    font-family: "JetBrainsMono Nerd Font", "Inter", sans-serif;
    font-size: 13px;
}

window {
    background-color: transparent;
}

.context-menu-card {
    background-color: rgba(20, 26, 26, 0.96);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 14px;
    padding: 8px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
}

.app-title-box {
    padding: 6px 10px 8px 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    margin-bottom: 4px;
}

.app-title {
    color: #7fbbb3;
    font-size: 13px;
    font-weight: 700;
}

.app-subtitle {
    color: #859289;
    font-size: 11px;
    margin-top: 2px;
}

.menu-item {
    padding: 7px 12px;
    border-radius: 8px;
    background: transparent;
    color: #d3c6aa;
    border: none;
    transition: background 0.12s ease;
}

.menu-item:hover {
    background-color: rgba(255, 255, 255, 0.09);
    color: #ffffff;
}

.menu-item.danger:hover {
    background-color: rgba(230, 126, 128, 0.18);
    color: #e67e80;
}
"""

def get_cursor_x():
    try:
        out = subprocess.check_output("hyprctl cursorpos -j 2>/dev/null || hyprctl cursorpos", shell=True).decode("utf-8").strip()
        if out.startswith("{"):
            data = json.loads(out)
            return int(data.get("x", 120))
        parts = [p.strip() for p in out.split(",")]
        return int(parts[0])
    except Exception:
        return 120

def get_active_win():
    try:
        out = subprocess.check_output("hyprctl activewindow -j", shell=True).decode("utf-8").strip()
        return json.loads(out)
    except Exception:
        return {}

class AppContextMenu(Gtk.Window):
    def __init__(self):
        super().__init__()
        self.set_name("app-context-menu")

        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)

        # Position at mouse cursor X directly under top bar
        cursor_x = get_cursor_x()
        margin_left = max(10, min(cursor_x - 30, 1650))

        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, True)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.TOP, 38)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.LEFT, margin_left)

        self.apply_css()

        self.connect("focus-out-event", lambda w, e: self.quit_app())
        self.connect("key-press-event", self.on_key)

        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        card.get_style_context().add_class("context-menu-card")
        self.add(card)

        win_info = get_active_win()
        win_class = win_info.get("class", "Application")
        win_title = win_info.get("title", "Active Window")

        # Header
        hdr = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        hdr.get_style_context().add_class("app-title-box")
        t_lbl = Gtk.Label(label=win_class)
        t_lbl.set_xalign(0.0)
        t_lbl.get_style_context().add_class("app-title")
        s_lbl = Gtk.Label(label=win_title[:32])
        s_lbl.set_xalign(0.0)
        s_lbl.get_style_context().add_class("app-subtitle")
        hdr.pack_start(t_lbl, False, False, 0)
        hdr.pack_start(s_lbl, False, False, 0)
        card.pack_start(hdr, False, False, 0)

        # Items
        items = [
            ("➕  New Window", self.action_new_window, False),
            ("⤢  Toggle Fullscreen Space", self.action_toggle_space, False),
            ("󰘖  Minimize to Scratchpad", self.action_minimize, False),
            ("󰅖  Close Window", self.action_close, True),
        ]

        for label, callback, is_danger in items:
            btn = Gtk.Button(label=label)
            btn.get_child().set_xalign(0.0)
            btn.get_style_context().add_class("menu-item")
            if is_danger:
                btn.get_style_context().add_class("danger")
            btn.connect("clicked", self.wrap_cb(callback))
            card.pack_start(btn, False, False, 0)

    def apply_css(self):
        screen = Gdk.Screen.get_default()
        provider = Gtk.CssProvider()
        provider.load_from_data(EVERFOREST_CSS)
        Gtk.StyleContext.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def wrap_cb(self, cb):
        def handler(w):
            cb()
            self.quit_app()
        return handler

    def action_new_window(self):
        win = get_active_win()
        w_class = win.get("class", "")
        if w_class:
            subprocess.Popen(f"gtk-launch '{w_class}' 2>/dev/null || setsid '{w_class}' &", shell=True)

    def action_toggle_space(self):
        subprocess.Popen("python3 /home/simple/.config/hypr/scripts/toggle_fullscreen_space.py", shell=True)

    def action_minimize(self):
        subprocess.Popen("hyprctl dispatch movetoworkspace special:minimized", shell=True)

    def action_close(self):
        subprocess.Popen("hyprctl dispatch killactive", shell=True)

    def on_key(self, w, event):
        if event.keyval == Gdk.KEY_Escape:
            self.quit_app()
            return True
        return False

    def quit_app(self):
        self.close()
        Gtk.main_quit()

if __name__ == "__main__":
    menu = AppContextMenu()
    menu.show_all()
    Gtk.main()
