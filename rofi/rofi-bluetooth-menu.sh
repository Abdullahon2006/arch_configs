#!/usr/bin/env bash
# =============================================================================
# Bluetooth quick menu for Waybar (~/.config/rofi/rofi-bluetooth-menu.sh)
# =============================================================================

# Check if bluetooth is powered on
power_state=$(bluetoothctl show 2>/dev/null | grep -i "Powered:" | awk '{print $2}')

if [ "$power_state" = "yes" ]; then
    toggle="󰂲  Turn Bluetooth Off"
else
    toggle="󰂯  Turn Bluetooth On"
fi

menu="$toggle\n⚙  Bluetooth Settings (Blueman)"

if [ "$power_state" = "yes" ]; then
    # Get paired devices
    devices=$(bluetoothctl devices Paired 2>/dev/null | cut -d ' ' -f 2-)
    if [ -n "$devices" ]; then
        menu="$menu\n--- Paired Devices ---"
        while IFS= read -r dev; do
            mac=$(echo "$dev" | awk '{print $1}')
            name=$(echo "$dev" | cut -d ' ' -f 2-)
            # Check if connected
            info=$(bluetoothctl info "$mac" 2>/dev/null)
            if echo "$info" | grep -q "Connected: yes"; then
                menu="$menu\n󰂱  Disconnect $name [$mac]"
            else
                menu="$menu\n󰂯  Connect $name [$mac]"
            fi
        done <<< "$devices"
    fi
    menu="$menu\n󰑐  Scan for Nearby Devices"
fi

chosen=$(echo -e "$menu" | rofi -dmenu -i -p "Bluetooth" \
    -theme ~/.config/rofi/theme.rasi \
    -theme-str '
    window {
        width: 320px;
        location: northeast;
        anchor: northeast;
        x-offset: -110px;
        y-offset: 44px;
        border-radius: 16px;
    }
    mainbox  { children: [ inputbar, listview ]; }
    listview { lines: 7; spacing: 4px; }
    element  { padding: 10px 14px; border-radius: 10px; }
')

[ -z "$chosen" ] && exit 0

case "$chosen" in
    *"Turn Bluetooth On")
        rfkill unblock bluetooth 2>/dev/null
        bluetoothctl power on
        notify-send "Bluetooth" "Powered ON" -i bluetooth-active
        ;;
    *"Turn Bluetooth Off")
        bluetoothctl power off
        notify-send "Bluetooth" "Powered OFF" -i bluetooth-disabled
        ;;
    *"Bluetooth Settings"*)
        blueman-manager &
        ;;
    *"Scan for Nearby Devices"*)
        notify-send "Bluetooth" "Scanning for devices (10s)..." -i bluetooth
        bluetoothctl --timeout 10 scan on &
        ;;
    *"Connect "*)
        mac=$(echo "$chosen" | grep -o -E '\[[0-9A-Fa-f:]+\]' | tr -d '[]')
        name=$(echo "$chosen" | sed -E 's/.*Connect (.*) \[.*/\1/')
        notify-send "Bluetooth" "Connecting to $name..." -i bluetooth
        if bluetoothctl connect "$mac"; then
            notify-send "Bluetooth" "Connected to $name" -i bluetooth-active
        else
            notify-send "Bluetooth" "Failed to connect to $name" -i dialog-error
        fi
        ;;
    *"Disconnect "*)
        mac=$(echo "$chosen" | grep -o -E '\[[0-9A-Fa-f:]+\]' | tr -d '[]')
        name=$(echo "$chosen" | sed -E 's/.*Disconnect (.*) \[.*/\1/')
        bluetoothctl disconnect "$mac"
        notify-send "Bluetooth" "Disconnected from $name" -i bluetooth-disabled
        ;;
esac
