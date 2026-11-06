#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import signal
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
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-top: 1px solid rgba(255, 255, 255, 0.28);
    border-radius: 14px;
    padding: 8px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.55);
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

.section-label {
    color: #859289;
    font-size: 10px;
    padding: 4px 10px 2px 10px;
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

.divider {
    background-color: rgba(255, 255, 255, 0.08);
    min-height: 1px;
    margin: 4px 6px;
}
"""

PID_FILE = "/tmp/waybar_app_menu.pid"

def handle_singleton():
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, "r") as f:
                old_pid = int(f.read().strip())
            os.kill(old_pid, signal.SIGTERM)
            os.remove(PID_FILE)
            sys.exit(0)
        except Exception:
            pass
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

def cleanup_pid():
    if os.path.exists(PID_FILE):
        try:
            os.remove(PID_FILE)
        except Exception:
            pass

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

def run_cmd(cmd):
    sig = get_signature()
    env = os.environ.copy()
    if sig:
        env["HYPRLAND_INSTANCE_SIGNATURE"] = sig
    try:
        res = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL, env=env)
        return res.decode("utf-8").strip()
    except Exception:
        return ""

def dispatch_lua(lua_str):
    run_cmd(f"hyprctl dispatch '{lua_str}'")

def get_cursor_pos():
    out = run_cmd("hyprctl cursorpos -j 2>/dev/null || hyprctl cursorpos")
    if out.startswith("{"):
        try:
            data = json.loads(out)
            return int(data.get("x", 200)), int(data.get("y", 15))
        except Exception:
            pass
    parts = [p.strip() for p in out.split(",")]
    try:
        return int(parts[0]), int(parts[1])
    except Exception:
        return 200, 15

def get_all_clients():
    out = run_cmd("hyprctl clients -j")
    if not out:
        return []
    try:
        clients = json.loads(out)
        return [c for c in clients if c.get("mapped", True) and not c.get("hidden", False)]
    except Exception:
        return []

def resolve_target_window(clients, cursor_x):
    if not clients:
        return None
    if len(clients) == 1:
        return clients[0]
    if cursor_x >= 150:
        task_idx = int((cursor_x - 170) / 38)
        task_idx = max(0, min(task_idx, len(clients) - 1))
        return clients[task_idx]
    sorted_by_focus = sorted(clients, key=lambda c: c.get("focusHistoryID", 999))
    return sorted_by_focus[0]

class AppContextMenu(Gtk.Window):
    def __init__(self):
        super().__init__()
        handle_singleton()

        self.set_name("app-context-menu")

        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_namespace(self, "waybar-app-menu")
        GtkLayerShell.set_exclusive_zone(self, -1)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)

        for edge in [GtkLayerShell.Edge.LEFT, GtkLayerShell.Edge.RIGHT, GtkLayerShell.Edge.TOP, GtkLayerShell.Edge.BOTTOM]:
            GtkLayerShell.set_anchor(self, edge, True)

        self.set_app_paintable(True)
        visual = self.get_screen().get_rgba_visual()
        if visual:
            self.set_visual(visual)

        self.connect("draw", self.on_draw)

        cursor_x, cursor_y = get_cursor_pos()
        card_margin_left = max(10, min(cursor_x - 30, 1620))

        self.apply_css()

        self.card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.card.get_style_context().add_class("context-menu-card")
        self.card.set_halign(Gtk.Align.START)
        self.card.set_valign(Gtk.Align.START)
        self.card.set_margin_start(card_margin_left)
        self.card.set_margin_top(38)
        self.card.set_size_request(240, -1)
        self.add(self.card)

        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.on_button_press)
        self.connect("key-press-event", self.on_key)
        self.connect("destroy", lambda _: cleanup_pid())

        clients = get_all_clients()
        target_win = resolve_target_window(clients, cursor_x)

        if target_win:
            win_class = target_win.get("class", "Application")
            win_title = target_win.get("title", "Active Window")
            win_addr = target_win.get("address", "")
        else:
            win_class = "Desktop"
            win_title = "No Active Application"
            win_addr = ""

        self.target_addr = win_addr
        self.target_class = win_class

        # Header with App Name and Title
        hdr = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        hdr.get_style_context().add_class("app-title-box")
        t_lbl = Gtk.Label(label=win_class)
        t_lbl.set_xalign(0.0)
        t_lbl.get_style_context().add_class("app-title")
        s_lbl = Gtk.Label(label=win_title[:36] if win_title else "Application")
        s_lbl.set_xalign(0.0)
        s_lbl.get_style_context().add_class("app-subtitle")
        hdr.pack_start(t_lbl, False, False, 0)
        hdr.pack_start(s_lbl, False, False, 0)
        self.card.pack_start(hdr, False, False, 0)

        # macOS style: List open windows belonging to this app
        matching_windows = [c for c in clients if c.get("class", "").lower() == win_class.lower()]
        if len(matching_windows) > 1:
            lbl_section = Gtk.Label(label="Open Windows")
            lbl_section.set_xalign(0.0)
            lbl_section.get_style_context().add_class("section-label")
            self.card.pack_start(lbl_section, False, False, 0)

            for mw in matching_windows:
                mw_title = mw.get("title", "Window")[:30]
                mw_addr = mw.get("address", "")
                btn_w = Gtk.Button(label=f"🪟  {mw_title}")
                btn_w.get_child().set_xalign(0.0)
                btn_w.get_style_context().add_class("menu-item")
                btn_w.connect("clicked", self.wrap_cb(lambda a=mw_addr: self.action_focus(a)))
                self.card.pack_start(btn_w, False, False, 0)

            div = Gtk.Box()
            div.get_style_context().add_class("divider")
            self.card.pack_start(div, False, False, 2)

        # Action Items
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
            self.card.pack_start(btn, False, False, 0)

    def on_draw(self, widget, cr):
        cr.set_source_rgba(0, 0, 0, 0.001)
        cr.paint()
        return False

    def on_button_press(self, widget, event):
        alloc = self.card.get_allocation()
        inside = (alloc.x <= event.x <= alloc.x + alloc.width and
                  alloc.y <= event.y <= alloc.y + alloc.height)
        if not inside:
            self.quit_app()
            return True
        return False

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

    def action_focus(self, address):
        if address:
            dispatch_lua(f'hl.dsp.focus({{ window = "address:{address}" }})')

    def action_new_window(self):
        if self.target_class and self.target_class not in ("Desktop", "Application"):
            sig = get_signature()
            env = os.environ.copy()
            if sig:
                env["HYPRLAND_INSTANCE_SIGNATURE"] = sig
            subprocess.Popen(f"gtk-launch '{self.target_class}' 2>/dev/null || setsid '{self.target_class}' &", shell=True, env=env)

    def action_toggle_space(self):
        sig = get_signature()
        env = os.environ.copy()
        if sig:
            env["HYPRLAND_INSTANCE_SIGNATURE"] = sig
        arg = f"'{self.target_addr}'" if self.target_addr else ""
        subprocess.Popen(f"python3 /home/simple/.config/hypr/scripts/toggle_fullscreen_space.py {arg}", shell=True, env=env)

    def action_minimize(self):
        if self.target_addr:
            dispatch_lua(f'hl.dsp.window.move({{ workspace = "special:minimized", address = "{self.target_addr}" }})')
        else:
            dispatch_lua('hl.dsp.window.move({{ workspace = "special:minimized" }})')

    def action_close(self):
        if self.target_addr:
            dispatch_lua(f'hl.dsp.window.close({{ address = "{self.target_addr}" }})')
        else:
            dispatch_lua('hl.dsp.window.close({{}})')

    def on_key(self, w, event):
        if event.keyval == Gdk.KEY_Escape:
            self.quit_app()
            return True
        return False

    def quit_app(self):
        cleanup_pid()
        self.close()
        Gtk.main_quit()

if __name__ == "__main__":
    menu = AppContextMenu()
    menu.show_all()
    Gtk.main()
