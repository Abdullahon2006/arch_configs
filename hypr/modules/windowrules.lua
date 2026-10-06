-- Window Rules (~/.config/hypr/modules/windowrules.lua)
hl.window_rule({
    name = "fix-xwayland-drags",
    match = {
        class = "^$",
        title = "^$",
        xwayland = true,
        float = true,
        fullscreen = false,
        pin = false,
    },
    no_focus = true,
})

hl.window_rule({
    name = "utility-float",
    match = { class = "^(pavucontrol|blueman-manager|nm-connection-editor|qt6ct|nwg-look)$" },
    float = true,
})

hl.window_rule({
    name = "cava-floating",
    match = { title = "cava-window" },
    float = true,
})
