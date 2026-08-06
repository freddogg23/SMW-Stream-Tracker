# SMW Stream Tracker Desktop v1.0.4

Version 1.0.4 is a maintenance release focused on reliable death tracking
when players quit, reopen, or switch between Mario A, B, and C save files.

## Changes

- Prevents the brief save-slot/lives synchronization period from adding a
  false death when selecting another Mario file.
- Keeps the first genuine death countable immediately after the slot handoff.
- Treats the standard SMW death state as a valid first sample after a fast
  reconnect or retry.
- Restores automatic death tracking when a previously started file returns
  directly to a level without visiting the overworld first.
- Improves translated privacy warnings, connection messages, and file-tool
  labels.
- Adds regression coverage for death tracking, downloaded-only random play,
  service health, and streamer privacy.
- Keeps the existing privacy-safe screenshots; no screenshot files changed in
  this maintenance release.

## Downloads

- `SMWStreamTracker_Setup_1.0.4.exe` - complete first-time installer.
- `SMWStreamTracker_Update_1.0.4.exe` - updater for an existing installation.
- `SMWStreamTracker_Desktop_1.0.4_Source.zip` - source, tests, documentation,
  installer definitions, and required assets.
- `SHA256SUMS_1.0.4.txt` - SHA-256 checksums for every release download.

These files are intentionally unsigned, so Windows can display an Unknown
publisher or Microsoft Defender SmartScreen warning. Compare downloaded files
with the published SHA-256 checksums before running them.

SMW Stream Tracker never includes or downloads a commercial Super Mario World
base ROM. Users must provide their own legally obtained clean ROM when applying
moderated patches.
