#!/bin/bash -eu

IDIR="${BASH_SOURCE%/*}"
if [[ ! -d "$IDIR" ]]; then IDIR="$PWD"; fi

MODE=${1:-hdd}

. "$IDIR/clean.sh"

if [ "$MODE" = "hdd" ]; then
    modprobe g_mass_storage file=/iso.img luns=1 stall=0 ro=0 cdrom=0 removable=1
elif [ "$MODE" = "cd" ]; then
    # Attach loop device (create if needed) and mount read-only. Prefer partition p1 if present.
    if [ ! -f /iso.img ]; then
        echo "/iso.img not found" >&2
        exit 1
    fi
    # Reuse existing loop device if present, otherwise create one
    EXISTING=$(losetup -j /iso.img 2>/dev/null | head -n1 | cut -d: -f1 || true)
    if [ -n "$EXISTING" ]; then
        LOOP=$EXISTING
    else
        LOOP=$(losetup --find --show -P /iso.img)
    fi
    # Wait briefly for kernel to create partition nodes
    sleep 0.2
    if [ -b "${LOOP}p1" ]; then
        mount -o ro "${LOOP}p1" /iso
    else
        # No partition table; mount the whole loop device
        mount -o ro "${LOOP}" /iso
    fi
elif [ "$MODE" = "usb" ]; then
    if [ ! -f /iso.img ]; then
        echo "/iso.img not found" >&2
        exit 1
    fi
    LOOP=$(losetup --find --show -P /iso.img)
    sleep 0.2
    if [ -b "${LOOP}p1" ]; then
        mount "${LOOP}p1" /iso
    else
        mount "${LOOP}" /iso
    fi
elif [ "$MODE" = "pxe" ]; then
    true
elif [ "$MODE" = "shutdown" ]; then
    true
fi
