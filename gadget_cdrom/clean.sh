#!/bin/bash -eu

# Clean up any previously-configured gadget or loop devices for /iso.img
if lsmod | grep -q g_mass_storage; then
    rmmod g_mass_storage || true
fi

# Find all loop devices associated with /iso.img and detach them
while read -r LOOPDEV; do
    LOOPDEV=$(echo "$LOOPDEV" | cut -d: -f1)
    if [ -z "$LOOPDEV" ]; then
        continue
    fi
    # Try to unmount partition p1 if mounted
    if mountpoint -q /iso; then
        umount "${LOOPDEV}p1" || true
    fi
    # Detach the loop device
    losetup -d "$LOOPDEV" || true
done < <(losetup -j /iso.img 2>/dev/null || true)

# Ensure mountpoint is clean
if mountpoint -q /iso; then
    umount /iso || true
fi
