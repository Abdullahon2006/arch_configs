#!/usr/bin/env bash
# =============================================================================
# Battery & Power Profile Quick Menu (~/.config/rofi/rofi-battery-menu.sh)
# Structured layout and click-outside dismissal
# =============================================================================

# If already open, toggle it closed
if pgrep -x rofi >/dev/null; then
    pkill -x rofi
    exit 0
fi

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
        fullscreen: true;
        background-color: transparent;
    }
    mainbox {
        orientation: horizontal;
        children: [ dummy-left, right-col ];
        background-color: transparent;
    }
    dummy-left {
        expand: true;
        background-color: transparent;
    }
    right-col {
        orientation: vertical;
        width: 320px;
        expand: false;
        children: [ menubox, dummy-bottom ];
        background-color: transparent;
    }
    dummy-bottom {
        expand: true;
        background-color: transparent;
    }
    menubox {
        orientation: vertical;
        height: 240px;
        margin: 46px 12px 0px 0px;
        background-color: #141a1af2;
        border: 1px;
        border-color: #ffffff24;
        border-radius: 18px;
        padding: 14px;
        children: [ listview ];
    }
    listview {
        lines: 5;
        fixed-height: true;
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
