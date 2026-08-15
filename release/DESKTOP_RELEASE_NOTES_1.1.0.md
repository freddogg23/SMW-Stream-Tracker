# SMW Stream Tracker Desktop v1.1.0

Version 1.1.0 makes MiSTer FPGA a complete supported platform, adds six new
Game Modes, improves tracker import and recovery, and keeps every new screen
fully translated across all six supported languages.

## Highlights

- Adds one-click MiSTer discovery and setup over the local network, remote ROM
  upload and launch, live tracking, and controller restoration after switching
  games. The same flow supports standard MiSTer and MiSTer Multisystem² systems.
- Adds a Game Modes page containing Play Random Hack, Hack Draft, Difficulty
  Ladder, Creator Spotlight, Time Capsule, and Hall of Fame Tour. Every mode has
  a translated blue window and a hover description.
- Adds smart Excel import and two-way Google Sheets synchronization, with
  clearer Spreadsheet Settings and Google Sheets Settings screens.
- Creates a new automatic tracker and database recovery backup on every clean
  exit, outside the normal fresh-install cleanup path.
- Reworks My Tracker with crisp compact add/remove controls, multi-row removal,
  automatic Hack # renumbering, and simplified action menus.
- Hides settings and setup commands that belong to a different platform, so
  FXPAK Pro, RetroArch, and MiSTer users see only relevant controls.
- Makes optional Windows RetroArch setup faster and waits to open RetroArch
  until the user launches a game.
- Adds Streamer.bot level-event output plus translated setup guides for optional
  Twitch prediction and payout automation.
- Uses the new transparent, pink-accent MiSTer cat art throughout the app.
- Completes every new menu, button, status, popup, and setup instruction in
  English, Australian, Spanish, French, German, and Brazilian Portuguese.

## Downloads

- `SMWStreamTracker_Setup_1.1.0.exe` - complete Windows installer and repair package.
- `SMWStreamTracker_Update_1.1.0.exe` - updater for a working Windows installation.
- `SMWStreamTracker_macOS_arm64_1.1.0.dmg` - Apple Silicon drag-to-Applications installer.
- `SMWStreamTracker_macOS_x86_64_1.1.0.dmg` - Intel Mac drag-to-Applications installer.
- Matching Mac ZIP and SHA-256 files for both architectures.
- `SMWStreamTracker_Desktop_1.1.0_Source.zip` - source, tests, documentation,
  packaging definitions, screenshots, and required assets.
- `SHA256SUMS_1.1.0.txt` - SHA-256 checksums for the Windows release downloads.

Windows files are intentionally unsigned. On Windows, SmartScreen may require
**More info > Run anyway**. Mac builds are signed with the configured Developer
ID when release secrets are available; otherwise macOS users must open
**System Settings > Privacy & Security** and choose **Open Anyway** after the
first blocked launch. This Privacy & Security step is important for unsigned or
ad-hoc-signed test builds.

SMW Stream Tracker never includes or downloads a commercial Super Mario World
base ROM. Users must provide their own legally obtained clean ROM when applying
moderated patches.
