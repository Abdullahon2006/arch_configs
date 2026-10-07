#!/usr/bin/env bash
# =============================================================================
# Wi-Fi Quick Menu (~/.config/rofi/rofi-wifi-menu.sh)
# Structured layout, on/off toggle card, and click-outside dismissal
# =============================================================================

# If already open, toggle it closed
if pgrep -x rofi >/dev/null; then
    pkill -x rofi
    exit 0
fi

wifi_status=$(nmcli -fields WIFI g 2>/dev/null | tail -n 1 | tr -d ' ')

if [ "$wifi_status" = "enabled" ]; then
    toggle="󰤮  Wi-Fi : Enabled                  [ Turn OFF ]"
    rescan="󰑐  Rescan Networks                  [ Refresh ]"
    settings="⚙  Network Connections              [ Open GUI ]"
    divider="── Available Networks ──────────────────────────"

    # Get clean, deduplicated wifi list formatted into structured columns
    wifi_list=$(nmcli -t -f IN-USE,SSID,SIGNAL,SECURITY device wifi list --rescan no 2>/dev/null | awk -F: '
    !seen[$2]++ && $2 != "" {
        in_use = ($1 ~ /\*/) ? "(Connected)" : "           "
        sec = ($4 != "" && $4 != "--") ? "" : ""
        icon = ($1 ~ /\*/) ? "󰤨" : "󰤪"
        printf "%s  %-20.20s  %s %3s%%  %s\n", icon, $2, in_use, $3, sec
    }')

    if [ -n "$wifi_list" ]; then
        menu_content="$toggle\n$rescan\n$settings\n$divider\n$wifi_list"
    else
        menu_content="$toggle\n$rescan\n$settings"
    fi
else
    toggle="󰤨  Wi-Fi : Disabled                 [ Turn ON ]"
    settings="⚙  Network Connections              [ Open GUI ]"
    menu_content="$toggle\n$settings"
fi

line_count=$(echo -e "$menu_content" | wc -l)
[ "$line_count" -gt 10 ] && line_count=10
[ "$line_count" -lt 2 ] && line_count=2

chosen=$(echo -e "$menu_content" | rofi -dmenu -i -p "Wi-Fi" \
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
        placeholder: \"Search networks...\";
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
    *"Turn OFF"*)
        nmcli radio wifi off
        notify-send "Wi-Fi" "Wi-Fi disabled" -i network-wireless-offline
        ;;
    *"Turn ON"*)
        nmcli radio wifi on
        notify-send "Wi-Fi" "Wi-Fi enabled" -i network-wireless-signal-good
        ;;
    *"Rescan"*)
        notify-send "Wi-Fi" "Scanning for networks..." -i network-wireless
        nmcli device wifi rescan 2>/dev/null
        sleep 1
        exec "$0"
        ;;
    *"Network Connections"*)
        nm-connection-editor &
        ;;
    *"──"*)
        exit 0
        ;;
    *)
        ssid="${chosen:3:20}"
        ssid="${ssid%"${ssid##*[! ]}"}"
        [ -z "$ssid" ] && exit 0

        if echo "$chosen" | grep -q "(Connected)"; then
            notify-send "Wi-Fi" "Already connected to $ssid" -i network-wireless-connected
            exit 0
        fi

        saved=$(nmcli -t -f NAME connection show | grep -F "$ssid" || true)

        if [ -n "$saved" ]; then
            notify-send "Wi-Fi" "Connecting to $ssid..." -i network-wireless-acquiring
            if nmcli connection up "$ssid"; then
                notify-send "Wi-Fi" "Successfully connected to $ssid" -i network-wireless-connected
            else
                notify-send "Wi-Fi" "Failed to connect to $ssid" -i dialog-error
            fi
        else
            if echo "$chosen" | grep -q ""; then
                pwd=$(rofi -dmenu -password -p "Password for $ssid" -click-to-exit \
                    -theme-str '
                    * { font: "JetBrainsMono Nerd Font 10.5"; background-color: transparent; text-color: #d3c6aa; }
                    window { location: northeast; anchor: northeast; x-offset: -12px; y-offset: 46px; width: 380px; background-color: #141a1af2; border: 1px; border-color: #ffffff24; border-radius: 16px; padding: 14px; }
                    mainbox { children: [ inputbar ]; }
                    inputbar { padding: 8px 12px; background-color: #ffffff0f; border-radius: 10px; children: [ prompt, entry ]; }
                    prompt { text-color: #7fbbb3; margin: 0 8px 0 0; }
                    entry { text-color: #d3c6aa; }
                ')
                [ -z "$pwd" ] && exit 0
                notify-send "Wi-Fi" "Connecting to $ssid..." -i network-wireless-acquiring
                if nmcli device wifi connect "$ssid" password "$pwd"; then
                    notify-send "Wi-Fi" "Successfully connected to $ssid" -i network-wireless-connected
                else
                    notify-send "Wi-Fi" "Failed to connect to $ssid" -i dialog-error
                fi
            else
                notify-send "Wi-Fi" "Connecting to $ssid..." -i network-wireless-acquiring
                if nmcli device wifi connect "$ssid"; then
                    notify-send "Wi-Fi" "Successfully connected to $ssid" -i network-wireless-connected
                else
                    notify-send "Wi-Fi" "Failed to connect to $ssid" -i dialog-error
                fi
            fi
        fi
        ;;
esac
