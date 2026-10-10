-- =============================================================================
-- Keybindings (~/.config/hypr/modules/binds.lua)
-- =============================================================================

-- Applications
hl.bind("SUPER + Return", hl.dsp.exec_cmd("kitty"))
hl.bind("CTRL + ALT + T", hl.dsp.exec_cmd("kitty"))
hl.bind("SUPER + E", hl.dsp.exec_cmd("nautilus --new-window"))
hl.bind("SUPER + Space", hl.dsp.exec_cmd("nwg-drawer"))
hl.bind("SUPER + D", hl.dsp.exec_cmd("nwg-drawer"))
hl.bind("SUPER + I", hl.dsp.exec_cmd("XDG_CURRENT_DESKTOP=GNOME gnome-control-center"))
hl.bind("CTRL + SHIFT + Escape", hl.dsp.exec_cmd("kitty -e htop"))
hl.bind("SUPER + Escape", hl.dsp.exec_cmd("bash ~/.config/rofi/powermenu.sh"))

-- Lock Screen (Super + L)
hl.bind("SUPER + L", hl.dsp.exec_cmd("hyprlock"))

-- Window Management (Closing, Fullscreen, Floating)
hl.bind("SUPER + Q", hl.dsp.window.close({}))
hl.bind("ALT + F4", hl.dsp.window.close({}))
hl.bind("SUPER + F", hl.dsp.window.fullscreen({ action = "toggle" }))
hl.bind("F11", hl.dsp.window.fullscreen({ action = "toggle" }))
hl.bind("SUPER + V", hl.dsp.window.float({ action = "toggle" }))

-- Alt + Tab & Super + Tab (Window Cycling + Bring to Top)
hl.bind("ALT + Tab", hl.dsp.window.cycle_next())
hl.bind("ALT + Tab", hl.dsp.window.bring_to_top())
hl.bind("SUPER + Tab", hl.dsp.window.cycle_next())
hl.bind("SUPER + Tab", hl.dsp.window.bring_to_top())
hl.bind("ALT + SHIFT + Tab", hl.dsp.window.cycle_next({ next = false }))
hl.bind("ALT + SHIFT + Tab", hl.dsp.window.bring_to_top())
hl.bind("SUPER + SHIFT + Tab", hl.dsp.window.cycle_next({ next = false }))
hl.bind("SUPER + SHIFT + Tab", hl.dsp.window.bring_to_top())

-- Window Minimization / Hiding (scratchpad special workspace)
hl.bind("SUPER + M", hl.dsp.window.move({ workspace = "special:minimized" }))
hl.bind("SUPER + H", hl.dsp.window.move({ workspace = "special:minimized" }))
hl.bind("SUPER + SHIFT + M", hl.dsp.workspace.toggle_special("minimized"))

-- Screenshots
hl.bind("Print", hl.dsp.exec_cmd("grim -g \"$(slurp)\" - | wl-copy && notify-send 'Screenshot' 'Copied to clipboard'"))
hl.bind("SUPER + SHIFT + S", hl.dsp.exec_cmd("grim -g \"$(slurp)\" - | wl-copy && notify-send 'Screenshot' 'Copied to clipboard'"))

-- Move Focus with Arrow Keys
hl.bind("SUPER + Left", hl.dsp.focus({ direction = "l" }))
hl.bind("SUPER + Right", hl.dsp.focus({ direction = "r" }))
hl.bind("SUPER + Up", hl.dsp.focus({ direction = "u" }))
hl.bind("SUPER + Down", hl.dsp.focus({ direction = "d" }))

-- Move Windows with Shift + Arrows
hl.bind("SUPER + SHIFT + Left", hl.dsp.window.swap({ direction = "l" }))
hl.bind("SUPER + SHIFT + Right", hl.dsp.window.swap({ direction = "r" }))
hl.bind("SUPER + SHIFT + Up", hl.dsp.window.swap({ direction = "u" }))
hl.bind("SUPER + SHIFT + Down", hl.dsp.window.swap({ direction = "d" }))

-- Workspaces 1..9, 10 (0)
for i = 1, 9 do
    hl.bind("SUPER + " .. tostring(i), hl.dsp.focus({ workspace = tostring(i) }))
    hl.bind("SUPER + SHIFT + " .. tostring(i), hl.dsp.window.move({ workspace = tostring(i) }))
end
hl.bind("SUPER + 0", hl.dsp.focus({ workspace = "10" }))
hl.bind("SUPER + SHIFT + 0", hl.dsp.window.move({ workspace = "10" }))

-- Workspace cycling & mouse scroll
hl.bind("SUPER + bracketleft", hl.dsp.focus({ workspace = "m-1" }))
hl.bind("SUPER + bracketright", hl.dsp.focus({ workspace = "m+1" }))
hl.bind("SUPER + CTRL + Left", hl.dsp.focus({ workspace = "m-1" }))
hl.bind("SUPER + CTRL + Right", hl.dsp.focus({ workspace = "m+1" }))
hl.bind("SUPER + mouse_down", hl.dsp.focus({ workspace = "m+1" }), { mouse = true })
hl.bind("SUPER + mouse_up", hl.dsp.focus({ workspace = "m-1" }), { mouse = true })


-- Mouse Bindings: Super + Left Click Drag (Move) & Super + Right Click Drag (Resize)
hl.bind("SUPER + mouse:272", hl.dsp.window.drag(), { mouse = true })
hl.bind("SUPER + mouse:273", hl.dsp.window.resize(), { mouse = true })

-- Audio & Brightness
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("wpctl set-volume -l 1.0 @DEFAULT_AUDIO_SINK@ 5%+"), { repeating = true, locked = true })
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"), { repeating = true, locked = true })
hl.bind("XF86AudioMute", hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"), { locked = true })
hl.bind("XF86AudioMicMute", hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle"), { locked = true })
hl.bind("XF86MonBrightnessUp", hl.dsp.exec_cmd("brightnessctl set +5%"), { repeating = true })
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd("brightnessctl set 5%-"), { repeating = true })
