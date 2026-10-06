#!/usr/bin/env bash

options="🖥️  Display & Scaling (Monitors)\n🎨  Appearance & GTK Theme (nwg-look)\n🔊  Sound & Audio (pavucontrol)\n  Network & Wi-Fi Settings\n  Bluetooth Manager (blueman)\n⌨️  Keyboard Shortcuts Cheatsheet\n🖼️  Select Wallpaper\n⚡  Power & Battery Management"

chosen=$(echo -e "$options" | rofi -dmenu -i -p "Settings" \
    -theme-str '
    window {
        width: 360px;
        border-radius: 18px;
        background-color: #141818fa;
        border: 2px;
        border-color: #343f44;
        padding: 18px;
    }
    inputbar { enabled: false; }
    listview { lines: 8; spacing: 4px; scrollbar: false; }
    element { padding: 10px 14px; border-radius: 10px; text-color: #d3c6aa; }
    element selected { background-color: #7fbbb3; text-color: #1e2524; font-weight: bold; }
')

case "$chosen" in
    *"Display"*)
        if command -v nwg-displays >/dev/null 2>&1; then nwg-displays &
        elif command -v wdisplays >/dev/null 2>&1; then wdisplays &
        else notify-send "Settings" "Install nwg-displays or wdisplays for monitor GUI"; fi ;;
    *"Appearance"*)
        if command -v nwg-look >/dev/null 2>&1; then nwg-look &
        elif command -v lxappearance >/dev/null 2>&1; then lxappearance &
        else notify-send "Settings" "Install nwg-look to customize GTK themes and fonts"; fi ;;
    *"Sound"*) pavucontrol & ;;
    *"Network"*) nm-connection-editor & ;;
    *"Bluetooth"*) blueman-manager & ;;
    *"Keyboard"*)
        kitty --title "Hyprland Keybinds" -e sh -c 'echo "=== HYPRLAND SHORTCUTS ===
Super + Enter        : Terminal (Kitty)
Super + D / Space    : App Drawer / Launcher
Super + E            : File Manager
Super + Q / Alt + F4 : Close Window
Super + F / F11      : Toggle Fullscreen
Super + V            : Toggle Float Mode
Super + M / H        : Minimize / Hide Window
Super + Shift + M    : Restore Minimized Windows
Super + L            : Lock Screen
Super + I            : Desktop Settings Menu
Ctrl + Shift + Esc   : Task Manager (htop)
Print / Super+Shift+S: Screenshot Area
Super + 1..9         : Switch Workspace
Super + Shift + 1..9 : Move Window to Workspace
Super + Left/Right   : Move Focus"; read -p "Press Enter to close"' & ;;
    *"Wallpaper"*)
        wallpaper=$(find ~/Pictures -type f \( -name "*.jpg" -o -name "*.png" \) 2>/dev/null | rofi -dmenu -i -p "Select Wallpaper")
        if [ -n "$wallpaper" ]; then
            killall swaybg 2>/dev/null
            swaybg -i "$wallpaper" -m fill &
            notify-send "Wallpaper" "Applied: $(basename "$wallpaper")"
        fi ;;
esac
