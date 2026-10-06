hl.layer_rule({ match = { address = "rofi" }, blur = true, ignorezero = true })
hl.layer_rule({ match = { address = "nwg-drawer" }, blur = true, ignorezero = true })
hl.layer_rule({ match = { address = "gtk-layer-shell" }, blur = true, ignorezero = true })

-- Enable size persistence on all windows
hl.window_rule({
    match = { class = ".*" },
    persistent_size = true,
})

-- Common dialogs and tools float automatically
hl.window_rule({ match = { class = "pavucontrol" }, float = true })
hl.window_rule({ match = { class = "blueman-manager" }, float = true })
hl.window_rule({ match = { class = "nm-connection-editor" }, float = true })
hl.window_rule({ match = { class = "gnome-control-center" }, float = true, size = { 1020, 640 } })
