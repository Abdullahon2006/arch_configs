#!/usr/bin/env python3
import json
import subprocess
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, GLib
from popup import BasePopup

class VolumeMenu(BasePopup):
    def __init__(self):
        super().__init__(name="volume", width=380, margin_right=12, margin_top=46)

        # Header Title
        title = Gtk.Label(label="󰕾  Audio & Volume")
        title.set_xalign(0.0)
        title.get_style_context().add_class("title-label")
        self.card.pack_start(title, False, False, 2)

        # -------------------------------------------------------------
        # Output (Sink) Section
        # -------------------------------------------------------------
        self.sink_vol, self.sink_muted = self.get_sink_info()

        sink_header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.sink_lbl = Gtk.Label(label=self.get_sink_label())
        self.sink_lbl.set_xalign(0.0)
        sink_header_box.pack_start(self.sink_lbl, True, True, 0)

        mute_action = "Unmute" if self.sink_muted else "Mute"
        self.sink_mute_btn = Gtk.Button(label=f"[ {mute_action} ]")
        self.sink_mute_btn.get_style_context().add_class("tool-button")
        self.sink_mute_btn.connect("clicked", self.on_toggle_sink_mute)
        sink_header_box.pack_end(self.sink_mute_btn, False, False, 0)
        self.card.pack_start(sink_header_box, False, False, 2)

        # Output Slider
        sink_adj = Gtk.Adjustment(
            value=min(int(self.sink_vol * 100), 100),
            lower=0,
            upper=100,
            step_increment=1,
            page_increment=5
        )
        self.sink_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=sink_adj)
        self.sink_scale.set_draw_value(False)
        self.sink_scale.connect("value-changed", self.on_sink_scale_changed)
        self.card.pack_start(self.sink_scale, False, False, 4)

        # -------------------------------------------------------------
        # Input (Source / Mic) Section
        # -------------------------------------------------------------
        self.src_vol, self.src_muted = self.get_source_info()

        src_header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.src_lbl = Gtk.Label(label=self.get_source_label())
        self.src_lbl.set_xalign(0.0)
        src_header_box.pack_start(self.src_lbl, True, True, 0)

        src_mute_action = "Unmute" if self.src_muted else "Mute"
        self.src_mute_btn = Gtk.Button(label=f"[ {src_mute_action} ]")
        self.src_mute_btn.get_style_context().add_class("tool-button")
        self.src_mute_btn.connect("clicked", self.on_toggle_source_mute)
        src_header_box.pack_end(self.src_mute_btn, False, False, 0)
        self.card.pack_start(src_header_box, False, False, 2)

        # Input Slider
        src_adj = Gtk.Adjustment(
            value=min(int(self.src_vol * 100), 100),
            lower=0,
            upper=100,
            step_increment=1,
            page_increment=5
        )
        self.src_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=src_adj)
        self.src_scale.set_draw_value(False)
        self.src_scale.connect("value-changed", self.on_source_scale_changed)
        self.card.pack_start(self.src_scale, False, False, 4)

        # Divider
        div = Gtk.Box()
        div.get_style_context().add_class("divider")
        self.card.pack_start(div, False, False, 4)

        # -------------------------------------------------------------
        # Output Devices Section
        # -------------------------------------------------------------
        devs_lbl = Gtk.Label(label="Output Device")
        devs_lbl.set_xalign(0.0)
        devs_lbl.get_style_context().add_class("subtitle-label")
        self.card.pack_start(devs_lbl, False, False, 2)

        self.devs_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        self.card.pack_start(self.devs_box, False, False, 2)
        self.populate_output_devices()

        # Divider
        div2 = Gtk.Box()
        div2.get_style_context().add_class("divider")
        self.card.pack_start(div2, False, False, 4)

        # -------------------------------------------------------------
        # Tools row (Pavucontrol launcher)
        # -------------------------------------------------------------
        pavu_btn = Gtk.Button(label="⚙  Open Audio Mixer (Pavucontrol)")
        pavu_btn.get_style_context().add_class("tool-button")
        pavu_btn.connect("clicked", self.on_open_pavucontrol)
        self.card.pack_start(pavu_btn, False, False, 2)

    def get_sink_label(self):
        icon = "󰖁" if self.sink_muted else ("󰕾" if self.sink_vol >= 0.6 else ("󰖀" if self.sink_vol >= 0.2 else "󰕿"))
        pct = int(self.sink_vol * 100)
        status = " (Muted)" if self.sink_muted else ""
        return f"{icon}  Speaker: {pct}%{status}"

    def get_source_label(self):
        icon = "󰍭" if self.src_muted else "󰍬"
        pct = int(self.src_vol * 100)
        status = " (Muted)" if self.src_muted else ""
        return f"{icon}  Microphone: {pct}%{status}"

    def get_sink_info(self):
        try:
            out = subprocess.check_output(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"], text=True)
            parts = out.strip().split()
            if len(parts) >= 2:
                vol = float(parts[1])
                muted = "[MUTED]" in out
                return vol, muted
        except Exception:
            pass
        return 0.5, False

    def get_source_info(self):
        try:
            out = subprocess.check_output(["wpctl", "get-volume", "@DEFAULT_AUDIO_SOURCE@"], text=True)
            parts = out.strip().split()
            if len(parts) >= 2:
                vol = float(parts[1])
                muted = "[MUTED]" in out
                return vol, muted
        except Exception:
            pass
        return 1.0, False

    def on_sink_scale_changed(self, scale):
        val = scale.get_value()
        self.sink_vol = val / 100.0
        subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{self.sink_vol:.2f}"])
        self.sink_lbl.set_text(self.get_sink_label())

    def on_source_scale_changed(self, scale):
        val = scale.get_value()
        self.src_vol = val / 100.0
        subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SOURCE@", f"{self.src_vol:.2f}"])
        self.src_lbl.set_text(self.get_source_label())

    def on_toggle_sink_mute(self, btn):
        subprocess.run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"])
        self.sink_vol, self.sink_muted = self.get_sink_info()
        mute_action = "Unmute" if self.sink_muted else "Mute"
        self.sink_mute_btn.set_label(f"[ {mute_action} ]")
        self.sink_lbl.set_text(self.get_sink_label())

    def on_toggle_source_mute(self, btn):
        subprocess.run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SOURCE@", "toggle"])
        self.src_vol, self.src_muted = self.get_source_info()
        src_mute_action = "Unmute" if self.src_muted else "Mute"
        self.src_mute_btn.set_label(f"[ {src_mute_action} ]")
        self.src_lbl.set_text(self.get_source_label())

    def get_output_devices(self):
        devices = []
        try:
            sinks_raw = subprocess.check_output(["pactl", "-f", "json", "list", "sinks"], text=True)
            sinks = json.loads(sinks_raw)
            info_raw = subprocess.check_output(["pactl", "info"], text=True)
            default_sink = ""
            for line in info_raw.splitlines():
                if line.startswith("Default Sink:"):
                    default_sink = line.split(":", 1)[1].strip()

            for s in sinks:
                name = s.get("name", "")
                desc = s.get("description", name)
                is_default = (name == default_sink)

                # Icon deduction
                desc_lower = desc.lower()
                name_lower = name.lower()
                if "bluez" in name_lower or "bluetooth" in desc_lower:
                    icon = "󰂱"
                elif "headphone" in desc_lower or "headset" in desc_lower:
                    icon = "󰋋"
                elif "hdmi" in desc_lower or "displayport" in desc_lower:
                    icon = "󰡁"
                else:
                    icon = "󰓃"

                devices.append({
                    "name": name,
                    "desc": desc,
                    "icon": icon,
                    "active": is_default,
                })
        except Exception:
            pass
        return devices

    def populate_output_devices(self):
        for child in self.devs_box.get_children():
            self.devs_box.remove(child)

        devices = self.get_output_devices()
        for dev in devices:
            btn = Gtk.Button()
            btn.get_style_context().add_class("menu-button")
            if dev["active"]:
                btn.get_style_context().add_class("active-item")

            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            icon_lbl = Gtk.Label(label=dev["icon"])
            box.pack_start(icon_lbl, False, False, 0)

            name_lbl = Gtk.Label(label=dev["desc"])
            name_lbl.set_xalign(0.0)
            box.pack_start(name_lbl, True, True, 0)

            if dev["active"]:
                tag_lbl = Gtk.Label(label="✓ (Active)")
                tag_lbl.get_style_context().add_class("subtitle-label")
                box.pack_end(tag_lbl, False, False, 0)

            btn.add(box)
            btn.connect("clicked", self.on_select_device, dev["name"])
            self.devs_box.pack_start(btn, False, False, 0)

        self.devs_box.show_all()

    def on_select_device(self, btn, sink_name):
        subprocess.run(["pactl", "set-default-sink", sink_name])
        self.sink_vol, self.sink_muted = self.get_sink_info()
        self.sink_scale.set_value(min(int(self.sink_vol * 100), 100))
        self.sink_lbl.set_text(self.get_sink_label())
        self.populate_output_devices()

    def on_open_pavucontrol(self, btn):
        self.close_popup()
        subprocess.Popen(["pavucontrol"])

if __name__ == "__main__":
    menu = VolumeMenu()
    menu.show_all()
    Gtk.main()
