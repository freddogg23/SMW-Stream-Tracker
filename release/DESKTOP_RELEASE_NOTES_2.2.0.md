# SMW Stream Tracker Desktop v2.2.0

Version 2.2.0 is a Windows-only music, Streamer.bot, and OBS radio release.

## Highlights

- Adds **Music Identifier & Radio**. It listens through a selected Windows
  audio source and matches the recording privately against the local SMW
  Central music catalog; recordings never leave the computer. Early matching
  makes good results appear sooner, Stop Listening responds immediately, and
  the index checks for new or changed music every 30 minutes while the app is
  open.
- Adds a polished in-app **SPC Player** with play/pause, replay, highlighted
  looping, next track, smooth progress seeking, volume control, collapse,
  scrolling track text, and smoother dragging. The player follows songs opened
  from the identifier, radio, and SMW Central music pages.
- Adds an **SMW Central Radio OBS Browser Source** controlled by the in-app SPC
  player. The stream widget shows the current title, artist, elapsed time,
  duration, animated equalizer, and smooth progress bar. Audio stays in the
  tracker so OBS can capture it through Desktop Audio or Application Audio
  Capture.
- Adds one-click Streamer.bot setup for the **What Song Is Playing?** Twitch
  channel-point reward. Users can choose the allowed OBS scene, reward cost,
  and cooldown; redemption replies contain the current level's song title and
  SMW Central listening link.
- Makes song redemptions faster by caching the live ROM, level, room, and music
  context. A changed level or music register creates a new result instead of
  reusing the previous level's song.
- Adds an in-app Streamer.bot installer, reuses existing rewards when present,
  and improves setup compatibility with current Streamer.bot navigation.
- Adds a dedicated **Elgato** settings page with one-click installation of the
  bundled SMW Stream Tracker Stream Deck plugin. Stream Deck buttons can
  start or close SMW Central Radio and control play/pause, replay, next track,
  looping, seeking, and volume through the tracker.
- Smooths notification dots and anti-aliases music artwork, player controls,
  scrubbers, progress indicators, and other custom-drawn Windows UI elements.
- Improves clean shutdown and tracker recovery so closing the app normally does
  not produce a false crash-recovery prompt.

## Windows downloads

- `SMWStreamTracker_Setup_2.2.0.exe` — installer for a new Windows setup.
- `SMWStreamTracker_Update_2.2.0.exe` — updater for an existing installation.
- `SMWStreamTracker.exe` — portable Windows application.
- `SMWStreamTracker_Desktop_2.2.0_Source.zip` — Windows release source.
- `SHA256SUMS_2.2.0.txt` — SHA-256 checksums for every release file.

This release is Windows-only. No macOS files are included because macOS has
not been tested. The executables are unsigned, so Windows may display a
SmartScreen warning.
