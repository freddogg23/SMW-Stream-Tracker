# SMW Stream Tracker Desktop v2.0.2

Version 2.0.2 adds the direct WebSocket OBS companion dock, repairs the Windows
update and install paths, and makes MiSTer setup and launching safer.

## Highlights

- Adds an authenticated OBS companion dock that talks directly to the running
  tracker over a local WebSocket. Each Windows installation receives a unique,
  persistent dock URL.
- Lets users choose which Hack, Creator, Exit Counter, Deaths, Timers, and
  RetroAchievements cards appear in the dock.
- Adds optional Search & Play and Play Random Hack controls, including rating,
  difficulty, type, release, and Hall of Fame filters in Configure.
- Repairs Download and Install, restores the Settings update notification, and
  fixes desktop-shortcut creation during the initial Windows install.
- Bundles complete Paramiko and cryptography support so MiSTer setup works in
  the packaged application.
- Removes the unstable experimental MiSTer Main from setup and all release
  packages, blocks launches while that known-bad build is active, and preserves
  the exact verified restore path for affected MiSTer systems.
- Improves Overview sizing and stability while preserving the fitted Stream
  Desk setup and OBS pages from v2.0.1.

## Windows downloads

- `SMWStreamTracker.exe` - portable single-file Windows application.
- `SMWStreamTracker_Setup_2.0.2.exe` - complete Windows installer.
- `SMWStreamTracker_Update_2.0.2.exe` - checksum-verified in-app updater.
- `SMWStreamTracker_Desktop_2.0.2_Source.zip` - curated release source.
- `SHA256SUMS_2.0.2.txt` - SHA-256 checksums for every generated artifact.

This is a Windows-only release. No macOS files are included because the macOS
build has not been tested. The Windows application and installers are unsigned,
so Windows may show a SmartScreen warning until the project develops reputation.
