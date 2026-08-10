# SMW Stream Tracker Desktop v1.0.10

Version 1.0.10 focuses on reliable FXPAK Pro emoji handling, a clearer guided
setup, catalog and OBS fixes, and the completed branded Windows installer.

## Changes

- Replaces every emoji in an FXPAK Pro ROM filename with its readable Unicode
  name while preserving the official hack title everywhere inside the tracker.
- Links FXPAK-only aliases to permanent SMW Central IDs, repairs older local
  emoji-named ROMs, and uploads a missing alias automatically when needed.
- Corrects the FXPAK missing-ROM status so successfully uploaded emoji aliases
  are recognized instead of being reported as missing.
- Temporarily releases and restores the live SNI/QUsb2Snes connection during
  FXPAK transfers so the tracker cannot block its own upload.
- Corrects the guided connection gate: QUsb2Snes can advance alone, while
  choosing SNI or RetroArch requires both SNI and RetroArch to be completed.
- Removes completed setup highlights so only the remaining required connection
  option continues flashing.
- Adds the blue OBS feature chooser after app setup, with separate OBS text-file
  and two-timer LiveSplit setup paths that link to one another.
- Moves LiveSplit Timer Setup into Help > Setup beside App Setup and OBS Text
  Setup, with translated labels in all six supported languages.
- Fixes OBS Text File Setup so a missing output folder can be selected, created,
  saved, and immediately displayed for copying into OBS or Streamlabs.
- Adds a translated Reset Catalog control with a recovery backup while
  preserving tracker progress, custom hacks, ROM mappings, and ROM files.
- Prevents the catalog status card from showing a permanent false new-moderated
  count when the live SMW Central catalog is ahead of its GitHub mirror.
- Adds a fully branded dark-blue installer, optional portable RetroArch setup,
  reusable folder choices, and an optional OBS output folder.
- Allows one installed copy per Windows account and offers fresh reinstall or
  complete uninstall choices while preserving RetroArch, SNI, QUsb2Snes, and
  every ROM file.
- Shows the branded welcome/setup splash on every true fresh installation and
  uses translated blue confirmation dialogs for detected optional tools.
- Includes all localization, popup, table, scrollbar, statistics, downloader,
  catalog, timer, and setup reliability improvements completed for this release.

## Downloads

- `SMWStreamTracker_Setup_1.0.10.exe` - complete installer and repair package.
- `SMWStreamTracker_Update_1.0.10.exe` - updater for a working installation.
- `SMWStreamTracker_Desktop_1.0.10_Source.zip` - source, tests, documentation,
  installer definitions, existing screenshots, and required assets.
- `SHA256SUMS_1.0.10.txt` - SHA-256 checksums for every release download.

No new screenshots are included for this release. The existing repository
screenshots remain current.

These files are intentionally unsigned, so Windows can display an Unknown
publisher or Microsoft Defender SmartScreen warning. Compare downloaded files
with the published SHA-256 checksums before running them.

SMW Stream Tracker never includes or downloads a commercial Super Mario World
base ROM. Users must provide their own legally obtained clean ROM when applying
moderated patches.
