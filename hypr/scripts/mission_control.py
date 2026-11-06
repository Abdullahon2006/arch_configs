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
    margin-bottom: 20px;
}

.mc-title {
    color: #7fbbb3;
    font-size: 22px;
    font-weight: 700;
}

.mc-subtitle {
    color: #859289;
    font-size: 13px;
    margin-top: 4px;
}

/* Spaces Bar */
.spaces-box {
    margin: 8px 40px 16px 40px;
    padding: 10px 14px;
    background-color: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
}

.space-card {
    min-width: 140px;
    min-height: 64px;
    margin: 0 6px;
    padding: 10px 14px;
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
    margin: 16px 50px 40px 50px;
}

.win-card {
    min-width: 280px;
    margin: 8px;
    padding: 14px 16px;
    border-radius: 14px;
    background-color: rgba(26, 33, 33, 0.90);
    border: 1px solid rgba(255, 255, 255, 0.12);
    transition: all 0.15s ease;
}

.win-card:hover {
    background-color: rgba(40, 52, 52, 0.95);
    border-color: #a7c080;
}

.win-app-name {
    color: #d3c6aa;
    font-size: 14px;
    font-weight: 700;
}

.win-title {
    color: #9da9a0;
    font-size: 12px;
    font-weight: 400;
    margin-top: 4px;
}

.badge-space {
    background-color: rgba(127, 187, 179, 0.18);
    color: #7fbbb3;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 6px;
}

.badge-minimized {
    background-color: rgba(219, 188, 127, 0.22);
    color: #dbbc7f;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 6px;
}

.win-meta {
    color: #859289;
    font-size: 11px;
}
"""

def get_signature():
    sig = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE", "")
    if sig:
        return sig
    hypr_dir = f"/run/user/{os.getuid()}/hypr"
    if os.path.exists(hypr_dir):
        entries = sorted([d for d in os.listdir(hypr_dir) if os.path.isdir(os.path.join(hypr_dir, d))], reverse=True)
        if entries:
            return entries[0]
    return ""

def hypr_query(endpoint):
    sig = get_signature()
    env = os.environ.copy()
    if sig:
        env["HYPRLAND_INSTANCE_SIGNATURE"] = sig
    try:
        out = subprocess.check_output(f"hyprctl {endpoint} -j", shell=True, stderr=subprocess.DEVNULL, env=env)
        return json.loads(out.decode("utf-8"))
    except Exception:
        return []

def get_app_icon_widget(win_class):
    theme = Gtk.IconTheme.get_default()
    clean_name = win_class.lower().strip()
    candidates = [
        clean_name,
        f"{clean_name}-desktop",
        f"org.gnome.{win_class}",
        f"org.kde.{clean_name}",
        "application-x-executable"
    ]
    if theme:
        for c in candidates:
            if theme.has_icon(c):
                img = Gtk.Image.new_from_icon_name(c, Gtk.IconSize.DND)
                img.set_pixel_size(24)
                return img

    lbl = Gtk.Label(label="")
    lbl.get_style_context().add_class("win-app-name")
    return lbl

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
        header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        header.get_style_context().add_class("mc-header")
        header.set_halign(Gtk.Align.CENTER)

        m_label = Gtk.Label(label="Mission Control")
        m_label.get_style_context().add_class("mc-title")
        s_label = Gtk.Label(label="Switch between active workspaces, spaces and running applications")
        s_label.get_style_context().add_class("mc-subtitle")

        header.pack_start(m_label, False, False, 0)
        header.pack_start(s_label, False, False, 0)
        main_box.pack_start(header, False, False, 0)

        # Spaces / Workspaces Row
        self.spaces_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.spaces_box.get_style_context().add_class("spaces-box")
        self.spaces_box.set_halign(Gtk.Align.CENTER)
        main_box.pack_start(self.spaces_box, False, False, 0)

        # Scrollable container for open windows
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
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
        workspaces = hypr_query("workspaces") or []
        clients = hypr_query("clients") or []
        active_ws_info = hypr_query("activeworkspace") or {}
        active_ws_id = active_ws_info.get("id", 1) if isinstance(active_ws_info, dict) else 1

        # Populate Spaces
        sorted_ws = sorted(workspaces, key=lambda w: w.get("id", 0))
        for ws in sorted_ws:
            ws_id = ws.get("id", 0)
            ws_name = str(ws.get("name", ws_id))
            if ws_name.startswith("special:"):
                continue

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
            win_class = win.get("class", "Application")
            win_ws = str(win.get("workspace", {}).get("name", "1"))

            btn = Gtk.Button()
            btn.get_style_context().add_class("win-card")
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

            # Header row: Icon + App Name + Space Badge
            h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            app_icon = get_app_icon_widget(win_class)
            h_box.pack_start(app_icon, False, False, 0)

            app_lbl = Gtk.Label(label=win_class)
            app_lbl.set_xalign(0.0)
            app_lbl.get_style_context().add_class("win-app-name")
            h_box.pack_start(app_lbl, True, True, 0)

            if win_ws.startswith("special:"):
                badge = Gtk.Label(label="󰘖 Scratchpad")
                badge.get_style_context().add_class("badge-minimized")
            else:
                space_str = win_ws.replace("space:", "Space: ") if win_ws.startswith("space:") else f"WS {win_ws}"
                badge = Gtk.Label(label=space_str)
                badge.get_style_context().add_class("badge-space")
            h_box.pack_end(badge, False, False, 0)

            title_lbl = Gtk.Label(label=title[:42])
            title_lbl.set_xalign(0.0)
            title_lbl.get_style_context().add_class("win-title")

            box.pack_start(h_box, False, False, 0)
            box.pack_start(title_lbl, False, False, 0)
            btn.add(box)

            btn.connect("clicked", self.make_focus_win(address, win_ws))
            self.grid.add(btn)

    def make_switch_ws(self, ws_name, ws_id):
        def handler(w):
            self.close()
            sig = get_signature()
            env = os.environ.copy()
            if sig:
                env["HYPRLAND_INSTANCE_SIGNATURE"] = sig
            target = f"name:{ws_name}" if str(ws_name).startswith("space:") else str(ws_id)
            subprocess.Popen(f"hyprctl dispatch 'hl.dsp.focus({{ workspace = \"{target}\" }})'", shell=True, env=env)
            Gtk.main_quit()
        return handler

    def make_focus_win(self, address, ws_name):
        def handler(w):
            self.close()
            sig = get_signature()
            env = os.environ.copy()
            if sig:
                env["HYPRLAND_INSTANCE_SIGNATURE"] = sig
            if str(ws_name).startswith("special:"):
                # Restore window from scratchpad
                script = os.path.expanduser("~/.config/hypr/scripts/toggle_scratchpad.py")
                subprocess.Popen(f"python3 {script} restore '{address}'", shell=True, env=env)
            else:
                target = f"name:{ws_name}" if str(ws_name).startswith("space:") else str(ws_name)
                subprocess.Popen(f"hyprctl dispatch 'hl.dsp.focus({{ workspace = \"{target}\" }})'; hyprctl dispatch 'hl.dsp.focus({{ window = \"address:{address}\" }})'", shell=True, env=env)
            Gtk.main_quit()
        return handler

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.close()
            Gtk.main_quit()
            return True
        return False

    def on_bg_click(self, widget, event):
        if event.window == self.get_window():
            self.close()
            Gtk.main_quit()
            return True
        return False

if __name__ == "__main__":
    app = MissionControl()
    app.show_all()
    Gtk.main()
