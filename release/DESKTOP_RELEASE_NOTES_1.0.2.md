# SMW Stream Tracker Desktop v1.0.2

This is the first SMW Stream Tracker release signed through Microsoft Artifact
Signing. Windows can verify that the application, installer, and updater were
published by FredDOGG23 and were not modified after signing.

## Changes

- Digitally signs `SMWStreamTracker.exe`, the complete installer, and the
  updater with the same publicly trusted publisher identity.
- Uses Microsoft's Artifact Signing timestamp service so release signatures
  remain valid after the short-lived signing certificate rotates.
- Establishes the trusted publisher baseline used to validate future automatic
  updates.
- Updates the application and multilingual setup documentation to version
  1.0.2.

## Important update note

Existing 1.0.0 and 1.0.1 installations were distributed without a trusted
publisher signature. Install the complete 1.0.2 installer manually once. After
that transition, the application can validate future updaters against the same
trusted Windows publisher.

## Downloads

- `SMWStreamTracker_Setup_1.0.2.exe` - complete first-time installer and the
  required transition from an unsigned installation.
- `SMWStreamTracker_Update_1.0.2.exe` - updater for an existing installation.
- `SMWStreamTracker_Desktop_1.0.2_Source.zip` - complete source, installer
  definitions, documentation, and required assets.

SMW Stream Tracker never includes or downloads a commercial Super Mario World
base ROM. Users must provide their own legally obtained clean ROM when applying
moderated patches.
