# SMW Stream Tracker Desktop v2.1.0

Version 2.1.0 is a Windows-only library, MiSTer, RetroAchievements, and
automation release.

## Highlights

- Adds a dedicated **SNES ROMs** Game Library tab. Import one ROM or a whole
  folder, clean common dump/region/date suffixes from displayed names, use the
  same search and filters as SMW hacks, select one or all entries, and send
  selected games through the existing MiSTer SD-card workflow.
- Extends **RetroAchievements** recognition to imported SNES games. Supported
  games receive trophy markers and the same expandable official badges,
  requirements, points, lock state, and earned dates available to SMW hacks.
- Tracks newly moderated and newly waiting SMW Central hacks since the last
  refresh, records the date, and adds notification dots to Game Library and
  the appropriate refresh/download actions.
- Adds multiple named MiSTer profiles and can automatically switch to the
  console that is online. Ethernet and Wi-Fi addresses are discovered and
  tested while manual profile selection remains available.
- Speeds up bulk MiSTer ROM transfers with on-device hashes, verified atomic
  uploads, and fewer round trips. **Find & Set Up MiSTer** now also installs
  the corrected virtual save-state slots 5–11.
- Lets Streamer.bot send approved controls back to the tracker, including
  action and chat-input handling, suggested mappings, and feedback-loop
  protection, while retaining all existing outbound tracker events.
- Adds automatic crash recovery, backups, SMW Central refresh, library
  maintenance, post-stream summaries, completion detection, and statistic
  reconciliation.
- Adapts live polling to observed connection quality so counters stay
  responsive without placing unnecessary load on slower systems.
- Adds **Always Ask to Confirm Final Exit** under Platform settings. A
  completion prompt is offered only when the final exit and completion state
  agree, and the user remains in control of the final confirmation.
- Hides SMW-only creator and exit fields for ordinary SNES games while keeping
  the game name, deaths, game timer, and level timer available.
- Rejects suspicious death readings that coincide with doors, pipes, level
  transitions, loading screens, or save-state restoration, including
  RA-SNES/SNI sessions.
- Fits MiSTer and RetroArch setup plus Tracker Automation onto compact,
  single-page Platform layouts and updates the remaining profile and hack
  detail dialogs to the current interface.

## Windows downloads

- `SMWStreamTracker_Setup_2.1.0.exe` — installer for a new Windows setup.
- `SMWStreamTracker_Update_2.1.0.exe` — updater for an existing installation.
- `SMWStreamTracker.exe` — portable Windows application.
- `SMWStreamTracker_Desktop_2.1.0_Source.zip` — Windows release source.
- `SHA256SUMS_2.1.0.txt` — SHA-256 checksums for every release file.

This release is Windows-only. No macOS files are included because macOS has
not been tested. The executables are unsigned, so Windows may display a
SmartScreen warning.
