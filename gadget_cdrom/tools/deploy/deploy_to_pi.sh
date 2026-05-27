#!/usr/bin/env bash
# Deploy PiPXE gadget and PXE scripts to a Pi over SSH
# Usage: deploy_to_pi.sh --host 10.42.0.12 [--user piusb] [--dest /home/piusb/pipxe] [--start-pxe profile.ipxe]

set -euo pipefail

HOST=""
USER="piusb"
DEST="/home/${USER}/pipxe"
START_PXE=""
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --host) HOST="$2"; shift 2;;
    --user) USER="$2"; DEST="/home/${USER}/pipxe"; shift 2;;
    --dest) DEST="$2"; shift 2;;
    --start-pxe) START_PXE="$2"; shift 2;;
    --dry-run) DRY_RUN=1; shift;;
    -h|--help) echo "Usage: $0 --host <ip> [--user <user>] [--dest <remote-path>] [--start-pxe <profile.ipxe>] [--dry-run]"; exit 0;;
    *) echo "Unknown arg: $1"; exit 2;;
  esac
done

if [[ -z "$HOST" ]]; then
  echo "--host is required" >&2
  exit 2
fi

echo "Deploying to ${USER}@${HOST}:${DEST}"

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

TMP_TAR="/tmp/pipxe-deploy-$(date +%s).tar.gz"

echo "Creating archive of gadget and PXE files..."
tar -C "$ROOT_DIR" -czf "$TMP_TAR" \
  gadget_cdrom \
  rpi-zero-usb-iso || true

# Also include top-level PXE scripts if present
for f in "$ROOT_DIR"/gadget_cdrom/pxe.sh "$ROOT_DIR"/gadget_cdrom/list_pxe.sh "$ROOT_DIR"/gadget_cdrom/insert_pxe.sh "$ROOT_DIR"/gadget_cdrom/remove_pxe.sh "$ROOT_DIR"/gadget_cdrom/mode.sh; do
  if [[ -f "$f" ]]; then
    rel="$(realpath --relative-to="$ROOT_DIR" "$f")"
    tar -C "$ROOT_DIR" -rzf "$TMP_TAR" "$rel"
  fi
done

echo "Archive created: $TMP_TAR"

if [[ $DRY_RUN -eq 1 ]]; then
  echo "Dry run: not copying to host.";
  exit 0
fi

echo "Copying archive to ${HOST}:/tmp/"
scp "$TMP_TAR" "${USER}@${HOST}:/tmp/" || { echo "scp failed"; exit 3; }

echo "Extracting on remote host and installing..."
ssh "${USER}@${HOST}" bash -s <<'EOF'
set -euo pipefail
DEST="${DEST}"
mkdir -p "$DEST"
tar -C "$DEST" -xzf "/tmp/$(basename "$TMP_TAR")"
# move PXE scripts to /usr/local/bin if present
if [[ -d "$DEST/gadget_cdrom" ]]; then
  if [[ -f "$DEST/gadget_cdrom/pxe.sh" ]]; then
    sudo install -m 0755 "$DEST/gadget_cdrom/pxe.sh" /usr/local/bin/pxe.sh || true
  fi
  for s in list_pxe.sh insert_pxe.sh remove_pxe.sh mode.sh; do
    if [[ -f "$DEST/gadget_cdrom/$s" ]]; then
      sudo install -m 0755 "$DEST/gadget_cdrom/$s" "/usr/local/bin/$s" || true
    fi
  done
  # install gadget_cdrom to /opt/pipxe
  sudo mkdir -p /opt/pipxe
  sudo rsync -a "$DEST/gadget_cdrom/" /opt/pipxe/ || true
  # if requirements.txt exists, prompt user to install deps
  if [[ -f /opt/pipxe/requirements.txt ]]; then
    echo "Found /opt/pipxe/requirements.txt on remote host. Please run: sudo python3 -m pip install -r /opt/pipxe/requirements.txt"
  fi
  # enable & start service if present
  if [[ -f /opt/pipxe/gadget_cdrom.service ]]; then
    sudo install -m 0644 /opt/pipxe/gadget_cdrom.service /etc/systemd/system/ || true
    sudo systemctl daemon-reload || true
    sudo systemctl enable --now gadget_cdrom.service || true
  fi
fi
EOF

echo "Remote install complete."

if [[ -n "$START_PXE" ]]; then
  echo "Starting PXE profile $START_PXE on remote host"
  ssh "${USER}@${HOST}" "sudo /usr/local/bin/pxe.sh start $START_PXE" || echo "Failed to start PXE"
fi

echo "Cleaning local temporary archive"
rm -f "$TMP_TAR"

echo "Done."
