local home = os.getenv("HOME") or "/home/david"
local wallpaper = home .. "/Pictures/wallpaper.jpg"
local f = io.open(wallpaper, "r")
if f then
    f:close()
else
    wallpaper = "/home/david/Pictures/wallpaper.jpg"
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
    hl.exec_cmd("gsettings set org.gnome.desktop.wm.preferences button-layout 'close,minimize,maximize:'")
end)
