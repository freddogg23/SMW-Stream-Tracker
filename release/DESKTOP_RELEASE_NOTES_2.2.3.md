# SMW Stream Tracker Desktop v2.2.3

Version 2.2.3 is a Windows-only reliability update for MiSTer profiles,
automatic save protection, dashboard progress, transfers, and the online SMW
Central music catalog.

## Highlights

- Keeps saved MiSTer hosts and IP addresses attached to the correct console,
  including when multiple systems are powered on at once.
- Transfers only ROMs that are missing from MiSTer SD cards and FXPAK Pro
  cards.
- Saves MiSTer SRAM every five minutes and after important gameplay boundaries:
  level clears, checkpoints, and returns to the overworld map. The tracker
  captures live SRAM, writes it atomically to MiSTer's real basename-only save
  path, verifies the file, and refuses to replace newer valid progress.
- Keeps newer MiSTer Main versions in place instead of overwriting or
  downgrading them during setup.
- Keeps Current exit on the dashboard at all times and changes it to Room number
  with the live Lunar Magic room ID for room-based hacks.
- Improves rapid consecutive death counting and SMW Central platform detection
  for ROMs that share a filename with another platform.
- Shows when the online SMW Central catalog was last updated and continuously
  counts down to its next hourly, on-the-hour refresh.
- Renames Community AI wording to community song results.

## Windows downloads

- `SMWStreamTracker.exe` — portable Windows application.
- `SMWStreamTracker_Setup_2.2.3.exe` — installer for a new Windows setup.
- `SMWStreamTracker_Update_2.2.3.exe` — updater for an existing installation.
- `SMWStreamTracker_Desktop_2.2.3_Source.zip` — Windows release source.
- `SHA256SUMS_2.2.3.txt` — SHA-256 checksums for every release file.

## Windows only

This release does not include a macOS build. Windows may display an unsigned-app
warning because the release is not code-signed.
