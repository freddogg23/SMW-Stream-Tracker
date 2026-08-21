# SMW Stream Tracker Desktop v2.0.3

Version 2.0.3 is a Windows-only tracking and display reliability update.

## Fixes

- Adds a dedicated Streamer.bot page immediately above OBS in Settings,
  using the Stream Desk interface and the cyan/purple Streamer.bot link mark.
- Connects directly to Streamer.bot's local WebSocket server, including its
  optional password challenge. Test & Load Actions discovers enabled actions
  and lets every supported tracker event be mapped or disabled separately.
- Sends confirmed game launch, death, exit, level completion,
  RetroAchievements unlock, game-timer start/finish, completed-hack, and
  tracker-connection events in the background so game polling stays responsive.
- Replaces the generic Settings sidebar symbols with colored, DPI-safe artwork:
  a Super Nintendo console for Platform, Windows file for File Locations,
  NVMe drive for Storage, Streamer.bot links, the OBS logo, a stopwatch for
  Timers, an open book for Help, and a bell for About & Updates.
- Gives the main navigation its own full-color artwork, assigns the colored
  Super Famicom controller to Game Modes, and uses the supplied blue SMW
  Central storefront at the same visual size as the other navigation symbols.
  Its dark screenshot backdrop is removed at render time without recoloring or
  smoothing any foreground pixels; no Banzai Bill or extra lettering remains.
- Adds a reliable in-app label box to every icon-only main navigation item,
  so each colored sidebar symbol identifies itself on hover.
- Replaces all eight generic Game Modes symbols with dedicated color artwork:
  steaming Hot Potato, pixel Mario, random die, hack-draft cards, Difficulty
  Vine, creator spotlight, time-capsule clock, and Hall of Fame medal.
- Renames Difficulty Ladder to Difficulty Vine throughout the interface while
  transparently migrating the old name in any active saved session.
- Replaces the redundant Game Modes button in the new dashboard's Current Run
  card with Finish Game Timer. The action row now places Add to My Tracker on
  the left, Finish Game Timer in the middle, and Complete Hack on the far
  right. Game Modes remains available from its dedicated sidebar page.
- Makes the RetroAchievements summary in Game Library > Selected Game
  clickable. Expanding it temporarily uses the detail panel for a scrollable
  list of every achievement, including its real badge, title, requirement,
  point value, locked or unlocked state, and earned date. Clicking the heading
  again restores the normal hack details.
- Gives the Overview RetroAchievements card the same click-to-expand behavior.
  Its complete achievement list fills the Overview chart area, supports mouse
  wheel and scrollbar navigation, and restores the normal Overview cards when
  the RetroAchievements heading is clicked again.
- Stabilizes the non-atomic RA-SNES/SNI live-memory feed before it reaches any
  dashboard consumer. A temporary bad sample can no longer add a death, flash
  the current exits to zero, restore another Mario slot's counters or timers,
  or move the session timeline forward and backward.
- Confirms death state and lives changes across repeated samples while keeping
  the standard SMW death byte, lives decrement, and retry/reload fallbacks.
  Legitimate changes receive only a brief polling-cycle confirmation delay.
- Updates the app and WebSocket OBS dock immediately after a confirmed death,
  before slower progress and OBS text-file persistence work. This removes the
  avoidable delay without increasing MiSTer or emulator polling load.
- Uses the same standard SMW death rules for normal SNES and RA-SNES, with the
  death byte confirmed at both ends of the shared memory pass so a transient
  RA value cannot become an irreversible counter change.
- Waits for the destination room to stabilize after RA-SNES pipe and door
  transitions before using the retry/reload fallback, preventing ordinary
  room entries from being counted as deaths.
- Reads SMW's native pipe, door, and scripted-entrance action bytes and keeps
  the retry-only fallback disabled for the entire transition. This also covers
  pipes and doors that deliberately return to the same `$010B` room number.
- Carries the selected library game's known exit total into live tracking so
  the dashboard does not fall back to `Unknown` when an RA-compatible core or
  MiSTer reports a shortened or platform-specific ROM path.
- Preserves that known exit total across a same-ROM bridge reconnect, so a
  completed counter remains, for example, `12 / 12` instead of changing to
  `12 / Unknown` during the ending transition.
- Configures MiSTer's native RetroAchievements client to center achievement
  popups and keep descriptions on one line. These are MiSTer's supported
  settings for avoiding side cropping on 4:3 HDMI output.
- Hides the persistent RetroAchievements leaderboard tracker during a level
  while preserving MiSTer's submitted-score popup when the attempt ends.
- Existing MiSTer users should run RetroAchievements Setup once after updating
  to apply the HDMI-safe popup settings. Credentials and achievement progress
  remain unchanged.

## Windows download

- `SMWStreamTracker_Update_2.0.3.exe` - updater for an existing Windows
  installation of SMW Stream Tracker.

This is a Windows-only build. No macOS files are included because macOS has not
been tested. The updater is unsigned, so Windows may display a SmartScreen
warning.
