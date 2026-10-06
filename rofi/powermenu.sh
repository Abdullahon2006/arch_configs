#!/usr/bin/env bash
# Power / session menu (~/.config/rofi/powermenu.sh)
# Uses the shared glass theme (~/.config/rofi/theme.rasi) so blur shows through.

opt_power="  Power Off"
opt_reboot="  Restart"
opt_suspend="  Suspend"
opt_hibernate="󰒲  Hibernate"
opt_lock="  Lock Screen"
opt_logout="  Log Out"

options="$opt_power\n$opt_reboot\n$opt_suspend\n$opt_hibernate\n$opt_lock\n$opt_logout"

chosen=$(echo -e "$options" | rofi -dmenu -i -p "Power" \
    -theme ~/.config/rofi/theme.rasi \
    -theme-str '
    window   { width: 320px; }
    mainbox  { children: [ listview ]; }
    listview { lines: 6; }
    element  { padding: 12px 16px; }
')

case "$chosen" in
    *"Power Off") systemctl poweroff ;;
    *"Restart") systemctl reboot ;;
    *"Suspend") systemctl suspend ;;
    *"Hibernate") systemctl hibernate ;;
    *"Lock Screen") hyprlock ;;
    # Hyprland 0.56 Lua dispatch syntax
    *"Log Out") hyprctl dispatch 'hl.dsp.exit()' ;;
esac
