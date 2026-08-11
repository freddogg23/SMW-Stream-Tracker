# SMW Stream Tracker Desktop v1.0.11

Version 1.0.11 adds native macOS packaging, smoother window and table rendering,
manual tracker entry, reliable custom-hack downloading, FXPAK Pro refresh recovery,
and the latest fully localized blue confirmation dialogs.

## Changes

- Adds native Windows and macOS behavior with reproducible Apple Silicon
  (`arm64`) and Intel (`x86_64`) Mac builds.
- Downloads and configures the official Mac versions of SNI, QUsb2Snes, and
  RetroArch, including the correct bsnes-mercury Performance core.
- Replaces unavailable classic LiveSplit on Mac with synchronized tracker-owned
  Game and Level timer windows plus `game_timer.txt` and `level_timer.txt` for OBS.
- Stores Mac user data under `~/Library/Application Support/SMWStreamTracker`
  so replacing the app does not remove settings, statistics, catalog data, ROM
  mappings, backups, or OBS files.
- Caches expensive banner and table drawing work to make window movement,
  resizing, and My Tracker scrolling substantially smoother.
- Keeps light-blue table borders aligned while scrolling and adds vertical
  dashboard scrolling when the main window is shorter than the full interface.
- Applies saved table styling before My Tracker becomes visible, reducing the
  multicolor startup flash, and improves text rendering throughout the app.
- Adds a translated blue Add to Tracker form with complete hack, progress,
  rating, playtime, date, death, and notes fields.
- Fixes custom unmoderated hacks so adding one does not hide the catalog and so
  it enters Download & Patch Missing Hacks for patching and FXPAK Pro upload.
- Makes the main Refresh button request a safe FXPAK Pro game reset before
  restarting the connection to a running Super Nt session.
- Converts Remove from My Tracker to the translated blue Yes/No dialog while
  preserving the warning about removed progress, ratings, playtime, and notes.
- Retains all v1.0.10 emoji-safe FXPAK aliases, guided setup, OBS, LiveSplit,
  catalog, installer, six-language localization, and update behavior.

## Downloads

- `SMWStreamTracker_Setup_1.0.11.exe` - complete Windows installer and repair package.
- `SMWStreamTracker_Update_1.0.11.exe` - updater for a working Windows installation.
- `SMWStreamTracker_macOS_arm64_1.0.11.dmg` - Apple Silicon drag-to-Applications installer.
- `SMWStreamTracker_macOS_x86_64_1.0.11.dmg` - Intel Mac drag-to-Applications installer.
- Matching Mac ZIP and SHA-256 files for both architectures.
- `SMWStreamTracker_Desktop_1.0.11_Source.zip` - source, tests, documentation,
  packaging definitions, existing screenshots, and required assets.
- `SHA256SUMS_1.0.11.txt` - SHA-256 checksums for the Windows release downloads.

No new screenshots are included for this release. The existing repository
screenshots remain current.

Windows files are intentionally unsigned. Mac builds are signed with the
configured Developer ID when release secrets are available, otherwise they use
ad-hoc signing. Compare downloads with the published SHA-256 checksums.

SMW Stream Tracker never includes or downloads a commercial Super Mario World
base ROM. Users must provide their own legally obtained clean ROM when applying
moderated patches.
