# SMW Stream Tracker Desktop v1.0.3

Version 1.0.3 improves multilingual use, connection setup, timer reliability,
random selection, multi-monitor behavior, and the built-in health check.

## Highlights

- Adds **File > Language** and immediately rebuilds the interface in the
  selected language.
- Translates the **Search or select a hack** prompt and keeps the open result
  list attached when the app moves between monitors.
- Keeps the full banner composition readable in smaller, non-maximized windows.
- Gives SNI and QUsb2Snes separate setup fields so either service can be
  configured and used independently.
- Adds in-app discovery and installation for SNI, QUsb2Snes, RetroArch, and the
  recommended RetroArch SNES core.
- Correctly reports a live RetroArch Network Commands connection as ready in
  Setup & Health Check.
- Limits **Play Random Hack** to downloaded games that can launch on the
  selected platform.
- Improves resumed-save death tracking, game-timer startup, and castle-clear
  behavior.
- Removes the duplicate About command from File; About & Updates remains in
  Help.
- Removes the local database path from the Statistics header for safer
  screenshots and streams.
- Adds a Testers credit thanking **Jole_12** for testing, detailed feedback,
  and contributions.
- Refreshes the repository screenshots without showing personal file paths.

## Downloads

- `SMWStreamTracker_Setup_1.0.3.exe` - complete first-time installer.
- `SMWStreamTracker_Update_1.0.3.exe` - updater for an existing installation.
- `SMWStreamTracker_Desktop_1.0.3_Source.zip` - source, tests, documentation,
  installer definitions, and required assets.
- `SHA256SUMS_1.0.3.txt` - SHA-256 checksums for every release download.

These files are intentionally unsigned, so Windows can display an Unknown
publisher or Microsoft Defender SmartScreen warning. Compare downloaded files
with the published SHA-256 checksums before running them.

SMW Stream Tracker never includes or downloads a commercial Super Mario World
base ROM. Users must provide their own legally obtained clean ROM when applying
moderated patches.
