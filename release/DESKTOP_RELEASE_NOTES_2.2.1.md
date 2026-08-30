# SMW Stream Tracker Desktop v2.2.1

Version 2.2.1 is a Windows-only reliability update for Music Identifier &
Radio.

## Highlights

- **Windows Volume Mixer app discovery:** Refresh Sources now reads the Apps
  section of Windows Volume Mixer across every active playback output. Apps
  routed to secondary devices—such as Chrome on a RØDECaster Music output—are
  detected without requiring that device to be the Windows default.
- **Reliable live refresh:** Every click performs a completely new scan,
  prioritizes currently active sessions, groups duplicate processes into one
  friendly application entry, and runs without freezing the interface.
- **Online-only music catalog:** Music recognition uses the shared SMW Central
  fingerprint catalog. The desktop build no longer bundles or maintains the
  full offline music index, while new and changed submissions are refreshed in
  the cloud automatically.
- **Recognition and tracking fixes:** Improves repeat song identification,
  voice-aware listening, community song result wording, and rapid consecutive
  death counting.

## Windows downloads

- `SMWStreamTracker_Setup_2.2.1.exe` — installer for a new Windows setup.
- `SMWStreamTracker_Update_2.2.1.exe` — updater for an existing installation.
- `SMWStreamTracker.exe` — portable Windows application.
- `SMWStreamTracker_Desktop_2.2.1_Source.zip` — Windows release source.
- `SHA256SUMS_2.2.1.txt` — SHA-256 checksums for every release file.

This release is Windows-only. No macOS files are included because macOS has
not been tested. The executables are unsigned, so Windows may display a
SmartScreen warning.
