#!/usr/bin/env bash
# Application Right-Click Context Menu for Waybar Taskbar

ACTIVE_WINDOW_JSON=$(hyprctl activewindow -j 2>/dev/null)
CLASS=$(echo "$ACTIVE_WINDOW_JSON" | jq -r '.class // empty')
TITLE=$(echo "$ACTIVE_WINDOW_JSON" | jq -r '.title // "Application"')
ADDRESS=$(echo "$ACTIVE_WINDOW_JSON" | jq -r '.address // empty')

options="➕  New Window\n⤢  Toggle Fullscreen (Space)\n➖  Minimize to Scratchpad\n❌  Close Window"

chosen=$(echo -e "$options" | rofi -dmenu -i -p "$CLASS" \
    -click-to-exit \
    -theme-str '
    * { font: "JetBrainsMono Nerd Font 10.5"; text-color: #d3c6aa; background-color: transparent; }
    window {
        location: north; anchor: north; y-offset: 42px; width: 280px;
        background-color: #141a1af5; border: 1px; border-color: #ffffff20;
        border-radius: 14px; padding: 10px;
    }
    mainbox { children: [ listview ]; }
    listview { lines: 4; spacing: 3px; scrollbar: false; }
    element { padding: 8px 12px; border-radius: 8px; }
    element selected.normal { background-color: #7fbbb3; text-color: #1e2524; }
    element-text { background-color: transparent; text-color: inherit; }
')

case "$chosen" in
    *"New Window")
        if [ -n "$CLASS" ]; then
            gtk-launch "$CLASS" 2>/dev/null || setsid "$CLASS" &
        fi
        ;;
    *"Toggle Fullscreen"*)
        python3 ~/.config/hypr/scripts/toggle_fullscreen_space.py
        ;;
    *"Minimize"*)
        hyprctl dispatch movetoworkspace special:minimized
        ;;
    *"Close Window"*)
        hyprctl dispatch killactive
        ;;
esac
