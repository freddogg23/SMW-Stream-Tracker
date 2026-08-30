# SMW Stream Tracker Desktop v2.2.2

Version 2.2.2 is a Windows-only reliability update for capture-card music
identification and MiSTer SRAM saving.

## Highlights

- **Direct capture-card audio:** Music Identifier now has a dedicated
  `Capture card / audio input` source mode. Compatible USB capture devices can
  be selected directly instead of depending on an application to appear in
  Windows Volume Mixer.
- **Fresh device discovery:** Refresh Sources rescans Windows for newly active
  capture devices. OBS is also offered as a fallback when the capture audio is
  available only through an OBS audio session.
- **Automatic MiSTer SRAM saves:** After a confirmed completed level, the
  tracker asks the SNES core to save SRAM in the background without opening
  the MiSTer menu.
- **Verified save completion:** The included MiSTer support now waits for real
  save-data writes and reports a useful warning if the core does not write the
  SRAM. The save request uses the exact online MiSTer profile and address that
  produced the tracking event.

## Windows downloads

- `SMWStreamTracker_Setup_2.2.2.exe` — installer for a new Windows setup.
- `SMWStreamTracker_Update_2.2.2.exe` — updater for an existing installation.
- `SMWStreamTracker.exe` — portable Windows application.
- `SMWStreamTracker_Desktop_2.2.2_Source.zip` — Windows release source.
- `SHA256SUMS_2.2.2.txt` — SHA-256 checksums for every release file.

This release is Windows-only. No macOS files are included because macOS has
not been tested. The executables are unsigned, so Windows may display a
SmartScreen warning.
