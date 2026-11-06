#!/usr/bin/env python3
import json
import os
import subprocess
import sys

STATE_FILE = "/tmp/hypr_spaces.json"
SETTINGS_FILE = os.path.expanduser("~/.config/hypr/settings.json")

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
    return run_cmd(f"hyprctl dispatch '{lua_str}'")

def load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path, data):
    try:
        with open(path, "w") as f:
            json.dump(data, f)
    except Exception:
        pass

def main():
    target_addr = sys.argv[1] if len(sys.argv) > 1 else None
    if target_addr and target_addr.startswith("address:"):
        target_addr = target_addr.split(":", 1)[1]

    clients_raw = run_cmd("hyprctl clients -j")
    clients = []
    if clients_raw:
        try:
            clients = json.loads(clients_raw)
        except Exception:
            clients = []

    target_win = None
    if target_addr:
        for c in clients:
            if c.get("address", "").lower() == target_addr.lower():
                target_win = c
                break

    if not target_win:
        active_raw = run_cmd("hyprctl activewindow -j")
        if active_raw:
            try:
                active_win = json.loads(active_raw)
                if active_win.get("address"):
                    target_win = active_win
            except Exception:
                pass

    if not target_win and clients:
        sorted_clients = sorted(clients, key=lambda x: x.get("focusHistoryID", 999))
        target_win = sorted_clients[0]

    if not target_win:
        return

    address = target_win.get("address", "")
    win_class = target_win.get("class", "app").strip() or "app"
    curr_ws = target_win.get("workspace", {})
    curr_ws_id = curr_ws.get("id", 1)
    curr_ws_name = str(curr_ws.get("name", curr_ws_id))

    spaces = load_json(STATE_FILE, {})
    settings = load_json(SETTINGS_FILE, {"fullscreen_bar": "visible"})
    fs_mode = "maximized" if settings.get("fullscreen_bar", "visible") == "visible" else "fullscreen"

    # Check if already in a dedicated space
    if curr_ws_name.startswith("space:") or address in spaces:
        space_info = spaces.get(address, {})
        orig_ws = space_info.get("orig_ws", 1)

        # Unfullscreen
        dispatch_lua(f'hl.dsp.focus({{ window = "address:{address}" }})')
        dispatch_lua('hl.dsp.window.fullscreen({{ action = "unset" }})')
        # Move back to original workspace
        dispatch_lua(f'hl.dsp.window.move({{ workspace = "{orig_ws}", address = "{address}" }})')
        # Switch to original workspace & focus window
        dispatch_lua(f'hl.dsp.focus({{ workspace = "{orig_ws}" }})')
        dispatch_lua(f'hl.dsp.focus({{ window = "address:{address}" }})')

        if address in spaces:
            del spaces[address]
            save_json(STATE_FILE, spaces)
    else:
        # Enter new dedicated Space
        suffix = address[-4:] if len(address) >= 4 else "00"
        space_name = f"space:{win_class}-{suffix}"

        spaces[address] = {
            "orig_ws": curr_ws_id,
            "space_name": space_name
        }
        save_json(STATE_FILE, spaces)

        # Move to space and switch to it
        dispatch_lua(f'hl.dsp.window.move({{ workspace = "name:{space_name}", address = "{address}" }})')
        dispatch_lua(f'hl.dsp.focus({{ workspace = "name:{space_name}" }})')
        dispatch_lua(f'hl.dsp.focus({{ window = "address:{address}" }})')
        dispatch_lua(f'hl.dsp.window.fullscreen({{ mode = "{fs_mode}", action = "set" }})')

if __name__ == "__main__":
    main()
