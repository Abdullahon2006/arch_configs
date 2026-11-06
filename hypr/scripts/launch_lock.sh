#!/usr/bin/env bash
# Clear faillock
faillock --reset 2>/dev/null || true

# If hyprlock is already running, do not spawn another
if pidof hyprlock >/dev/null 2>&1; then
    exit 0
fi

# Ensure RustDesk or other background input hooks do not intercept keystrokes
exec hyprlock
