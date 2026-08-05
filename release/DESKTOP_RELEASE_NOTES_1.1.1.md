# SMW Stream Tracker Desktop v1.1.1

Version 1.1.1 is a focused feedback-window reliability update.

## Fixes

- Restores Feedback & Suggestions as an in-app Microsoft Forms window.
- Packages pywebview, pythonnet, and the Windows WebView2 bridge in the app,
  installer, and updater builds.
- Detects an embedded-feedback process that exits during startup and displays
  the in-app fallback panel instead of silently doing nothing.
- Keeps the feedback window synchronized with the selected light or dark
  appearance.

## Downloads

- `SMWStreamTracker.exe` - portable single-file application.
- `SMWStreamTracker_Setup_1.1.1.exe` - complete unsigned installer.
- `SMWStreamTracker_Update_1.1.1.exe` - checksum-verified in-app updater.
- `SMWStreamTracker_Desktop_1.1.1_Source.zip` - complete release source.
- `SHA256SUMS_1.1.1.txt` - SHA-256 checksums for every release artifact.

The application and installers are intentionally unsigned. Windows may show a
SmartScreen warning until the project develops reputation with Microsoft.
