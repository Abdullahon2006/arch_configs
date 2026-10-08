-- =============================================================================
-- Window & layer rules (~/.config/hypr/modules/windowrules.lua)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Apps that should TILE instead of float. Add window classes here
-- (find a class with: hyprctl activewindow | grep class)
-- e.g. local TILE_APPS = { "kitty", "code-oss" }
-- -----------------------------------------------------------------------------
local TILE_APPS = {}

-- macOS-style: every window floats, opens centered, remembers its size
hl.window_rule({
    name = "float-by-default",
    match = { class = ".*" },
    float = true,
    center = true,
    persistent_size = true,
    -- Apps asking to open maximized are ignored (Super+F still works)
    suppress_event = "maximize",
})

if #TILE_APPS > 0 then
    hl.window_rule({
        name = "tile-list",
        match = { class = "^(" .. table.concat(TILE_APPS, "|") .. ")$" },
        float = false,
    })
end

-- Fix some dragging issues with XWayland
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

-- -----------------------------------------------------------------------------
-- Layer surfaces: blur translucent panels/menus
-- -----------------------------------------------------------------------------
local BLUR_LAYERS = {
    "rofi", "waybar", "nwg-drawer", "nwg-dock", "gtk-layer-shell",
    "swaync-control-center", "swaync-notification-window", "logout_dialog",
}
for _, ns in ipairs(BLUR_LAYERS) do
    local alpha_cutoff = (ns:find("swaync") and 0.5) or 0.2
    hl.layer_rule({
        name = "blur-" .. ns,
        match = { namespace = ns },
        blur = true,
        ignore_alpha = alpha_cutoff,
    })
end

-- -----------------------------------------------------------------------------
-- Workspaces: persistent workspaces 1..6
-- -----------------------------------------------------------------------------
for i = 1, 6 do
    hl.workspace_rule({
        workspace = tostring(i),
        persistent = true,
    })
end

