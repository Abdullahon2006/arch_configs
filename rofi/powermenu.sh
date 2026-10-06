#!/usr/bin/env bash

opt_power="  Power Off"
opt_reboot="  Restart"
opt_suspend="  Suspend"
opt_hibernate="󰒲  Hibernate"
opt_lock="  Lock Screen"
opt_logout="  Log Out"

options="$opt_power\n$opt_reboot\n$opt_suspend\n$opt_hibernate\n$opt_lock\n$opt_logout"

chosen=$(echo -e "$options" | rofi -dmenu -i -p "Power Menu" \
    -theme-str '
    window {
        width: 320px;
        border-radius: 18px;
        background-color: #141818fa;
        border: 2px;
        border-color: #343f44;
        padding: 18px;
        location: center;
        anchor: center;
    }
    inputbar { enabled: false; }
    listview {
        lines: 6;
        margin: 0px;
        spacing: 6px;
        scrollbar: false;
    }
    element {
        padding: 12px 16px;
        border-radius: 12px;
        text-color: #d3c6aa;
        background-color: transparent;
    }
    element selected {
        background-color: #7fbbb3;
        text-color: #1e2524;
        font-weight: bold;
    }
')

case "$chosen" in
    *"Power Off") systemctl poweroff ;;
    *"Restart") systemctl reboot ;;
    *"Suspend") systemctl suspend ;;
    *"Hibernate") systemctl hibernate ;;
    *"Lock Screen") hyprlock ;;
    *"Log Out") hyprctl dispatch exit ;;
esac
