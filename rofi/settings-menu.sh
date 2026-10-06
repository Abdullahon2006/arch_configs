#!/bin/bash
MENU="󰔎 Appearance & GTK Themes (nwg-look)
󰓃 Sound & Volume (pavucontrol)
󰤨 Network & Wi-Fi (nm-connection-editor)
󰂯 Bluetooth Settings (blueman-manager)
󰍹 Display & Monitors
󰝚 Audio Visualizer (Cava)"

CHOSEN=$(echo -e "$MENU" | rofi -dmenu -i -p "Settings" -theme-str '
  window {
    width: 440px;
    border-radius: 18px;
    background-color: #141818ee;
    border: 1px solid rgba(255,255,255,0.1);
    padding: 18px;
  }
  inputbar {
    children: [ prompt, entry ];
    padding: 8px 12px;
    background-color: #1e2424;
    border-radius: 10px;
  }
  prompt {
    color: #7aa2f7;
    margin: 0 8px 0 0;
  }
  entry {
    color: #c5c8c6;
    placeholder: "Search settings...";
    placeholder-color: #565f89;
  }
  listview {
    lines: 6;
    margin: 12px 0 0 0;
  }
  element {
    padding: 10px 14px;
    border-radius: 8px;
    text-color: #a9b1d6;
  }
  element selected {
    background-color: #2e3838;
    text-color: #ffffff;
  }
')

case "$CHOSEN" in
  *"Appearance"*)
    nwg-look || notify-send "Settings" "Install nwg-look: sudo pacman -S nwg-look"
    ;;
  *"Sound"*)
    pavucontrol || notify-send "Settings" "Install pavucontrol: sudo pacman -S pavucontrol"
    ;;
  *"Network"*)
    nm-connection-editor || kitty -e nmtui
    ;;
  *"Bluetooth"*)
    blueman-manager || notify-send "Settings" "Install blueman: sudo pacman -S blueman"
    ;;
  *"Display"*)
    kitty -e hyprctl monitors
    ;;
  *"Visualizer"*)
    kitty --title cava-window -e cava &
    ;;
esac
