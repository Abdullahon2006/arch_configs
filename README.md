# Arch Hyprland Dotfiles (Everforest Edition) 🌲✨

A modern, highly polished Arch Linux setup powered by **Hyprland (Lua configuration)**, featuring a cohesive **Everforest Dark** glass aesthetic, native **GTK Layer Shell** popup menus, and seamless touch/tablet support.

---

## 📸 Overview & Features

- **Window Manager**: [Hyprland](https://hyprland.org/) configured with modern **Lua** architecture (`~/.config/hypr/modules/`).
- **Window Behavior**: macOS-style floating-by-default with centered placement, persistent window sizes, and `hyprbars` native buttons.
- **Top Bar**: [Waybar](https://github.com/Alexays/Waybar) designed as a floating, blurred pill bar with grouped status icons and numbered workspace controls.
- **Native GTK Layer Shell Popups** (`~/.config/waybar/menus/`):
  - 🔊 **Volume & Audio**: Smooth output and microphone sliders, mute toggles, live output device switcher (Speakers, Headphones, HDMI, Bluetooth), and Pavucontrol launcher.
  - 📶 **Wi-Fi**: Live network scanner with signal strength indicators, search bar, and inline password authentication.
  - 󰂯 **Bluetooth**: Power toggle, nearby scanning, paired devices list with connect/disconnect actions, and Blueman shortcut.
  - 󰂄 **Battery**: Live battery percentage, power status, and `powerprofilesctl` profile switcher (Performance, Balanced, Power-saver).
  - ⏻ **Power & Session**: Clean shutdown, reboot, suspend, hibernate, lock screen, and logout actions.
  - 🖱️ **Universal Dismissal**: All popups cleanly dismiss when clicking anywhere outside their boundaries or pressing <kbd>Esc</kbd>.
- **Tablet & Touch Mode**: [Onboard](https://launchpad.net/onboard) Full Keyboard integration with a dedicated toggle button (`󰌌`) directly on Waybar.
- **Notification Center**: [SwayNC](https://github.com/ErikReider/SwayNotificationCenter) customized with an Everforest glass theme and aligned background blur.
- **App Launcher & Menus**: [Rofi](https://github.com/davatorium/rofi) styled with translucent frosted glass and rounded cards.
- **Terminal**: [Kitty](https://sw.kovidgoyal.net/kitty/) with Everforest palette, background blur, and JetBrainsMono Nerd Font.
- **Lock Screen**: [Hyprlock](https://github.com/hyprwm/hyprlock) with frosted wallpaper background and minimalist clock.

---

## ⌨️ Keybindings Cheatsheet

| Keybinding | Action |
| :--- | :--- |
| <kbd>Super</kbd> + <kbd>Return</kbd> | Open Terminal ([Kitty](https://sw.kovidgoyal.net/kitty/)) |
| <kbd>Super</kbd> + <kbd>Space</kbd> / <kbd>D</kbd> | Application Launcher ([nwg-drawer](https://github.com/nwg-piotr/nwg-drawer)) |
| <kbd>Super</kbd> + <kbd>E</kbd> | File Manager (Nautilus) |
| <kbd>Super</kbd> + <kbd>Q</kbd> | Close Active Window |
| <kbd>Super</kbd> + <kbd>F</kbd> / <kbd>F11</kbd> | Toggle Fullscreen |
| <kbd>Super</kbd> + <kbd>V</kbd> | Toggle Float Mode |
| <kbd>Super</kbd> + <kbd>L</kbd> | Lock Screen ([Hyprlock](https://github.com/hyprwm/hyprlock)) |
| <kbd>Super</kbd> + <kbd>I</kbd> | Desktop Settings Menu ([Rofi](https://github.com/davatorium/rofi)) |
| <kbd>Super</kbd> + <kbd>1</kbd> .. <kbd>6</kbd> | Switch to Workspace 1–6 |
| <kbd>Super</kbd> + <kbd>Shift</kbd> + <kbd>1</kbd> .. <kbd>6</kbd> | Move Active Window to Workspace 1–6 |
| <kbd>Print</kbd> / <kbd>Super</kbd> + <kbd>Shift</kbd> + <kbd>S</kbd> | Area Screenshot ([Grim](https://sr.ht/~emersion/grim/) + [Slurp](https://github.com/mvaldes14/slurp)) |
| <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>Esc</kbd> | Task Manager (`htop`) |

---

## 📦 Required Packages & Dependencies

Install the core dependencies on Arch Linux:

```bash
# Core Compositor & Tools
sudo pacman -S hyprland waybar swaync rofi kitty grim slurp swaybg polkit-gnome

# Audio & Networking
sudo pacman -S pipewire wireplumber pavucontrol networkmanager network-manager-applet bluez bluez-utils blueman

# Power Management & Utilities
sudo pacman -S power-profiles-daemon onboard brightnessctl

# Fonts
sudo pacman -S ttf-jetbrains-mono-nerd noto-fonts-emoji inter-font

# GTK Layer Shell & Python bindings (needed for Waybar popups)
sudo pacman -S gtk-layer-shell python-gobject
```

Optional launchers:
```bash
# Launchpad & Dock (from AUR)
yay -S nwg-drawer nwg-dock-hyprland
```

---

## 🚀 Installation & Setup

1. **Backup existing configs**:
   ```bash
   cp -r ~/.config ~/.config.backup
   ```

2. **Clone the repository**:
   ```bash
   git clone https://github.com/Abdullahon2006/arch_configs.git ~/.config
   ```

3. **Wallpaper**:
   Place your preferred wallpaper at `~/Pictures/wallpaper.jpg` (or update the path in `hypr/modules/autostart.lua` and `hypr/hyprlock.conf`).

4. **Start or Reload Hyprland**:
   - Reload running Hyprland: `hyprctl reload`
   - Reload Waybar: `killall -SIGUSR2 waybar`

---

## 🎨 Color Palette (Everforest)

- **Background**: `#1e2524` / `#141818` (Translucent glass: `rgba(20, 26, 26, 0.94)`)
- **Foreground / Text**: `#d3c6aa`
- **Subtext / Dim**: `#859289`
- **Teal / Accent**: `#7fbbb3`
- **Green**: `#a7c080`
- **Red / Warning**: `#e67e80`
- **Yellow / Accent**: `#dbbc7f`
