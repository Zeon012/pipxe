PiPXE — PXE + Gadget CD/USB Launcher
===================================

This repository is a focused extraction of the PiPXE work (PXE helper scripts,
mode management, and ST7735S display integration) created during a development
session based on the original `gadget_cdrom` project.

Attribution
-----------
- Original project: gadget_cdrom by Adam Bambuch (<adam.bambuch2@gmail.com>) and
  maintained at https://github.com/tjmnmk/gadget_cdrom
- This repo contains additional code and helpers developed by Matthew L van Winkle
  (mvanwi3@lsu.edu) during an interactive session; see the attached patch for the
  full set of changes.

Contents
--------
- `patches/` — a git-format-patch file describing the changes added to the
  original `gadget_cdrom` repository (PXE mode, ST7735S driver, scripts).
- `LICENSE` — original beer-ware license from the upstream project.
- `INSTALL.md` — quick installation and deployment notes.

Applying the patch
------------------
To apply the included patch to a local clone of `gadget_cdrom`:

```bash
cd /path/to/gadget_cdrom
git am --signoff ../pipxe/patches/0001-gadget_cdrom-add-PXE-mode-ST7735S-display-support-ad.patch
```

If you prefer to keep this as a standalone repo, review the files in
`patches/` and copy the scripts you need into the target device.

Next steps
----------
- Push this repository to your GitHub account and open a PR against the upstream
  `tjmnmk/gadget_cdrom` if you want the changes merged upstream.
- Optionally I can push this branch to your fork and create the PR for you.

