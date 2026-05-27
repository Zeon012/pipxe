Deploy helper

Quick helper to copy the gadget and PXE scripts to a Raspberry Pi and enable the gadget service.

Usage example:

```bash
# from this repo
cd upstream/gadget_cdrom/tools/deploy
./deploy_to_pi.sh --host 10.42.0.12 --user piusb --start-pxe example.ipxe
```

Notes:
- The script creates a tarball of `gadget_cdrom` and `rpi-zero-usb-iso` and copies it to `/tmp` on the Pi.
- It installs PXE helper scripts to `/usr/local/bin/` and copies `gadget_cdrom` to `/opt/pipxe`.
- If a `gadget_cdrom.service` unit is present it will attempt to install and enable it.
- The script may prompt for the remote user's password when running `scp` or `sudo` on the Pi.
- If Python dependencies are required, run on the Pi:

```bash
sudo python3 -m pip install -r /opt/pipxe/requirements.txt
```
