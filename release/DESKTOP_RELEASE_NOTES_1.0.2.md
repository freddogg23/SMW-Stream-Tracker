# SMW Stream Tracker Desktop v1.0.2

This release adds persistent death tracking, recent-hack replay controls, and refined timing for older hacks and opening cutscenes.

## What's new

- Track **Level Deaths** and **Total Deaths** separately on the main screen and in OBS text files.
- Save total deaths per ROM and Mario A, B, or C save slot, even after leaving and replaying a hack.
- Correct game time, level time, Level Deaths, and Total Deaths from the shared override area.
- Replay any of the five most recently played hacks from a centered selector beside **Replay Recent Hack**.
- Store completed totals in the editable **Total Deaths** My Tracker column.
- Show a yellow asterisk for hacks completed before death tracking existed, while still allowing the value to be entered later.
- Ignore opening cutscenes when starting the level timer or counting deaths.
- Keep older-hack level timing active through death-to-overworld transitions, then reset after a confirmed clear or new level.
- Detect the first death and short death transitions more reliably without counting one death twice.

## Downloads

- `SMWStreamTracker_Setup_1.0.2.exe` — complete first-time installer.
- `SMWStreamTracker_Update_1.0.2.exe` — updater for an existing installation.
- `SMWStreamTracker.exe` — portable desktop application.
- `SMWStreamTracker_Desktop_1.0.2_Source.zip` — source, tests, installer definitions, documentation, and required assets.
- `SHA256SUMS_1.0.2.txt` — checksums for verifying every download.

SMW Stream Tracker never includes or downloads a commercial Super Mario World base ROM. Users must provide their own legally obtained clean ROM when applying moderated patches.
