Title: Add PXE mode, ST7735S support, and PXE helper scripts

Body:
This PR introduces a PXE mode to `gadget_cdrom`, adds a Waveshare ST7735S
SPI display driver for the UI, and provides helper scripts to serve PXE
profiles (`pxe.sh`, `list_pxe.sh`, `insert_pxe.sh`, `remove_pxe.sh`).

Changes include:
- New `MODE_PXE` support in `gadget_cdrom.py` and UI menu integration.
- `ST7735S` display class using `spidev` and `RPi.GPIO`.
- PXE runtime helper: `pxe.sh` to start/stop dnsmasq + HTTP server.
- pi-gen stage files to include cloud-init seeds for first-boot.
- Hardened `mode.sh` and `clean.sh` to avoid duplicate loop device issues.

Attribution:
- Original project: `gadget_cdrom` by Adam Bambuch (<adam.bambuch2@gmail.com>),
  https://github.com/tjmnmk/gadget_cdrom
- This patch authored by Matthew L van Winkle (mvanwi3@lsu.edu)

Notes:
- Requires `dnsmasq`, `python3`, and system packages for SPI/GPIO/Pillow.
- PXE profiles must be placed under `/pxe/` and referenced by absolute path.
