#!/usr/bin/env python3
import subprocess
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, GLib
from popup import BasePopup

class WifiMenu(BasePopup):
    def __init__(self):
        super().__init__(name="wifi", width=460, margin_right=12, margin_top=46)

        is_enabled = self.get_wifi_status()
        self.networks = []
        self.network_rows = []

        # Header Title
        title = Gtk.Label(label="󰤨  Wi-Fi Networks")
        title.set_xalign(0.0)
        title.get_style_context().add_class("title-label")
        self.card.pack_start(title, False, False, 2)

        # Toggle Card
        toggle_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        toggle_box.get_style_context().add_class("tool-button")
        
        status_text = "󰤮  Wi-Fi : Enabled" if is_enabled else "󰤨  Wi-Fi : Disabled"
        status_lbl = Gtk.Label(label=status_text)
        status_lbl.set_xalign(0.0)
        toggle_box.pack_start(status_lbl, True, True, 6)

        btn_action = "Turn OFF" if is_enabled else "Turn ON"
        toggle_btn = Gtk.Button(label=f"[ {btn_action} ]")
        toggle_btn.get_style_context().add_class("tool-button")
        toggle_btn.connect("clicked", self.on_toggle_wifi, is_enabled)
        toggle_box.pack_end(toggle_btn, False, False, 4)
        self.card.pack_start(toggle_box, False, False, 3)

        if is_enabled:
            # Action tools row
            tools_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            
            rescan_btn = Gtk.Button(label="󰑐  Rescan")
            rescan_btn.get_style_context().add_class("tool-button")
            rescan_btn.connect("clicked", self.on_rescan)
            tools_box.pack_start(rescan_btn, True, True, 0)

            settings_btn = Gtk.Button(label="⚙  Connections")
            settings_btn.get_style_context().add_class("tool-button")
            settings_btn.connect("clicked", self.on_open_connections)
            tools_box.pack_start(settings_btn, True, True, 0)

            self.card.pack_start(tools_box, False, False, 3)

            # Divider
            div = Gtk.Box()
            div.get_style_context().add_class("divider")
            self.card.pack_start(div, False, False, 4)

            # Search entry
            self.search_entry = Gtk.Entry()
            self.search_entry.set_placeholder_text("Search networks...")
            self.search_entry.get_style_context().add_class("search-entry")
            self.search_entry.connect("changed", self.on_search_changed)
            self.card.pack_start(self.search_entry, False, False, 2)

            # Password Entry Area (hidden by default, shown when connecting to secured wifi)
            self.pwd_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            self.pwd_box.set_no_show_all(True)
            self.pwd_target_ssid = None

            pwd_lbl = Gtk.Label(label="Enter Wi-Fi Password:")
            pwd_lbl.set_xalign(0.0)
            pwd_lbl.get_style_context().add_class("subtitle-label")
            self.pwd_box.pack_start(pwd_lbl, False, False, 0)

            pwd_input_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            self.pwd_entry = Gtk.Entry()
            self.pwd_entry.set_visibility(False)
            self.pwd_entry.get_style_context().add_class("search-entry")
            self.pwd_entry.connect("activate", self.on_submit_password)
            pwd_input_row.pack_start(self.pwd_entry, True, True, 0)

            pwd_connect_btn = Gtk.Button(label="Connect")
            pwd_connect_btn.get_style_context().add_class("tool-button")
            pwd_connect_btn.connect("clicked", self.on_submit_password)
            pwd_input_row.pack_end(pwd_connect_btn, False, False, 0)

            self.pwd_box.pack_start(pwd_input_row, False, False, 2)
            self.card.pack_start(self.pwd_box, False, False, 2)

            # Available Networks Header
            networks_lbl = Gtk.Label(label="Available Networks")
            networks_lbl.set_xalign(0.0)
            networks_lbl.get_style_context().add_class("subtitle-label")
            self.card.pack_start(networks_lbl, False, False, 2)

            # Scrolled list of networks
            self.networks = self.get_wifi_list()
            scroll = Gtk.ScrolledWindow()
            scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            scroll.set_min_content_height(min(max(len(self.networks) * 38, 120), 280))

            self.list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            self.populate_networks()
            scroll.add(self.list_box)
            self.card.pack_start(scroll, True, True, 2)

    def get_wifi_status(self):
        try:
            out = subprocess.check_output(["nmcli", "-fields", "WIFI", "g"], text=True)
            return "enabled" in out.lower()
        except Exception:
            return False

    def get_wifi_list(self):
        networks = []
        seen = set()
        try:
            out = subprocess.check_output(
                ["nmcli", "-t", "-f", "IN-USE,SSID,SIGNAL,SECURITY", "device", "wifi", "list", "--rescan", "no"],
                text=True
            )
            for line in out.strip().splitlines():
                parts = line.split(":")
                if len(parts) >= 4:
                    in_use = (parts[0].strip() == "*")
                    ssid = parts[1].strip()
                    signal_str = parts[2].strip()
                    sec = parts[3].strip()

                    if not ssid or ssid in seen:
                        continue
                    seen.add(ssid)

                    try:
                        sig_val = int(signal_str)
                    except ValueError:
                        sig_val = 50

                    if sig_val >= 75:
                        sig_icon = "󰤨"
                    elif sig_val >= 50:
                        sig_icon = "󰤥"
                    elif sig_val >= 25:
                        sig_icon = "󰤢"
                    else:
                        sig_icon = "󰤟"

                    is_secured = (sec != "" and sec != "--")
                    networks.append({
                        "ssid": ssid,
                        "in_use": in_use,
                        "signal": sig_val,
                        "sig_icon": sig_icon,
                        "secured": is_secured,
                        "sec_icon": "" if is_secured else ""
                    })
        except Exception:
            pass

        # Sort: connected first, then by signal strength descending
        networks.sort(key=lambda x: (not x["in_use"], -x["signal"]))
        return networks

    def populate_networks(self, filter_text=""):
        for child in self.list_box.get_children():
            self.list_box.remove(child)

        filter_text = filter_text.lower().strip()
        filtered = [n for n in self.networks if filter_text in n["ssid"].lower()]

        for net in filtered:
            btn = Gtk.Button()
            btn.get_style_context().add_class("menu-button")
            if net["in_use"]:
                btn.get_style_context().add_class("active-item")

            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            
            icon_lbl = Gtk.Label(label=net["sig_icon"])
            box.pack_start(icon_lbl, False, False, 0)

            status_tag = " (Connected)" if net["in_use"] else ""
            name_lbl = Gtk.Label(label=f"{net['ssid']}{status_tag}")
            name_lbl.set_xalign(0.0)
            box.pack_start(name_lbl, True, True, 0)

            sec_lbl = Gtk.Label(label=f"{net['sec_icon']}  {net['signal']}%")
            box.pack_end(sec_lbl, False, False, 0)

            btn.add(box)
            btn.connect("clicked", self.on_network_selected, net)
            self.list_box.pack_start(btn, False, False, 1)

        self.list_box.show_all()

    def on_search_changed(self, entry):
        self.populate_networks(entry.get_text())

    def on_toggle_wifi(self, widget, is_enabled):
        self.close_popup()
        if is_enabled:
            subprocess.run(["nmcli", "radio", "wifi", "off"])
            subprocess.Popen(["notify-send", "Wi-Fi", "Wi-Fi disabled", "-i", "network-wireless-offline"])
        else:
            subprocess.run(["nmcli", "radio", "wifi", "on"])
            subprocess.Popen(["notify-send", "Wi-Fi", "Wi-Fi enabled", "-i", "network-wireless-signal-good"])

    def on_rescan(self, widget):
        self.close_popup()
        subprocess.Popen(["notify-send", "Wi-Fi", "Scanning for networks...", "-i", "network-wireless"])
        subprocess.run(["nmcli", "device", "wifi", "rescan"])

    def on_open_connections(self, widget):
        self.close_popup()
        subprocess.Popen(["nm-connection-editor"])

    def on_network_selected(self, widget, net):
        ssid = net["ssid"]
        if net["in_use"]:
            self.close_popup()
            subprocess.Popen(["notify-send", "Wi-Fi", f"Already connected to {ssid}", "-i", "network-wireless-connected"])
            return

        # Check if saved connection exists
        try:
            saved = subprocess.check_output(["nmcli", "-t", "-f", "NAME", "connection", "show"], text=True)
            is_saved = any(line.strip() == ssid for line in saved.splitlines())
        except Exception:
            is_saved = False

        if is_saved:
            self.close_popup()
            subprocess.Popen(["notify-send", "Wi-Fi", f"Connecting to {ssid}...", "-i", "network-wireless-acquiring"])
            res = subprocess.run(["nmcli", "connection", "up", ssid])
            if res.returncode == 0:
                subprocess.Popen(["notify-send", "Wi-Fi", f"Successfully connected to {ssid}", "-i", "network-wireless-connected"])
            else:
                subprocess.Popen(["notify-send", "Wi-Fi", f"Failed to connect to {ssid}", "-i", "dialog-error"])
        elif not net["secured"]:
            self.close_popup()
            subprocess.Popen(["notify-send", "Wi-Fi", f"Connecting to open network {ssid}...", "-i", "network-wireless-acquiring"])
            res = subprocess.run(["nmcli", "device", "wifi", "connect", ssid])
            if res.returncode == 0:
                subprocess.Popen(["notify-send", "Wi-Fi", f"Successfully connected to {ssid}", "-i", "network-wireless-connected"])
            else:
                subprocess.Popen(["notify-send", "Wi-Fi", f"Failed to connect to {ssid}", "-i", "dialog-error"])
        else:
            # Need password: show inline password field in the card
            self.pwd_target_ssid = ssid
            self.pwd_entry.set_text("")
            self.pwd_box.show_all()
            self.pwd_entry.grab_focus()

    def on_submit_password(self, widget):
        if not self.pwd_target_ssid:
            return
        pwd = self.pwd_entry.get_text()
        ssid = self.pwd_target_ssid
        self.close_popup()
        subprocess.Popen(["notify-send", "Wi-Fi", f"Connecting to {ssid}...", "-i", "network-wireless-acquiring"])
        res = subprocess.run(["nmcli", "device", "wifi", "connect", ssid, "password", pwd])
        if res.returncode == 0:
            subprocess.Popen(["notify-send", "Wi-Fi", f"Successfully connected to {ssid}", "-i", "network-wireless-connected"])
        else:
            subprocess.Popen(["notify-send", "Wi-Fi", f"Failed to connect to {ssid}", "-i", "dialog-error"])

if __name__ == "__main__":
    menu = WifiMenu()
    menu.show_all()
    Gtk.main()
