#!/usr/bin/env python3
import json
import os
import subprocess
import sys

STATE_FILE = "/tmp/hypr_spaces.json"
SETTINGS_FILE = os.path.expanduser("~/.config/hypr/settings.json")

def run_cmd(cmd):
    try:
        res = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL)
        return res.decode("utf-8").strip()
    except Exception:
        return ""

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
    active_win_raw = run_cmd("hyprctl activewindow -j")
    if not active_win_raw:
        return

    try:
        active_win = json.loads(active_win_raw)
    except Exception:
        return

    address = active_win.get("address", "")
    if not address:
        return

    win_class = active_win.get("class", "app").strip() or "app"
    curr_ws = active_win.get("workspace", {})
    curr_ws_id = curr_ws.get("id", 1)
    curr_ws_name = str(curr_ws.get("name", curr_ws_id))

    spaces = load_json(STATE_FILE, {})
    settings = load_json(SETTINGS_FILE, {"fullscreen_bar": "visible"})
    fs_mode = 1 if settings.get("fullscreen_bar", "visible") == "visible" else 0

    # Check if already in a dedicated space
    if curr_ws_name.startswith("space:") or address in spaces:
        # Exit space: return window to original workspace
        space_info = spaces.get(address, {})
        orig_ws = space_info.get("orig_ws", 1)

        # Unfullscreen
        run_cmd(f"hyprctl dispatch fullscreen 0")
        # Move back to original workspace
        run_cmd(f"hyprctl dispatch movetoworkspacesilent {orig_ws},address:{address}")
        # Switch to original workspace & focus window
        run_cmd(f"hyprctl dispatch workspace {orig_ws}")
        run_cmd(f"hyprctl dispatch focuswindow address:{address}")

        if address in spaces:
            del spaces[address]
            save_json(STATE_FILE, spaces)
    else:
        # Enter new dedicated Space
        # Short clean ID from address
        suffix = address[-4:] if len(address) >= 4 else "00"
        space_name = f"space:{win_class}-{suffix}"

        spaces[address] = {
            "orig_ws": curr_ws_id,
            "space_name": space_name
        }
        save_json(STATE_FILE, spaces)

        # Move to space and switch to it
        run_cmd(f"hyprctl dispatch movetoworkspace name:{space_name},address:{address}")
        run_cmd(f"hyprctl dispatch workspace name:{space_name}")
        # Set fullscreen (1 preserves top bar, 0 covers bar)
        run_cmd(f"hyprctl dispatch fullscreen {fs_mode}")

if __name__ == "__main__":
    main()
