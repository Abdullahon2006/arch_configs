#!/usr/bin/env python3
"""
Waybar workspace button (~/.config/waybar/scripts/ws.py)

Usage:
  ws.py show N      -> JSON for workspace button N (active / occupied / empty)
  ws.py listen      -> long-running: on Hyprland workspace/window events,
                       signal waybar (SIGRTMIN+8) so every button refreshes.

Replaces waybar's built-in hyprland/workspaces module, whose click handler
still uses the pre-0.56 dispatch syntax that Lua-config Hyprland rejects.
"""
import json, os, signal, socket, subprocess, sys, time

SIGNAL = 8


def hypr(*args):
    try:
        return json.loads(subprocess.check_output(["hyprctl", "-j", *args], stderr=subprocess.DEVNULL))
    except Exception:
        return None


def show(n: str):
    active = (hypr("activeworkspace") or {}).get("id")
    occupied = {str(w["id"]) for w in (hypr("workspaces") or []) if w.get("windows", 0) > 0}
    if str(active) == n:
        cls = "active"
    elif n in occupied:
        cls = "occupied"
    else:
        cls = "empty"
    print(json.dumps({"text": n, "class": cls, "tooltip": f"Workspace {n}"}), flush=True)


def socket_path():
    sig = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
    run = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
    if not sig:  # fall back to newest instance
        base = os.path.join(run, "hypr")
        sig = max(os.listdir(base), key=lambda d: os.path.getmtime(os.path.join(base, d)))
    return os.path.join(run, "hypr", sig, ".socket2.sock")


TRIGGERS = ("workspace", "focusedmon", "createworkspace", "destroyworkspace",
            "openwindow", "closewindow", "movewindow", "activespecial")


def refresh():
    subprocess.run(["pkill", f"-RTMIN+{SIGNAL}", "-x", "waybar"], stderr=subprocess.DEVNULL)


def listen():
    while True:
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.connect(socket_path())
            refresh()
            buf = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                buf += chunk
                *lines, buf = buf.split(b"\n")
                if any(l.split(b">>", 1)[0].decode(errors="ignore").startswith(TRIGGERS) for l in lines):
                    refresh()
        except Exception:
            time.sleep(1)


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "show":
        show(sys.argv[2])
    elif len(sys.argv) >= 2 and sys.argv[1] == "listen":
        listen()
    else:
        print(__doc__)
