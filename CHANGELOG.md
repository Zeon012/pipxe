# Changelog

All notable changes to this repository are documented here.

## v0.1.0 - 2026-05-27
- Initial import/hard fork of `gadget_cdrom` with additional features:
  - Added PXE mode and PXE helper scripts (`pxe.sh`, `list_pxe.sh`, `insert_pxe.sh`, `remove_pxe.sh`).
  - Added Waveshare ST7735S display support in `gadget_cdrom.py`.
  - Hardened `mode.sh` and `clean.sh` to avoid duplicate loop devices.
  - Added `tools/deploy/deploy_to_pi.sh` to simplify remote deployment.
  - Added pi-gen stage files to include cloud-init seeds for first-boot.
  - Added minimal CI workflow and release tag `v0.1.0`.

## Unreleased
- Tidy menu and controls (debounce, clearer button mappings, confirm->mount, right->toggle mode).

