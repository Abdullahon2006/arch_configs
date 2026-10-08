#!/usr/bin/env python3
import os
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

.popup-card {
    background-color: rgba(20, 26, 26, 0.94);
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-top: 1px solid rgba(255, 255, 255, 0.28);
    border-radius: 18px;
    padding: 14px;
    box-shadow: none;
}

.title-label {
    color: #7fbbb3;
    font-weight: 700;
    font-size: 14px;
    margin-bottom: 4px;
}

.subtitle-label {
    color: #859289;
    font-size: 11.5px;
}

.divider {
    background-color: rgba(255, 255, 255, 0.10);
    min-height: 1px;
    margin: 8px 0px;
}

.menu-button {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 10px;
    padding: 8px 12px;
    color: #d3c6aa;
    transition: all 0.15s ease;
}

.menu-button:hover {
    background-color: #7fbbb3;
    color: #1e2524;
}

.active-item {
    background-color: rgba(127, 187, 179, 0.20);
    border: 1px solid rgba(127, 187, 179, 0.40);
    color: #7fbbb3;
    font-weight: 700;
}

.active-item:hover {
    background-color: #7fbbb3;
    color: #1e2524;
}

.tool-button {
    background-color: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 8px;
    padding: 6px 10px;
    color: #d3c6aa;
    font-size: 11.5px;
    transition: all 0.15s ease;
}

.tool-button:hover {
    background-color: #7fbbb3;
    color: #1e2524;
}

.search-entry {
    background-color: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 10px;
    padding: 7px 10px;
    color: #d3c6aa;
    margin-bottom: 6px;
}

.search-entry:focus {
    border-color: #7fbbb3;
}

scrollbar slider {
    background-color: rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    min-width: 6px;
}

scrollbar slider:hover {
    background-color: rgba(127, 187, 179, 0.5);
}
"""

def handle_singleton(name):
    pid_file = f"/tmp/waybar_popup_{name}.pid"
    if os.path.exists(pid_file):
        try:
            with open(pid_file, "r") as f:
                old_pid = int(f.read().strip())
            os.kill(old_pid, signal.SIGTERM)
            os.remove(pid_file)
            sys.exit(0)
        except (ProcessLookupError, ValueError):
            pass
        except Exception:
            pass

    # Close any other waybar popups so only one is open at a time
    for f in os.listdir("/tmp"):
        if f.startswith("waybar_popup_") and f.endswith(".pid"):
            try:
                with open(f"/tmp/{f}", "r") as pf:
                    p = int(pf.read().strip())
                os.kill(p, signal.SIGTERM)
                os.remove(f"/tmp/{f}")
            except Exception:
                pass

    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))

def cleanup_pid(name):
    pid_file = f"/tmp/waybar_popup_{name}.pid"
    if os.path.exists(pid_file):
        try:
            os.remove(pid_file)
        except Exception:
            pass

class BasePopup(Gtk.Window):
    def __init__(self, name="popup", width=380, margin_right=12, margin_top=46):
        super().__init__()
        self.name = name
        self.width = width
        self.margin_right = margin_right
        self.margin_top = margin_top

        handle_singleton(self.name)

        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_namespace(self, "waybar-popup")
        GtkLayerShell.set_exclusive_zone(self, -1)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)

        for edge in [GtkLayerShell.Edge.LEFT, GtkLayerShell.Edge.RIGHT, GtkLayerShell.Edge.TOP, GtkLayerShell.Edge.BOTTOM]:
            GtkLayerShell.set_anchor(self, edge, True)

        self.set_app_paintable(True)
        visual = self.get_screen().get_rgba_visual()
        if visual:
            self.set_visual(visual)

        self.connect("draw", self.on_draw)

        # Load style
        screen = self.get_screen()
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(EVERFOREST_CSS)
        Gtk.StyleContext.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        # Main Card Box pinned to top-right
        self.card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.card.get_style_context().add_class("popup-card")
        self.card.set_halign(Gtk.Align.END)
        self.card.set_valign(Gtk.Align.START)
        self.card.set_margin_end(self.margin_right)
        self.card.set_margin_top(self.margin_top)
        self.card.set_size_request(self.width, -1)
        self.add(self.card)

        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.connect("button-press-event", self.on_button_press)
        self.connect("key-press-event", self.on_key_press)
        self.connect("destroy", lambda _: cleanup_pid(self.name))

    def on_draw(self, widget, cr):
        # Micro-alpha paint creates a valid Wayland surface buffer so the entire screen gets hit-testing
        cr.set_source_rgba(0, 0, 0, 0.001)
        cr.paint()
        return False

    def on_button_press(self, widget, event):
        alloc = self.card.get_allocation()
        inside = (alloc.x <= event.x <= alloc.x + alloc.width and
                  alloc.y <= event.y <= alloc.y + alloc.height)
        if not inside:
            self.close_popup()
            return True
        return False

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.close_popup()
            return True
        return False

    def close_popup(self):
        cleanup_pid(self.name)
        Gtk.main_quit()
