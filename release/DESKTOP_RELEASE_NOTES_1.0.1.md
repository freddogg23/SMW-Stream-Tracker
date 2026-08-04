# SMW Stream Tracker Desktop v1.0.1

This maintenance release repairs update checks for existing installations and
makes version information and updates easier to find inside the app.

## Changes

- Automatically migrates the retired `freddogg23/smwc_tracker` update-manifest
  address to the public `freddogg23/SMW-Stream-Tracker` repository.
- Replaces the separate **File → Check for Updates** command with
  **File → About & Updates**.
- Shows the installed version and build date prominently in the About & Updates
  window.
- Keeps the **Check for Updates** button in that window beside the website,
  documentation, privacy, and close controls.
- Publishes the complete source tree and multilingual documentation on the
  repository `main` branch.
- Expands the Australian setup guide with a more playful Australian voice.

## Important update note

The public `1.0.0` executables were not digitally signed. They can discover
this release after the manifest repair, but the app's security checks will not
launch a downloaded updater from an unsigned installation. Existing users must
run the complete `1.0.1` installer once. Fully automatic in-app installation
requires the application and updater to be signed by the same trusted Windows
publisher.

## Downloads

- `SMWStreamTracker_Setup_1.0.1.exe` — complete first-time installer.
- `SMWStreamTracker_Update_1.0.1.exe` — updater for an existing installation.
- `SMWStreamTracker_Desktop_1.0.1_Source.zip` — complete source, installer
  definitions, documentation, and required assets.

SMW Stream Tracker never includes or downloads a commercial Super Mario World
base ROM. Users must provide their own legally obtained clean ROM when applying
moderated patches.
