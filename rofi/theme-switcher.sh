#!/bin/bash
THEMES="anime\nariadne\ncatppuccin\ne-ink\neverblush\neverforest"

CHOSEN=$(echo -e "$THEMES" | rofi -dmenu -i -p "Select Theme" -theme-str '
  window {
    width: 380px;
    border-radius: 18px;
    background-color: #141818ee;
    border: 1px solid rgba(255,255,255,0.1);
    padding: 18px;
  }
  inputbar {
    children: [ prompt, entry ];
    padding: 6px 12px;
    background-color: #1e2424;
    border-radius: 10px;
  }
  prompt {
    color: #9ece6a;
    margin: 0 8px 0 0;
  }
  entry {
    color: #c5c8c6;
    placeholder: "Search themes...";
    placeholder-color: #565f89;
  }
  listview {
    lines: 6;
    margin: 12px 0 0 0;
  }
  element {
    padding: 8px 12px;
    border-radius: 8px;
    text-color: #a9b1d6;
  }
  element selected {
    background-color: #2e3838;
    text-color: #ffffff;
  }
')

if [ -n "$CHOSEN" ]; then
    notify-send "Theme Switcher" "Switched theme to $CHOSEN"
fi
