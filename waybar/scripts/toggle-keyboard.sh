#!/usr/bin/env bash
# =============================================================================
# Toggle Onboard Virtual Keyboard via DBus (~/.config/waybar/scripts/toggle-keyboard.sh)
# =============================================================================

if pgrep -x onboard >/dev/null; then
    pkill -x onboard
else
    onboard -l "Full Keyboard" &
fi
