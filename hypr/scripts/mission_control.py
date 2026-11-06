#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GtkLayerShell

MISSION_CSS = b"""
* {
    font-family: "JetBrainsMono Nerd Font", "Inter", sans-serif;
}

window#mission-control {
    background-color: rgba(14, 18, 18, 0.88);
}

.mc-header {
    margin-top: 36px;
    margin-bottom: 24px;
}

.mc-title {
    color: #7fbbb3;
    font-size: 20px;
    font-weight: 700;
}

.mc-subtitle {
    color: #859289;
    font-size: 13px;
    margin-top: 4px;
}

/* Spaces Bar */
.spaces-box {
    margin: 12px 40px;
    padding: 10px;
    background-color: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
}

.space-card {
    min-width: 140px;
    min-height: 70px;
    margin: 0 6px;
    padding: 10px;
    border-radius: 12px;
    background-color: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.10);
    color: #d3c6aa;
    transition: all 0.15s ease;
}

.space-card:hover {
    background-color: rgba(127, 187, 179, 0.20);
    border-color: #7fbbb3;
}

.space-card.active {
    background-color: rgba(127, 187, 179, 0.35);
    border: 2px solid #7fbbb3;
    color: #ffffff;
}

/* Windows Grid */
.windows-container {
    margin: 20px 60px 40px 60px;
}

.win-card {
    min-width: 280px;
    margin: 10px;
    padding: 16px;
    border-radius: 14px;
    background-color: rgba(26, 33, 33, 0.90);
    border: 1px solid rgba(255, 255, 255, 0.12);
    transition: all 0.15s ease;
}

.win-card:hover {
    background-color: rgba(40, 52, 52, 0.95);
    border-color: #a7c080;
}

.win-title {
    color: #d3c6aa;
    font-size: 13.5px;
    font-weight: 600;
}

.win-meta {
    color: #859289;
    font-size: 11px;
    margin-top: 6px;
}
"""

def hypr_query(endpoint):
    try:
        out = subprocess.check_output(f"hyprctl {endpoint} -j", shell=True, stderr=subprocess.DEVNULL)
        return json.loads(out.decode("utf-8"))
    except Exception:
        return []

class MissionControl(Gtk.Window):
    def __init__(self):
        super().__init__()
        self.set_name("mission-control")

        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.EXCLUSIVE)
        for edge in (GtkLayerShell.Edge.TOP, GtkLayerShell.Edge.BOTTOM, GtkLayerShell.Edge.LEFT, GtkLayerShell.Edge.RIGHT):
            GtkLayerShell.set_anchor(self, edge, True)

        self.apply_css()

        self.connect("key-press-event", self.on_key_press)
        self.connect("button-press-event", self.on_bg_click)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(main_box)

        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        header.get_style_context().add_class("mc-header")
        t_label = Gtk.Label(label="󰨡  Mission Control & Spaces")
        t_label.get_style_context().add_class("mc-title")
        s_label = Gtk.Label(label="Switch between active workspaces, spaces and running applications")
        s_label.get_style_context().add_class("mc-subtitle")
        header.pack_start(t_label, False, False, 0)
        header.pack_start(s_label, False, False, 0)
        main_box.pack_start(header, False, False, 0)

        # Spaces Bar
        self.spaces_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.spaces_box.get_style_context().add_class("spaces-box")
        self.spaces_box.set_halign(Gtk.Align.CENTER)
        main_box.pack_start(self.spaces_box, False, False, 0)

        # Scrolled Windows Grid
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.set_vexpand(True)
        main_box.pack_start(scroller, True, True, 0)

        self.grid = Gtk.FlowBox()
        self.grid.get_style_context().add_class("windows-container")
        self.grid.set_valign(Gtk.Align.START)
        self.grid.set_halign(Gtk.Align.CENTER)
        self.grid.set_max_children_per_line(4)
        self.grid.set_selection_mode(Gtk.SelectionMode.NONE)
        scroller.add(self.grid)

        self.populate_data()

    def apply_css(self):
        screen = Gdk.Screen.get_default()
        provider = Gtk.CssProvider()
        provider.load_from_data(MISSION_CSS)
        Gtk.StyleContext.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def populate_data(self):
        workspaces = hypr_query("workspaces")
        clients = hypr_query("clients")
        active_ws_info = hypr_query("activeworkspace")
        active_ws_id = active_ws_info.get("id", 1) if isinstance(active_ws_info, dict) else 1

        # Populate Spaces
        sorted_ws = sorted(workspaces, key=lambda w: w.get("id", 0))
        for ws in sorted_ws:
            ws_id = ws.get("id", 0)
            ws_name = str(ws.get("name", ws_id))
            is_active = (ws_id == active_ws_id)

            card = Gtk.Button()
            card.get_style_context().add_class("space-card")
            if is_active:
                card.get_style_context().add_class("active")

            display_name = f"Space: {ws_name.replace('space:', '')}" if ws_name.startswith("space:") else f"Workspace {ws_name}"
            card_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            lbl = Gtk.Label(label=f"<b>{display_name}</b>")
            lbl.set_use_markup(True)
            cnt = Gtk.Label(label=f"{ws.get('windows', 0)} windows")
            cnt.get_style_context().add_class("win-meta")
            card_box.pack_start(lbl, False, False, 0)
            card_box.pack_start(cnt, False, False, 0)
            card.add(card_box)

            card.connect("clicked", self.make_switch_ws(ws_name, ws_id))
            self.spaces_box.pack_start(card, False, False, 0)

        # Populate Windows
        for win in clients:
            address = win.get("address", "")
            title = win.get("title", "Window")
            win_class = win.get("class", "app")
            win_ws = win.get("workspace", {}).get("name", "1")

            btn = Gtk.Button()
            btn.get_style_context().add_class("win-card")
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

            title_lbl = Gtk.Label(label=f"<b>{title[:38]}</b>")
            title_lbl.set_use_markup(True)
            title_lbl.set_xalign(0.0)
            title_lbl.get_style_context().add_class("win-title")

            meta_lbl = Gtk.Label(label=f"󰖲  {win_class}  ·  Space: {win_ws}")
            meta_lbl.set_xalign(0.0)
            meta_lbl.get_style_context().add_class("win-meta")

            box.pack_start(title_lbl, False, False, 0)
            box.pack_start(meta_lbl, False, False, 0)
            btn.add(box)

            btn.connect("clicked", self.make_focus_win(address, win_ws))
            self.grid.add(btn)

    def make_switch_ws(self, ws_name, ws_id):
        def handler(w):
            self.close()
            target = f"name:{ws_name}" if str(ws_name).startswith("space:") else str(ws_id)
            subprocess.Popen(f"hyprctl dispatch 'hl.dsp.focus({{ workspace = \"{target}\" }})'", shell=True)
            Gtk.main_quit()
        return handler

    def make_focus_win(self, address, ws_name):
        def handler(w):
            self.close()
            subprocess.Popen(f"hyprctl dispatch 'hl.dsp.focus({{ window = \"address:{address}\" }})'", shell=True)
            Gtk.main_quit()
        return handler

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.close()
            Gtk.main_quit()
            return True
        return False

    def on_bg_click(self, widget, event):
        # clicking background closes
        if event.window == self.get_window():
            self.close()
            Gtk.main_quit()
            return True
        return False

if __name__ == "__main__":
    app = MissionControl()
    app.show_all()
    Gtk.main()
