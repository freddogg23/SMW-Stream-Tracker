# SMW Stream Tracker Stream Deck plugin

This Windows-only Stream Deck plugin controls the SMW Central SPC player that
is built into SMW Stream Tracker. It connects only to the tracker's secure
localhost WebSocket and reads the existing per-user access token from
`%USERPROFILE%\SMWStreamTrackerConfig.json`.

## Controls

- Start SMW Central Radio
- Close SMW Central Radio (also stops its audio)
- Play / Pause (starts SMW Central Radio when the player is not open)
- Replay Track
- Next Track
- Toggle Looping, including an illuminated selected state
- Seek Back 10 Seconds
- Seek Forward 10 Seconds
- Volume Down
- Volume Up

Install `SMWStreamTracker-SPC-Controls.streamDeckPlugin`, then drag the desired
actions from the **SMW Stream Tracker** category onto a Stream Deck profile.
SMW Stream Tracker must be open when a key is pressed.

## Building

Run `package_streamdeck_plugin.ps1`. The script validates the Windows-only
manifest and creates the installer in `streamdeck\dist`.
