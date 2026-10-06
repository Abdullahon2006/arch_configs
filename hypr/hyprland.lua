-- =============================================================================
-- saneAspect Hyprland Lua Configuration
-- Entry point: ~/.config/hypr/hyprland.lua
-- =============================================================================

local config_dir = os.getenv("HOME") .. "/.config/hypr"
package.path = package.path .. ";" .. config_dir .. "/?.lua;" .. config_dir .. "/?/init.lua"

require("modules.env")
require("modules.monitors")
require("modules.autostart")
require("modules.input")
require("modules.decorations")
require("modules.layout")
require("modules.misc")
require("modules.windowrules")
require("modules.binds")
