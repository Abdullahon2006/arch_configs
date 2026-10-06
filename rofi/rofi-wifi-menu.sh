#!/usr/bin/env bash

wifi_status=$(nmcli -fields WIFI g 2>/dev/null | tail -n 1 | tr -d ' ')

if [ "$wifi_status" = "enabled" ]; then
    toggle="󰤮  Turn Wi-Fi Off"
else
    toggle="󰤨  Turn Wi-Fi On"
fi

if [ "$wifi_status" = "enabled" ]; then
    wifi_list=$(nmcli --fields "SECURITY,SSID,BARS" device wifi list 2>/dev/null | tail -n +2 | \
        sed 's/  */ /g' | sed -E 's/^ *//;s/ *$//' | \
        awk '{
            sec=$1; bars=$NF;
            $1=""; $NF="";
            ssid=$0;
            sub(/^ */, "", ssid); sub(/ *$/, "", ssid);
            if (ssid != "--" && ssid != "") {
                if (sec == "--") icon="󰤨"; else icon="󰤪";
                print icon " " ssid "  [" bars "]"
            }
        }' | sort -u)
    menu_content="$toggle\n󰑐  Rescan Networks\n⚙  Network Connections\n$wifi_list"
else
    menu_content="$toggle\n⚙  Network Connections"
fi

chosen=$(echo -e "$menu_content" | rofi -dmenu -i -p "Wi-Fi" \
    -theme-str '
    window {
        width: 380px;
        border-radius: 18px;
        background-color: #141818fa;
        border: 2px;
        border-color: #343f44;
        padding: 18px;
        location: top right;
        anchor: top right;
        x-offset: -16px;
        y-offset: 46px;
    }
    entry {
        placeholder: "Search Wi-Fi networks...";
        padding: 8px 12px;
        margin: 0 0 10px 0;
        background-color: #1e2524;
        border-radius: 10px;
        text-color: #d3c6aa;
    }
    listview {
        lines: 8;
        spacing: 4px;
        scrollbar: false;
    }
    element {
        padding: 10px 14px;
        border-radius: 10px;
        text-color: #d3c6aa;
    }
    element selected {
        background-color: #7fbbb3;
        text-color: #1e2524;
        font-weight: bold;
    }
')

if [ -z "$chosen" ]; then
    exit 0
fi

if [[ "$chosen" == *"Turn Wi-Fi Off"* ]]; then
    nmcli radio wifi off
    notify-send "Wi-Fi" "Wi-Fi interface disabled"
elif [[ "$chosen" == *"Turn Wi-Fi On"* ]]; then
    nmcli radio wifi on
    notify-send "Wi-Fi" "Wi-Fi interface enabled"
elif [[ "$chosen" == *"Rescan Networks"* ]]; then
    notify-send "Wi-Fi" "Scanning for available networks..."
    nmcli device wifi rescan
    exec "$0"
elif [[ "$chosen" == *"Network Connections"* ]]; then
    nm-connection-editor &
else
    ssid=$(echo "$chosen" | sed 's/^[󰤨󰤪 ]*//' | sed 's/ *\[.*\]$//')
    connection_exists=$(nmcli -g NAME connection show | grep -Fx "$ssid" || true)
    
    if [ -n "$connection_exists" ]; then
        notify-send "Wi-Fi" "Connecting to $ssid..."
        if nmcli connection up "$ssid"; then
            notify-send "Wi-Fi" "Connected to $ssid successfully!"
        else
            notify-send "Wi-Fi" "Failed to connect to $ssid"
        fi
    else
        pass=$(rofi -dmenu -password -p "Password for $ssid" \
            -theme-str '
            window { width: 320px; border-radius: 16px; background-color: #141818fa; border: 2px; border-color: #7fbbb3; padding: 16px; }
            entry { padding: 10px; background-color: #1e2524; border-radius: 8px; text-color: #d3c6aa; }
            listview { enabled: false; }
            ')
        
        if [ -n "$pass" ]; then
            notify-send "Wi-Fi" "Connecting to $ssid..."
            if nmcli device wifi connect "$ssid" password "$pass"; then
                notify-send "Wi-Fi" "Connected to $ssid!"
            else
                notify-send "Wi-Fi" "Connection failed. Check password."
            fi
        fi
    fi
fi
