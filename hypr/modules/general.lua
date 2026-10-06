hl.config({
    general = {
        gaps_in = 6,
        gaps_out = 12,
        border_size = 2,
        ["col.active_border"] = "rgba(7fbbb3ee) rgba(a7c080ee) 45deg",
        ["col.inactive_border"] = "rgba(343f44aa)",
        layout = "dwindle",
        resize_on_border = true,
        no_cursor_warps = true,
    },
    cursor = {
        no_warps = true,
        warp_on_change_workspace = 0,
        warp_on_monitor_change = 0,
        persistent_warps = true,
    },
    input = {
        kb_layout = "us",
        follow_mouse = 1,
        float_switch_override_focus = 0,
        focus_on_close = 0,
        sensitivity = 0,
        touchpad = {
            natural_scroll = true,
        },
    },
    misc = {
        disable_hyprland_logo = true,
        disable_splash_rendering = true,
        focus_on_activate = false,
        no_cursor_warps = true,
    },
    decoration = {
        rounding = 8,
        active_opacity = 0.95,
        inactive_opacity = 0.88,
        shadow = {
            enabled = true,
            range = 14,
            render_power = 3,
            color = "rgba(14181877)",
        },
        blur = {
            enabled = true,
            size = 6,
            passes = 3,
            new_optimizations = true,
        },
    },
})
