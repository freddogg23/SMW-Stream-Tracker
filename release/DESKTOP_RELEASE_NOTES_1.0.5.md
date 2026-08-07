# SMW Stream Tracker Desktop v1.0.5

Version 1.0.5 is an urgent maintenance release that repairs the window-system
runtime used by the packaged Windows app and protects future in-app updates.

## Changes

- Fixes the Tcl/Tk `init.tcl` startup failure that could leave the app unable
  to open after an update.
- Packages a verified Tcl/Tk runtime beside the installed application as a
  stable fallback.
- Runs a real hidden-window startup check before the updater accepts the new
  executable or launches it.
- Automatically restores the previous working executable if that startup
  check fails.
- Makes the release builder refuse to package an executable that cannot pass
  the same startup check.
- Removes a development-only local path from the packaged Tcl startup files.

## Recovery for an affected installation

If an earlier update left SMW Stream Tracker unable to open, close any remaining
tray process and run the complete v1.0.5 installer. Existing tracker data and
settings stored in the user's application-data folder are retained.

## Downloads

- `SMWStreamTracker_Setup_1.0.5.exe` - complete installer and repair package.
- `SMWStreamTracker_Update_1.0.5.exe` - updater for a working installation.
- `SMWStreamTracker_Desktop_1.0.5_Source.zip` - source, tests, documentation,
  installer definitions, and required assets.
- `SHA256SUMS_1.0.5.txt` - SHA-256 checksums for every release download.

These files are intentionally unsigned, so Windows can display an Unknown
publisher or Microsoft Defender SmartScreen warning. Compare downloaded files
with the published SHA-256 checksums before running them.

SMW Stream Tracker never includes or downloads a commercial Super Mario World
base ROM. Users must provide their own legally obtained clean ROM when applying
moderated patches.
