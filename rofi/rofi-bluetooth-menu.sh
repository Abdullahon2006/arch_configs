#!/usr/bin/env bash
# =============================================================================
# Bluetooth Quick Menu (~/.config/rofi/rofi-bluetooth-menu.sh)
# Structured layout, on/off toggle card, and click-outside dismissal
# =============================================================================

# If already open, toggle it closed
if pgrep -x rofi >/dev/null; then
    pkill -x rofi
    exit 0
fi

power_state=$(bluetoothctl show 2>/dev/null | grep -i "Powered:" | awk '{print $2}')

if [ "$power_state" = "yes" ]; then
    toggle="󰂲  Bluetooth : Enabled              [ Turn OFF ]"
    scan="󰑐  Scan for Nearby Devices          [ Scan 10s ]"
    settings="⚙  Bluetooth Manager (Blueman)      [ Open GUI ]"
    divider="── Paired Devices ──────────────────────────────"

    device_lines=""
    paired_list=$(bluetoothctl devices Paired 2>/dev/null)
    if [ -n "$paired_list" ]; then
        while IFS= read -r dev; do
            [ -z "$dev" ] && continue
            mac=$(echo "$dev" | awk '{print $2}')
            name=$(echo "$dev" | cut -d ' ' -f 3-)
            [ -z "$name" ] && name="$mac"

            if bluetoothctl info "$mac" 2>/dev/null | grep -q "Connected: yes"; then
                printf -v line "󰂱  %-20.20s  (Connected)  [ Disconnect ]" "$name"
            else
                printf -v line "󰂯  %-20.20s  (Paired)     [ Connect ]" "$name"
            fi
            device_lines="${device_lines}\n${line}"
        done <<< "$paired_list"
    fi

    if [ -n "$device_lines" ]; then
        menu_content="${toggle}\n${scan}\n${settings}\n${divider}${device_lines}"
    else
        menu_content="${toggle}\n${scan}\n${settings}"
    fi
else
    toggle="󰂯  Bluetooth : Disabled             [ Turn ON ]"
    settings="⚙  Bluetooth Manager (Blueman)      [ Open GUI ]"
    menu_content="${toggle}\n${settings}"
fi

line_count=$(echo -e "$menu_content" | wc -l)
[ "$line_count" -gt 10 ] && line_count=10
[ "$line_count" -lt 2 ] && line_count=2

chosen=$(echo -e "$menu_content" | rofi -dmenu -i -p "Bluetooth" \
    -click-to-exit \
    -theme-str "
    * {
        font: \"JetBrainsMono Nerd Font 10.5\";
        background-color: transparent;
        text-color: #d3c6aa;
    }
    window {
        location: northeast;
        anchor: northeast;
        x-offset: -12px;
        y-offset: 46px;
        width: 460px;
        background-color: #141a1af2;
        border: 1px;
        border-color: #ffffff24;
        border-radius: 18px;
        padding: 14px;
    }
    mainbox {
        orientation: vertical;
        children: [ inputbar, listview ];
    }
    inputbar {
        padding: 8px 12px;
        margin: 0px 0px 10px 0px;
        background-color: #ffffff0f;
        border: 1px;
        border-color: #ffffff14;
        border-radius: 12px;
        spacing: 8px;
        children: [ prompt, entry ];
    }
    prompt {
        text-color: #7fbbb3;
    }
    entry {
        placeholder: \"Search devices...\";
        placeholder-color: #859289;
        text-color: #d3c6aa;
    }
    listview {
        lines: $line_count;
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
")

[ -z "$chosen" ] && exit 0

case "$chosen" in
    *"Turn ON"*)
        rfkill unblock bluetooth 2>/dev/null
        bluetoothctl power on
        notify-send "Bluetooth" "Bluetooth powered ON" -i bluetooth-active
        sleep 0.5
        exec "$0"
        ;;
    *"Turn OFF"*)
        bluetoothctl power off
        notify-send "Bluetooth" "Bluetooth powered OFF" -i bluetooth-disabled
        ;;
    *"Scan for Nearby"*)
        notify-send "Bluetooth" "Scanning for nearby devices (10s)..." -i bluetooth
        bluetoothctl --timeout 10 scan on &
        ;;
    *"Bluetooth Manager"*)
        blueman-manager &
        ;;
    *"──"*)
        exit 0
        ;;
    *"[ Disconnect ]"*)
        dev_name="${chosen:3:20}"
        dev_name="${dev_name%"${dev_name##*[! ]}"}"
        mac=$(bluetoothctl devices Paired 2>/dev/null | grep -F "$dev_name" | head -n 1 | awk '{print $2}')
        if [ -n "$mac" ]; then
            bluetoothctl disconnect "$mac"
            notify-send "Bluetooth" "Disconnected from $dev_name" -i bluetooth-disabled
        fi
        ;;
    *"[ Connect ]"*)
        dev_name="${chosen:3:20}"
        dev_name="${dev_name%"${dev_name##*[! ]}"}"
        mac=$(bluetoothctl devices Paired 2>/dev/null | grep -F "$dev_name" | head -n 1 | awk '{print $2}')
        if [ -n "$mac" ]; then
            notify-send "Bluetooth" "Connecting to $dev_name..." -i bluetooth
            if bluetoothctl connect "$mac"; then
                notify-send "Bluetooth" "Connected to $dev_name" -i bluetooth-active
            else
                notify-send "Bluetooth" "Failed to connect to $dev_name" -i dialog-error
            fi
        fi
        ;;
esac
