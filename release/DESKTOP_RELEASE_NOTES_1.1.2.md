# SMW Stream Tracker Desktop v1.1.2

Version 1.1.2 is a focused cross-system UI cleanup release.

## Fix

- Prevents delayed outlined-button redraw callbacks from reporting Tkinter's
  `invalid command name` traceback after their popup has already closed.
- Covers both already-destroyed buttons and the narrow race where a button is
  destroyed immediately after its existence check.
- Does not change MiSTer, FXPAK Pro, RetroArch, tracker data, or translated UI
  behavior.

## Downloads

- `SMWStreamTracker.exe` - portable single-file application.
- `SMWStreamTracker_Setup_1.1.2.exe` - complete unsigned installer.
- `SMWStreamTracker_Update_1.1.2.exe` - checksum-verified in-app updater.
- `SMWStreamTracker_macOS_arm64_1.1.2.dmg` - Apple Silicon installer.
- `SMWStreamTracker_macOS_x86_64_1.1.2.dmg` - Intel Mac installer.
- `SMWStreamTracker_Desktop_1.1.2_Source.zip` - complete release source.
- `SHA256SUMS_1.1.2.txt` - SHA-256 checksums for every release artifact.

The application and installers are intentionally unsigned. Windows may show a
SmartScreen warning until the project develops reputation with Microsoft.
