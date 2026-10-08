-- =============================================================================
-- Plugins (~/.config/hypr/modules/plugins.lua)
-- Plugins are installed/updated with hyprpm and loaded by `hyprpm reload -n`
-- (see autostart.lua). Everything here is guarded so the config never breaks
-- if a plugin isn't loaded (e.g. right after a Hyprland update).
-- =============================================================================

local function dsp(lua_expr)
    return "hyprctl dispatch '" .. lua_expr .. "'"
end

-- -----------------------------------------------------------------------------
-- hyprbars: macOS-style title bar with traffic-light buttons on the left
-- -----------------------------------------------------------------------------
if hl.plugin and hl.plugin.hyprbars then
    hl.config({
        plugin = {
            hyprbars = {
                enabled = true,
                bar_height = 28,
                bar_color = "rgba(1e2524e6)",
                bar_blur = true,
                bar_padding = 12,
                bar_button_padding = 8,
                bar_buttons_alignment = "left",
                bar_part_of_window = true,
                bar_precedence_over_border = true,
                ["col.text"] = "rgba(d3c6aaff)",
                bar_title_enabled = true,
                bar_text_font = "Inter",
                bar_text_size = 10,
                bar_text_weight = "medium",
                bar_text_align = "center",
                icon_on_hover = true,          -- glyphs appear only on hover, like macOS
                inactive_button_color = "rgba(4f585eff)", -- grey dots on unfocused windows
                on_double_click = dsp('hl.dsp.window.fullscreen({ mode = "maximized", action = "toggle" })'),
            },
        },
    })

    -- Buttons are placed from the aligned edge inwards: close, minimize, maximize
    local fg = "rgba(1e2524ff)"
    hl.plugin.hyprbars.add_button({
        bg_color = "rgba(e67e80ff)", fg_color = fg, size = 13, icon = "",
        action = dsp("hl.dsp.window.close({})"),
    })
    hl.plugin.hyprbars.add_button({
        bg_color = "rgba(dbbc7fff)", fg_color = fg, size = 13, icon = "",
        action = dsp('hl.dsp.window.move({ workspace = "special:minimized" })'),
    })
    hl.plugin.hyprbars.add_button({
        bg_color = "rgba(a7c080ff)", fg_color = fg, size = 13, icon = "",
        action = dsp('hl.dsp.window.fullscreen({ mode = "maximized", action = "toggle" })'),
    })

    -- Apps with their own header bar (GTK4/libadwaita) keep native buttons.
    -- Their buttons are put on the left by the gsettings button-layout in autostart.
    local CSD_APPS = {
        "org\\.gnome\\..*", "nautilus", "firefox", "chromium", "google-chrome",
        "Code", "code-oss", "antigravity", "Antigravity", "blueman-manager",
        "onboard",
    }
    hl.window_rule({
        name = "hyprbars-skip-csd",
        match = { class = "^(" .. table.concat(CSD_APPS, "|") .. ")$" },
        ["hyprbars:no_bar"] = true,
    })
end
