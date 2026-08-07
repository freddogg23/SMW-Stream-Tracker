# SMW Stream Tracker Desktop v1.0.6

Version 1.0.6 improves the tracker and catalog workflows, adds clearer update
notifications, and fixes several interface and launch issues found during testing.

## Changes

- Shows an update badge on Help and a red dot beside About & Updates only when
  a newer published release is actually available.
- Flashes the About & Updates button between Check for Updates and Update
  Available while a newer release is available.
- Adds filtered random-hack selection that only launches downloaded and patched
  ROMs, with Confirm and Cancel controls.
- Recognizes downloaded catalog games from direct paths, platform mappings,
  FXPAK mappings, and the configured local ROM library.
- Makes playable catalog titles yellow and allows them to be launched directly.
- Adds navigation between Overview and My Tracker and moves spreadsheet import,
  export, and Google Sheets tools into My Tracker.
- Improves full-screen child-window scaling and centers the catalog filter layout.
- Fixes the update-badge startup crash caused by raising a Tk canvas without an
  item identifier.
- Adds and improves translations for the new tracker, catalog, random-play, and
  update controls.

## Downloads

- `SMWStreamTracker_Setup_1.0.6.exe` - complete installer and repair package.
- `SMWStreamTracker_Update_1.0.6.exe` - updater for a working installation.
- `SMWStreamTracker_Desktop_1.0.6_Source.zip` - source, tests, documentation,
  installer definitions, and required assets.
- `SHA256SUMS_1.0.6.txt` - SHA-256 checksums for every release download.

These files are intentionally unsigned, so Windows can display an Unknown
publisher or Microsoft Defender SmartScreen warning. Compare downloaded files
with the published SHA-256 checksums before running them.

SMW Stream Tracker never includes or downloads a commercial Super Mario World
base ROM. Users must provide their own legally obtained clean ROM when applying
moderated patches.
