hl.config({
    general = {
        gaps_in = 6,
        gaps_out = 14,
        border_size = 2,
        col = {
            active_border = {
                colors = { "rgba(89b4faee)", "rgba(cba6f7ee)" },
                angle = 45,
            },
            inactive_border = "rgba(313244aa)",
        },
        resize_on_border = true,
        allow_tearing = false,
        layout = "dwindle",
    },
    decoration = {
        rounding = 16,
        rounding_power = 4,
        active_opacity = 0.96,
        inactive_opacity = 0.88,
        fullscreen_opacity = 1.0,
        shadow = {
            enabled = true,
            range = 24,
            render_power = 3,
            color = 0x66000000,
        },
        blur = {
            enabled = true,
            size = 8,
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
