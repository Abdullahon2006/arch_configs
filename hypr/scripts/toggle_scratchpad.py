#!/usr/bin/env python3
import json
import os
import subprocess
import sys

STATE_FILE = "/tmp/hypr_scratchpad.json"

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

def dispatch_lua(lua_expr):
    return run_cmd(f"hyprctl dispatch '{lua_expr}'")

def hypr_query(endpoint):
    raw = run_cmd(f"hyprctl {endpoint} -j")
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            return None
    return None

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

def get_target_regular_ws():
    act_ws = hypr_query("activeworkspace")
    if act_ws:
        ws_name = str(act_ws.get("name", "1"))
        ws_id = act_ws.get("id", 1)
        if not ws_name.startswith("special:") and ws_id > 0:
            return str(ws_id)
    # Fallback to workspace 1
    return "1"

def restore_window(address):
    clients = hypr_query("clients") or []
    target_win = None
    for c in clients:
        if c.get("address", "").lower() == address.lower():
            target_win = c
            break

    state = load_json(STATE_FILE, {})
    saved_orig = state.get(address, {}).get("orig_ws")
    target_ws = str(saved_orig) if saved_orig else get_target_regular_ws()

    # Move window back to regular workspace
    dispatch_lua(f'hl.dsp.focus({{ window = "address:{address}" }})')
    dispatch_lua(f'hl.dsp.window.move({{ workspace = "{target_ws}" }})')
    dispatch_lua(f'hl.dsp.focus({{ workspace = "{target_ws}" }})')
    dispatch_lua(f'hl.dsp.focus({{ window = "address:{address}" }})')

    if address in state:
        del state[address]
        save_json(STATE_FILE, state)

def minimize_window(address, orig_ws=None):
    if not orig_ws:
        orig_ws = get_target_regular_ws()

    state = load_json(STATE_FILE, {})
    state[address] = {
        "orig_ws": orig_ws
    }
    save_json(STATE_FILE, state)

    dispatch_lua(f'hl.dsp.focus({{ window = "address:{address}" }})')
    dispatch_lua('hl.dsp.window.move({ workspace = "special:minimized" })')

def toggle_active():
    act_win = hypr_query("activewindow")
    if not act_win or not act_win.get("address"):
        # If no active window, check if special workspace is open to toggle it
        dispatch_lua('hl.dsp.workspace.toggle_special("minimized")')
        return

    address = act_win.get("address", "")
    ws_name = str(act_win.get("workspace", {}).get("name", ""))

    if ws_name == "special:minimized" or ws_name.startswith("special:"):
        restore_window(address)
    else:
        orig_ws = str(act_win.get("workspace", {}).get("id", "1"))
        minimize_window(address, orig_ws)

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "toggle"

    if action == "toggle":
        toggle_active()
    elif action == "restore":
        addr = sys.argv[2] if len(sys.argv) > 2 else ""
        if addr:
            restore_window(addr)
        else:
            toggle_active()
    elif action == "minimize":
        addr = sys.argv[2] if len(sys.argv) > 2 else ""
        if addr:
            minimize_window(addr)
        else:
            toggle_active()
    elif action == "overlay":
        dispatch_lua('hl.dsp.workspace.toggle_special("minimized")')

if __name__ == "__main__":
    main()
