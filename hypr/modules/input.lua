-- =============================================================================
-- Input & cursor (~/.config/hypr/modules/input.lua)
-- =============================================================================
hl.config({
    input = {
        kb_layout = "us",
        follow_mouse = 1,
        sensitivity = 0,
        accel_profile = "flat",
        -- Don't steal focus / warp when floating windows appear or close
        float_switch_override_focus = 0,
        focus_on_close = 0,
        touchpad = {
            natural_scroll = true,
            tap_to_click = true,
        },
    },
    -- Stop the cursor teleporting to newly focused windows
    cursor = {
        no_warps = true,
        persistent_warps = true,
        warp_on_change_workspace = 0,
        warp_on_toggle_special = 0,
    },
})

hl.gesture({
    fingers = 3,
    direction = "horizontal",
    action = "workspace",
})
