#!/usr/bin/env python3
import subprocess
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Pango
from popup import BasePopup

class BluetoothMenu(BasePopup):
    def __init__(self):
        super().__init__(name="bluetooth", width=390, margin_right=12, margin_top=46)

        is_powered = self.get_power_status()

        # Header Title
        title = Gtk.Label(label="󰂯  Bluetooth")
        title.set_xalign(0.0)
        title.get_style_context().add_class("title-label")
        self.card.pack_start(title, False, False, 2)

        # Toggle Card
        toggle_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        toggle_box.get_style_context().add_class("tool-button")
        
        status_text = "󰂲  Bluetooth : Enabled" if is_powered else "󰂯  Bluetooth : Disabled"
        status_lbl = Gtk.Label(label=status_text)
        status_lbl.set_xalign(0.0)
        toggle_box.pack_start(status_lbl, True, True, 6)

        btn_action = "Turn OFF" if is_powered else "Turn ON"
        toggle_btn = Gtk.Button(label=f"[ {btn_action} ]")
        toggle_btn.get_style_context().add_class("tool-button")
        toggle_btn.connect("clicked", self.on_toggle_power, is_powered)
        toggle_box.pack_end(toggle_btn, False, False, 4)
        self.card.pack_start(toggle_box, False, False, 3)

        if is_powered:
            # Action tools row
            tools_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            
            scan_btn = Gtk.Button(label="󰑐  Scan (10s)")
            scan_btn.get_style_context().add_class("tool-button")
            scan_btn.connect("clicked", self.on_scan)
            tools_box.pack_start(scan_btn, True, True, 0)

            gui_btn = Gtk.Button(label="⚙  Blueman GUI")
            gui_btn.get_style_context().add_class("tool-button")
            gui_btn.connect("clicked", self.on_open_gui)
            tools_box.pack_start(gui_btn, True, True, 0)

            self.card.pack_start(tools_box, False, False, 3)

            # Divider
            div = Gtk.Box()
            div.get_style_context().add_class("divider")
            self.card.pack_start(div, False, False, 4)

            # Paired Devices Header
            devices_lbl = Gtk.Label(label="Paired Devices")
            devices_lbl.set_xalign(0.0)
            devices_lbl.get_style_context().add_class("subtitle-label")
            self.card.pack_start(devices_lbl, False, False, 2)

            # Scrolled list of devices
            devices = self.get_paired_devices()
            if devices:
                scroll = Gtk.ScrolledWindow()
                scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
                scroll.set_min_content_height(min(len(devices) * 38, 220))

                dev_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
                for dev in devices:
                    row = self.create_device_row(dev)
                    dev_box.pack_start(row, False, False, 1)

                scroll.add(dev_box)
                self.card.pack_start(scroll, True, True, 2)
            else:
                empty = Gtk.Label(label="No paired devices found")
                empty.set_xalign(0.0)
                empty.get_style_context().add_class("subtitle-label")
                self.card.pack_start(empty, False, False, 6)

    def get_power_status(self):
        try:
            out = subprocess.check_output(["bluetoothctl", "show"], text=True)
            return "Powered: yes" in out
        except Exception:
            return False

    def get_paired_devices(self):
        devices = []
        try:
            out = subprocess.check_output(["bluetoothctl", "devices", "Paired"], text=True)
            for line in out.strip().splitlines():
                if not line.startswith("Device"):
                    continue
                parts = line.split(" ", 2)
                if len(parts) >= 3:
                    mac = parts[1]
                    name = parts[2]
                    # Check if connected
                    info = subprocess.check_output(["bluetoothctl", "info", mac], text=True)
                    connected = "Connected: yes" in info
                    devices.append({"mac": mac, "name": name, "connected": connected})
        except Exception:
            pass
        return devices

    def create_device_row(self, dev):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row.get_style_context().add_class("menu-button")

        icon_str = "󰂱" if dev["connected"] else "󰂯"
        icon_lbl = Gtk.Label(label=icon_str)
        row.pack_start(icon_lbl, False, False, 0)

        name_lbl = Gtk.Label(label=dev["name"])
        name_lbl.set_xalign(0.0)
        name_lbl.set_ellipsize(Pango.EllipsizeMode.END)
        row.pack_start(name_lbl, True, True, 0)

        status_text = "Connected" if dev["connected"] else "Paired"
        status_lbl = Gtk.Label(label=status_text)
        status_lbl.get_style_context().add_class("subtitle-label")
        row.pack_start(status_lbl, False, False, 2)

        action_text = "[ Disconnect ]" if dev["connected"] else "[ Connect ]"
        act_btn = Gtk.Button(label=action_text)
        act_btn.get_style_context().add_class("tool-button")
        act_btn.connect("clicked", self.on_device_action, dev)
        row.pack_end(act_btn, False, False, 0)

        return row

    def on_toggle_power(self, widget, is_powered):
        self.close_popup()
        if is_powered:
            subprocess.run(["bluetoothctl", "power", "off"])
            subprocess.Popen(["notify-send", "Bluetooth", "Bluetooth powered OFF", "-i", "bluetooth-disabled"])
        else:
            subprocess.run(["rfkill", "unblock", "bluetooth"])
            subprocess.run(["bluetoothctl", "power", "on"])
            subprocess.Popen(["notify-send", "Bluetooth", "Bluetooth powered ON", "-i", "bluetooth-active"])

    def on_scan(self, widget):
        self.close_popup()
        subprocess.Popen(["notify-send", "Bluetooth", "Scanning for nearby devices (10s)...", "-i", "bluetooth"])
        subprocess.Popen(["bluetoothctl", "--timeout", "10", "scan", "on"])

    def on_open_gui(self, widget):
        self.close_popup()
        subprocess.Popen(["blueman-manager"])

    def on_device_action(self, widget, dev):
        self.close_popup()
        mac = dev["mac"]
        name = dev["name"]
        if dev["connected"]:
            subprocess.run(["bluetoothctl", "disconnect", mac])
            subprocess.Popen(["notify-send", "Bluetooth", f"Disconnected from {name}", "-i", "bluetooth-disabled"])
        else:
            subprocess.Popen(["notify-send", "Bluetooth", f"Connecting to {name}...", "-i", "bluetooth"])
            res = subprocess.run(["bluetoothctl", "connect", mac])
            if res.returncode == 0:
                subprocess.Popen(["notify-send", "Bluetooth", f"Connected to {name}", "-i", "bluetooth-active"])
            else:
                subprocess.Popen(["notify-send", "Bluetooth", f"Failed to connect to {name}", "-i", "dialog-error"])

if __name__ == "__main__":
    menu = BluetoothMenu()
    menu.show_all()
    Gtk.main()
