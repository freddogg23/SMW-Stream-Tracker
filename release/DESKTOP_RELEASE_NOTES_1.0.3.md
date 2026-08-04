# SMW Stream Tracker Desktop v1.0.3

This release switches SMW Stream Tracker to unsigned distribution while
keeping update checks and installation available inside the application.

## Changes

- Removes the requirement that the installed application and downloaded
  updater share a Windows publisher signature.
- Continues to download updates only from the HTTPS URL in the official update
  manifest.
- Verifies the complete updater with SHA-256 before it can run.
- Preserves the installed executable and its SHA-256 value before replacement.
- Verifies the saved SHA-256 value before restoring a previous app version.
- Builds the app, complete installer, and updater as unsigned files by design.

## Important transition note

Version 1.0.2 requires a matching Windows publisher signature and therefore
will refuse the unsigned 1.0.3 updater. Install the complete 1.0.3 installer
manually once. After that transition, future unsigned releases can be checked,
downloaded, verified, and started from **File > About & Updates** inside the app.

Because these files are intentionally unsigned, Windows can display **Unknown
publisher** or a Microsoft Defender SmartScreen warning. Verify the SHA-256
values published with the release before running a downloaded file.

## Downloads

- `SMWStreamTracker_Setup_1.0.3.exe` - complete first-time and transition
  installer.
- `SMWStreamTracker_Update_1.0.3.exe` - checksum-verified updater for an
  existing unsigned installation.
- `SMWStreamTracker_Desktop_1.0.3_Source.zip` - complete source, installer
  definitions, documentation, and required assets.

SMW Stream Tracker never includes or downloads a commercial Super Mario World
base ROM. Users must provide their own legally obtained clean ROM when applying
moderated patches.
