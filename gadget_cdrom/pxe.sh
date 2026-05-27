#!/bin/bash -eu

IDIR="${BASH_SOURCE%/*}"
if [[ ! -d "$IDIR" ]]; then IDIR="$PWD"; fi

ACTION=${1:-stop}
PROFILE=${2:-}
STATE_DIR=/run/pipxe
HTTP_PORT=${PXE_HTTP_PORT:-8080}
PXE_IFACE=${PXE_IFACE:-eth0}
PXE_NETWORK=${PXE_NETWORK:-192.168.72.0/24}
PXE_GATEWAY=${PXE_GATEWAY:-192.168.72.1}
PXE_RANGE_START=${PXE_RANGE_START:-192.168.72.50}
PXE_RANGE_END=${PXE_RANGE_END:-192.168.72.150}

bootloader_bios() {
    for path in \
        /usr/lib/ipxe/undionly.kpxe \
        /usr/share/ipxe/undionly.kpxe \
        /var/lib/tftpboot/undionly.kpxe \
        /srv/tftp/undionly.kpxe; do
        if [ -f "$path" ]; then
            echo "$path"
            return 0
        fi
    done
    return 1
}

bootloader_efi() {
    for path in \
        /usr/lib/ipxe/snponly.efi \
        /usr/share/ipxe/snponly.efi \
        /var/lib/tftpboot/snponly.efi \
        /srv/tftp/snponly.efi; do
        if [ -f "$path" ]; then
            echo "$path"
            return 0
        fi
    done
    return 1
}

stop() {
    if [ -f "$STATE_DIR/http.pid" ]; then
        kill "$(cat "$STATE_DIR/http.pid")" || true
    fi
    if [ -f "$STATE_DIR/dnsmasq.pid" ]; then
        kill "$(cat "$STATE_DIR/dnsmasq.pid")" || true
    fi
    rm -rf "$STATE_DIR"
}

start() {
    if [ ! -f "$PROFILE" ]; then
        echo "PXE profile not found: $PROFILE" >&2
        exit 1
    fi

    if ! command -v dnsmasq >/dev/null 2>&1; then
        echo "dnsmasq is required for PXE mode" >&2
        exit 1
    fi

    if ! command -v python3 >/dev/null 2>&1; then
        echo "python3 is required for PXE mode" >&2
        exit 1
    fi

    mkdir -p "$STATE_DIR"

    PROFILE_REL="${PROFILE#/pxe/}"
    PROFILE_DIR_REL="$(dirname "$PROFILE_REL")"
    PROFILE_DIR_ABS="$(dirname "$PROFILE")"
    mkdir -p "$(dirname "$STATE_DIR/$PROFILE_DIR_REL")"
    ln -sfn "$PROFILE_DIR_ABS" "$STATE_DIR/$PROFILE_DIR_REL"
    cat > "$STATE_DIR/boot.ipxe" <<EOF
#!ipxe
chain http://${PXE_GATEWAY}:${HTTP_PORT}/${PROFILE_REL}
EOF

    TFTP_ROOT="$STATE_DIR/tftp"
    mkdir -p "$TFTP_ROOT"

    if bios_bootloader=$(bootloader_bios); then
        cp "$bios_bootloader" "$TFTP_ROOT/undionly.kpxe"
    fi
    if efi_bootloader=$(bootloader_efi); then
        cp "$efi_bootloader" "$TFTP_ROOT/snponly.efi"
    fi

    cat > "$STATE_DIR/dnsmasq.conf" <<EOF
interface=${PXE_IFACE}
bind-interfaces
dhcp-range=${PXE_RANGE_START},${PXE_RANGE_END},12h
dhcp-option=3,${PXE_GATEWAY}
enable-tftp
tftp-root=${TFTP_ROOT}
dhcp-match=set:ipxe,175
dhcp-match=set:efi64,option:client-arch,7
dhcp-match=set:efi32,option:client-arch,6
dhcp-boot=tag:ipxe,http://${PXE_GATEWAY}:${HTTP_PORT}/boot.ipxe
dhcp-boot=tag:efi64,snponly.efi
dhcp-boot=tag:efi32,snponly.efi
dhcp-boot=undionly.kpxe
EOF

    python3 -m http.server "$HTTP_PORT" --directory "$STATE_DIR" >/dev/null 2>&1 &
    echo $! > "$STATE_DIR/http.pid"

    dnsmasq --no-daemon --keep-in-foreground --conf-file="$STATE_DIR/dnsmasq.conf" >/dev/null 2>&1 &
    echo $! > "$STATE_DIR/dnsmasq.pid"
}

case "$ACTION" in
    start)
        stop
        start
        ;;
    stop)
        stop
        ;;
    *)
        echo "Usage: $0 start <profile> | stop" >&2
        exit 1
        ;;
esac