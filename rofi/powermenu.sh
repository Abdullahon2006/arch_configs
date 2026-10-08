#!/usr/bin/env bash
# =============================================================================
# Power & Session Menu (~/.config/rofi/powermenu.sh)
# GTK Layer Shell Menu with outside-click dismissal
# =============================================================================

exec python3 ~/.config/waybar/menus/power.py "$@"


opt_power="󰐥  Power Off"
opt_reboot="󰜉  Restart"
opt_suspend="󰤄  Suspend"
opt_hibernate="󰒲  Hibernate"
opt_lock="󰌾  Lock Screen"
opt_logout="󰍃  Log Out"

options="$opt_power\n$opt_reboot\n$opt_suspend\n$opt_hibernate\n$opt_lock\n$opt_logout"

chosen=$(echo -e "$options" | rofi -dmenu -i -p "Power" \
    -click-to-exit \
    -theme-str '
    * {
        font: "JetBrainsMono Nerd Font 10.5";
        background-color: transparent;
        text-color: #d3c6aa;
    }
    window {
        location: northeast;
        anchor: northeast;
        x-offset: -12px;
        y-offset: 46px;
        width: 260px;
        background-color: #141a1af2;
        border: 1px;
        border-color: #ffffff24;
        border-radius: 18px;
        padding: 14px;
    }
    mainbox {
        orientation: vertical;
        children: [ listview ];
    }
    listview {
        lines: 6;
        fixed-height: false;
        spacing: 4px;
        scrollbar: false;
    }
    element {
        padding: 8px 12px;
        border-radius: 10px;
        background-color: transparent;
        text-color: #d3c6aa;
    }
    element normal.normal {
        background-color: transparent;
        text-color: #d3c6aa;
    }
    element alternate.normal {
        background-color: transparent;
        text-color: #d3c6aa;
    }
    element selected.normal {
        background-color: #7fbbb3;
        text-color: #1e2524;
    }
    element-text {
        background-color: transparent;
        text-color: inherit;
    }
')

case "$chosen" in
    *"Power Off") systemctl poweroff ;;
    *"Restart") systemctl reboot ;;
    *"Suspend") systemctl suspend ;;
    *"Hibernate") systemctl hibernate ;;
    *"Lock Screen") hyprlock ;;
    *"Log Out") hyprctl dispatch 'hl.dsp.exit()' ;;
esac
