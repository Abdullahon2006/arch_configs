-- =============================================================================
-- Input & cursor (~/.config/hypr/modules/input.lua)
-- =============================================================================
hl.config({
    input = {
        kb_layout = "us",
        follow_mouse = 1,
        sensitivity = 0,
        accel_profile = "flat",
        float_switch_override_focus = 0,
        focus_on_close = 0,
        touchpad = {
            natural_scroll = true,
            tap_to_click = true,
        },
    },
    cursor = {
        no_warps = true,
        persistent_warps = true,
        warp_on_change_workspace = 0,
        warp_on_toggle_special = 0,
    },
    gestures = {
        workspace_swipe_distance = 300,
        workspace_swipe_cancel_ratio = 0.5,
        workspace_swipe_create_new = true,
        workspace_swipe_forever = true,
    },
})

hl.gesture({
    fingers = 3,
    direction = "horizontal",
    action = "workspace",
})

local home = os.getenv("HOME")
hl.gesture({
    fingers = 3,
    direction = "up",
    action = function()
        hl.exec_cmd("python3 " .. home .. "/.config/hypr/scripts/mission_control.py")
    end,
})
