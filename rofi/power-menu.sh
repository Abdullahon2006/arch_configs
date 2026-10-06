#!/bin/bash
OPTIONS="󰐥 Shutdown\n󰜉 Reboot\n󰤄 Suspend\n󰌾 Lock\n󰍃 Logout"

CHOSEN=$(echo -e "$OPTIONS" | rofi -dmenu -i -p "Power" -theme-str '
  window {
    width: 280px;
    border-radius: 18px;
    background-color: #141818ee;
    border: 1px solid rgba(255,255,255,0.1);
    padding: 16px;
  }
  inputbar { enabled: false; }
  listview { lines: 5; margin: 0; }
  element {
    padding: 10px 14px;
    border-radius: 10px;
    text-color: #c5c8c6;
  }
  element selected {
    background-color: #7aa2f7;
    text-color: #1a1b26;
    font-weight: bold;
  }
')

case "$CHOSEN" in
  *"Shutdown"*) systemctl poweroff ;;
  *"Reboot"*)   systemctl reboot ;;
  *"Suspend"*)  systemctl suspend ;;
  *"Lock"*)     hyprlock ;;
  *"Logout"*)   hyprctl dispatch exit ;;
esac
