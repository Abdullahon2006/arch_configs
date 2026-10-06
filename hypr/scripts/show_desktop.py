#!/usr/bin/env python3
import json, subprocess, os

try:
    ws_out = subprocess.check_output(["hyprctl", "activeworkspace", "-j"], stderr=subprocess.DEVNULL)
    ws = json.loads(ws_out).get("name", "1")
except Exception:
    ws = "1"

state_file = f"/tmp/hypr-desktop-state-{ws}"

if os.path.exists(state_file) and os.path.getsize(state_file) > 0:
    with open(state_file, "r") as f:
        addrs = [line.strip() for line in f if line.strip()]
    for addr in addrs:
        subprocess.run(["hyprctl", "dispatch", "movetoworkspacesilent", f"name:{ws},address:{addr}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        os.remove(state_file)
    except OSError:
        pass
else:
    try:
        clients_out = subprocess.check_output(["hyprctl", "clients", "-j"], stderr=subprocess.DEVNULL)
        clients = json.loads(clients_out)
        addrs = [c["address"] for c in clients if str(c.get("workspace", {}).get("name")) == str(ws)]
    except Exception:
        addrs = []

    if addrs:
        with open(state_file, "w") as f:
            f.write("\n".join(addrs) + "\n")
        for addr in addrs:
            subprocess.run(["hyprctl", "dispatch", "movetoworkspacesilent", f"special:desktop,address:{addr}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
