#!/usr/bin/env bash
# =============================================================================
# Fix hibernation (run once with: sudo bash ~/.config/hypr/scripts/system/fix-hibernate.sh)
#
# Problem: the hibernate image is written to /swap/swapfile, but the initramfs
# has no `resume` hook, so on boot nothing restores it -> looks like power-off.
# Fix: add `resume` hook + explicit resume=/resume_offset= kernel params,
#      then rebuild the UKI. Backups of every touched file are made first.
# =============================================================================
set -euo pipefail

[[ $EUID -eq 0 ]] || { echo "Run with sudo"; exit 1; }

TS=$(date +%Y%m%d-%H%M%S)
SWAPFILE=/swap/swapfile
ROOT_UUID=$(findmnt -no UUID /)

echo "==> Backups (.bak-$TS)"
cp -v /etc/mkinitcpio.conf "/etc/mkinitcpio.conf.bak-$TS"
cp -v /etc/kernel/cmdline  "/etc/kernel/cmdline.bak-$TS"

echo "==> Sanity checks"
SWAP_BYTES=$(stat -c %s "$SWAPFILE")
RAM_BYTES=$(awk '/MemTotal/ {print $2*1024}' /proc/meminfo)
echo "    swapfile: $((SWAP_BYTES/1024/1024/1024)) GiB   RAM: $((RAM_BYTES/1024/1024/1024)) GiB"
(( SWAP_BYTES >= RAM_BYTES * 6 / 10 )) || echo "    WARNING: swapfile may be too small for a full RAM image"

OFFSET=$(btrfs inspect-internal map-swapfile -r "$SWAPFILE")
echo "    root UUID: $ROOT_UUID   resume_offset: $OFFSET"

echo "==> Adding 'resume' hook to mkinitcpio HOOKS"
if grep -qE '^HOOKS=.*\bresume\b' /etc/mkinitcpio.conf; then
    echo "    already present"
else
    sed -i -E '/^HOOKS=/ s/\bfilesystems\b/resume filesystems/' /etc/mkinitcpio.conf
fi
grep -E '^HOOKS=' /etc/mkinitcpio.conf

echo "==> Setting resume= / resume_offset= in /etc/kernel/cmdline"
CMD=$(cat /etc/kernel/cmdline)
CMD=$(echo "$CMD" | sed -E 's/\s*resume=[^ ]+//g; s/\s*resume_offset=[^ ]+//g')
echo "$CMD resume=UUID=$ROOT_UUID resume_offset=$OFFSET" > /etc/kernel/cmdline
cat /etc/kernel/cmdline

echo "==> Rebuilding UKI (mkinitcpio -P)"
mkinitcpio -P

echo
echo "Done. Reboot once, then test with:  systemctl hibernate"
echo "To undo: cp /etc/mkinitcpio.conf.bak-$TS /etc/mkinitcpio.conf && cp /etc/kernel/cmdline.bak-$TS /etc/kernel/cmdline && mkinitcpio -P"
