#!/usr/bin/env bash
# =============================================================================
# Battery & Power Profile Quick Menu (~/.config/rofi/rofi-battery-menu.sh)
# GTK Layer Shell Menu with outside-click dismissal
# =============================================================================

exec python3 ~/.config/waybar/menus/battery.py "$@"


current_profile=$(powerprofilesctl get 2>/dev/null || echo "balanced")
cap=$(cat /sys/class/power_supply/BAT*/capacity 2>/dev/null | head -1 || echo "100")
status=$(cat /sys/class/power_supply/BAT*/status 2>/dev/null | head -1 || echo "Unknown")

prof_perf="󰓅  Performance"
prof_bal="󰾆  Balanced"
prof_sav="󰾆  Power Saver"

[ "$current_profile" = "performance" ] && prof_perf="󰓅  Performance  (Active) ✓"
[ "$current_profile" = "balanced" ]    && prof_bal="󰾆  Balanced     (Active) ✓"
[ "$current_profile" = "power-saver" ] && prof_sav="󰾆  Power Saver  (Active) ✓"

header="󰂄  Battery: ${cap}% [${status}]"
divider="─────────────────────────────"

options="$header\n$divider\n$prof_perf\n$prof_bal\n$prof_sav"

chosen=$(echo -e "$options" | rofi -dmenu -i -p "Power Profile" \
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
        width: 320px;
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
        lines: 5;
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

[ -z "$chosen" ] && exit 0

case "$chosen" in
    *"Performance"*)
        powerprofilesctl set performance
        notify-send "Power Profile" "Switched to Performance" -i preferences-system-power
        ;;
    *"Balanced"*)
        powerprofilesctl set balanced
        notify-send "Power Profile" "Switched to Balanced" -i preferences-system-power
        ;;
    *"Power Saver"*)
        powerprofilesctl set power-saver
        notify-send "Power Profile" "Switched to Power Saver" -i preferences-system-power
        ;;
esac
