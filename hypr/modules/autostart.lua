local home = os.getenv("HOME") or ""
local wallpaper = home .. "/Pictures/wallpaper.jpg"
local f = io.open(wallpaper, "r")
if f then
    f:close()
else
    local candidates = {
        "/home/simple/sharedDavid/wallpapers/cyan_teal/d3ext_everforest_robin.png",
        "/home/simple/Pictures/wallpaper.jpg",
        "/home/david/Pictures/wallpaper.jpg"
    }
    for _, path in ipairs(candidates) do
        local test_f = io.open(path, "r")
        if test_f then
            test_f:close()
            wallpaper = path
            break
        end
    end
end

hl.on("hyprland.start", function()
    hl.exec_cmd("hyprpm reload -n")
    hl.exec_cmd("/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1")
    hl.exec_cmd("waybar")
    hl.exec_cmd("swaync")
    hl.exec_cmd("swaybg -i " .. wallpaper .. " -m fill")
    hl.exec_cmd("nwg-drawer -r -c 7 -is 64 -spacing 20 -mt 0 -mb 0 -nocats -nofs -ovl")
    hl.exec_cmd("nwg-dock-hyprland -d -hd 20 -i 46 -mb 8 -p bottom -a center -c nwg-drawer -s style.css")
    hl.exec_cmd("nm-applet --indicator")
    hl.exec_cmd("gsettings set org.gnome.desktop.interface color-scheme \x27prefer-dark\x27")
    hl.exec_cmd("gsettings set org.gnome.desktop.interface gtk-theme \x27Adwaita-dark\x27")
    hl.exec_cmd("gsettings set org.gnome.desktop.interface font-name \x27Adwaita Sans 11\x27")
    hl.exec_cmd("gsettings set org.gnome.desktop.interface document-font-name \x27Adwaita Sans 11\x27")
    hl.exec_cmd("gsettings set org.gnome.desktop.interface monospace-font-name \x27Adwaita Mono 11\x27")
    hl.exec_cmd("gsettings set org.gnome.desktop.interface font-antialiasing \x27rgba\x27")
    hl.exec_cmd("gsettings set org.gnome.desktop.interface font-hinting \x27slight\x27")
    hl.exec_cmd("gsettings set org.gnome.desktop.interface font-rgba-order \x27rgb\x27")
    hl.exec_cmd("gsettings set org.gnome.desktop.wm.preferences button-layout 'close,minimize,maximize:'")
end)
