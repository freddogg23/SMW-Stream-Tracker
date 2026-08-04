# SMW Stream Tracker Desktop v1.0.4

This maintenance release restores all banner and interface artwork in the
packaged Windows app and fixes update-manifest compatibility.

## Changes

- Restores the full banner, platform artwork, menu images, and application
  photos in packaged builds.
- Packages every banner asset directory used by the desktop application.
- Uses a Python 3.13-compatible Pillow image engine during release builds.
- Accepts update manifests saved as either ordinary UTF-8 or UTF-8 with a
  byte-order mark.
- Generates future update manifests as BOM-free UTF-8.
- Keeps successfully loaded artwork visible if one optional image fails and
  records the failure in the diagnostics log.

## Downloads

- `SMWStreamTracker_Setup_1.0.4.exe` - complete installer for new or existing
  users.
- `SMWStreamTracker_Update_1.0.4.exe` - checksum-verified updater for an
  existing unsigned installation.
- `SMWStreamTracker_Desktop_1.0.4_Source.zip` - complete source, installer
  definitions, documentation, and required assets.

SMW Stream Tracker never includes or downloads a commercial Super Mario World
base ROM. Users must provide their own legally obtained clean ROM when applying
moderated patches.
