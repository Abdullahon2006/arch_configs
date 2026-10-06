-- =============================================================================
-- Look & feel (~/.config/hypr/modules/decorations.lua)
-- Everforest dark-slate palette. This is the ONLY place for gaps/borders/blur.
-- =============================================================================
hl.config({
    general = {
        gaps_in = 6,
        gaps_out = 12,
        border_size = 2,
        col = {
            active_border = {
                colors = { "rgba(7fbbb3ee)", "rgba(a7c080ee)" },
                angle = 45,
            },
            inactive_border = "rgba(343f44aa)",
        },
        resize_on_border = true,
        allow_tearing = false,
        layout = "dwindle",
        -- Floating windows snap to edges / each other (macOS-like)
        snap = {
            enabled = true,
            window_gap = 10,
            monitor_gap = 12,
            respect_gaps = true,
        },
    },
    decoration = {
        rounding = 8,
        rounding_power = 2,
        active_opacity = 0.97,
        inactive_opacity = 0.90,
        fullscreen_opacity = 1.0,
        shadow = {
            enabled = true,
            range = 18,
            render_power = 3,
            color = "rgba(14181877)",
        },
        blur = {
            enabled = true,
            size = 6,
            passes = 3,
            vibrancy = 0.1696,
            new_optimizations = true,
            ignore_opacity = true,
        },
    },
    animations = {
        enabled = true,
    },
})

hl.curve("easeOutQuint", { type = "bezier", points = { {0.23, 1}, {0.32, 1} } })
hl.curve("linear", { type = "bezier", points = { {0, 0}, {1, 1} } })
hl.curve("almostLinear", { type = "bezier", points = { {0.5, 0.5}, {0.75, 1} } })
hl.curve("quick", { type = "bezier", points = { {0.15, 0}, {0.1, 1} } })
hl.curve("easy", { type = "spring", mass = 1, stiffness = 71.26, dampening = 15.82 })

hl.animation({ leaf = "global", enabled = true, speed = 6, bezier = "easeOutQuint" })
hl.animation({ leaf = "windows", enabled = true, speed = 4.8, spring = "easy" })
hl.animation({ leaf = "windowsIn", enabled = true, speed = 4.2, spring = "easy", style = "popin 87%" })
hl.animation({ leaf = "windowsOut", enabled = true, speed = 2.0, bezier = "linear", style = "popin 87%" })
hl.animation({ leaf = "border", enabled = true, speed = 4.0, bezier = "quick" })
hl.animation({ leaf = "fadeIn", enabled = true, speed = 1.8, bezier = "almostLinear" })
hl.animation({ leaf = "fadeOut", enabled = true, speed = 1.5, bezier = "almostLinear" })
hl.animation({ leaf = "workspaces", enabled = true, speed = 2.5, bezier = "easeOutQuint", style = "slide" })
