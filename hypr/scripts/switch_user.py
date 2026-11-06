#!/usr/bin/env python3
import json
import os
import subprocess
import sys

def get_sessions():
    try:
        out = subprocess.check_output(["loginctl", "list-sessions", "--no-legend"], text=True)
        sessions = []
        for line in out.strip().splitlines():
            parts = line.split()
            if len(parts) >= 3:
                s_id, uid, user = parts[0], parts[1], parts[2]
                sessions.append({"session": s_id, "uid": uid, "user": user})
        return sessions
    except Exception:
        return []

def switch_to_user(target_user):
    sessions = get_sessions()
    for s in sessions:
        if s["user"] == target_user:
            s_id = s["session"]
            res = subprocess.run(["loginctl", "activate", s_id])
            if res.returncode == 0:
                return True
    
    subprocess.run([
        "busctl", "call", "org.freedesktop.DisplayManager",
        "/org/freedesktop/DisplayManager/Seat0",
        "org.freedesktop.DisplayManager.Seat", "SwitchToGreeter"
    ])
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        current_user = os.environ.get("USER") or "david"
        target = "simple" if current_user == "david" else "david"
    switch_to_user(target)
