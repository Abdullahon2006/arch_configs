#!/usr/bin/env bash
# =============================================================================
# Battery & Power Profile Quick Menu (~/.config/rofi/rofi-battery-menu.sh)
# =============================================================================

current_profile=$(powerprofilesctl get 2>/dev/null || echo "balanced")
cap=$(cat /sys/class/power_supply/BAT*/capacity 2>/dev/null | head -1 || echo "100")
status=$(cat /sys/class/power_supply/BAT*/status 2>/dev/null | head -1 || echo "Unknown")

prof_perf="󰓅  Performance"
prof_bal="󰾆  Balanced"
prof_sav="󰾆  Power Saver"

[ "$current_profile" = "performance" ] && prof_perf="󰓅  Performance (Active) ✓"
[ "$current_profile" = "balanced" ]    && prof_bal="󰾆  Balanced (Active) ✓"
[ "$current_profile" = "power-saver" ] && prof_sav="󰾆  Power Saver (Active) ✓"

header="󰂄  Battery: ${cap}% [${status}]"

options="$header\n---\n$prof_perf\n$prof_bal\n$prof_sav"

chosen=$(echo -e "$options" | rofi -dmenu -i -p "Power Profile" \
    -theme ~/.config/rofi/theme.rasi \
    -theme-str '
    window {
        width: 290px;
        location: northeast;
        anchor: northeast;
        x-offset: -54px;
        y-offset: 44px;
        border-radius: 16px;
    }
    mainbox  { children: [ listview ]; }
    listview { lines: 5; spacing: 4px; }
    element  { padding: 10px 14px; border-radius: 10px; }
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
