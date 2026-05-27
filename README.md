git am --signoff ../pipxe/patches/0001-gadget_cdrom-add-PXE-mode-ST7735S-display-support-ad.patch
PiPXE — PXE + Gadget CD/USB Launcher
===================================

This repository packages PiPXE: PXE helper scripts, mode management, and
Waveshare ST7735S display integration derived from work on `gadget_cdrom`.

Attribution
-----------
- Upstream project: `gadget_cdrom` by Adam Bambuch (<adam.bambuch2@gmail.com>),
  original repository: https://github.com/tjmnmk/gadget_cdrom
- License: The Beer-Ware License from the upstream project is included in
  `LICENSE` and must be retained when reusing that code.
- This repository includes additional contributions by Matthew L van Winkle
  (mvanwi3@lsu.edu) produced during interactive development; see
  `patches/0001-gadget_cdrom-add-PXE-mode-ST7735S-display-support-ad.patch`
  for the complete set of changes.

Contents
--------
- `gadget_cdrom/` — the full working tree imported from the modified upstream
  project (PXE mode, ST7735S driver, helper scripts, and pi-gen seeds).
- `patches/` — git-format-patch that documents the changes relative to the
  original upstream `gadget_cdrom` repository.
- `LICENSE` — original Beer-Ware license from the upstream project.
- `INSTALL.md` — quick installation and deployment notes.

Applying the patch
------------------
If you already have a clone of the upstream `gadget_cdrom`, you can apply the
included patch like this:

```bash
cd /path/to/gadget_cdrom
git am --signoff ../pipxe/patches/0001-gadget_cdrom-add-PXE-mode-ST7735S-display-support-ad.patch
```

If you want this repository as a standalone package, the `gadget_cdrom/`
directory already contains the full modified source tree — copy it to your Pi
into `/opt/pipxe` and follow `INSTALL.md`.

Contact / Next steps
--------------------
- Repo owner: https://github.com/Zeon012/pipxe
  
Hard fork
---------
This repository is a hard fork of the original `gadget_cdrom` project and is
maintained independently. Changes in this repository will not be proposed or
merged back into the upstream `gadget_cdrom` repository. Use at your own
discretion; retain the original `LICENSE` when reusing upstream code.

