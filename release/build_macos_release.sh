#!/bin/bash
set -euo pipefail

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "This build must run on macOS."
  exit 2
fi

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

VERSION="${1:-}"
if [[ -z "$VERSION" ]]; then
  VERSION="$(sed -n 's/^APP_VERSION = "\([^"]*\)"/\1/p' SMWStreamTracker_MARIO_UI_STATS_CHARTS_MARIO_TIGHTER.py | head -n 1)"
fi
if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Version must use the form 1.2.3."
  exit 3
fi

ARCHITECTURE="$(uname -m)"
APP_PATH="$PROJECT_DIR/dist/SMW Stream Tracker.app"
ZIP_PATH="$PROJECT_DIR/dist/SMWStreamTracker_macOS_${ARCHITECTURE}_${VERSION}.zip"
DMG_PATH="$PROJECT_DIR/dist/SMWStreamTracker_macOS_${ARCHITECTURE}_${VERSION}.dmg"
CHECKSUM_PATH="$PROJECT_DIR/dist/SHA256SUMS_macOS_${ARCHITECTURE}_${VERSION}.txt"

python3 -c "import paramiko" || {
  echo "Paramiko is required for MiSTer support. Install release/requirements-macos.txt first."
  exit 4
}

python3 -m PyInstaller --noconfirm --clean SMWStreamTracker-macOS.spec
if [[ ! -d "$APP_PATH" ]]; then
  echo "PyInstaller did not create the Mac app bundle."
  exit 5
fi

SIGN_IDENTITY="${MACOS_CODESIGN_IDENTITY:--}"
if [[ "$SIGN_IDENTITY" == "-" ]]; then
  codesign --force --deep --sign - "$APP_PATH"
else
  codesign --force --deep --options runtime --sign "$SIGN_IDENTITY" "$APP_PATH"
fi
codesign --verify --deep --strict --verbose=2 "$APP_PATH"

"$APP_PATH/Contents/MacOS/SMWStreamTracker" --startup-check
"$APP_PATH/Contents/MacOS/SMWStreamTracker" --network-check

ditto -c -k --sequesterRsrc --keepParent "$APP_PATH" "$ZIP_PATH"

DMG_STAGE="$(mktemp -d)"
cleanup_stage() {
  rm -rf "$DMG_STAGE"
}
trap cleanup_stage EXIT
ditto "$APP_PATH" "$DMG_STAGE/SMW Stream Tracker.app"
ln -s /Applications "$DMG_STAGE/Applications"
hdiutil create \
  -volname "SMW Stream Tracker $VERSION" \
  -srcfolder "$DMG_STAGE" \
  -ov \
  -format UDZO \
  "$DMG_PATH"

if [[ -n "${APPLE_ID:-}" && -n "${APPLE_TEAM_ID:-}" && -n "${APPLE_APP_PASSWORD:-}" ]]; then
  xcrun notarytool submit "$DMG_PATH" \
    --apple-id "$APPLE_ID" \
    --team-id "$APPLE_TEAM_ID" \
    --password "$APPLE_APP_PASSWORD" \
    --wait
  xcrun stapler staple "$DMG_PATH"
fi

(
  cd "$PROJECT_DIR/dist"
  shasum -a 256 "$(basename "$ZIP_PATH")" "$(basename "$DMG_PATH")" > "$(basename "$CHECKSUM_PATH")"
)

echo "Mac release created:"
echo "$DMG_PATH"
echo "$ZIP_PATH"
echo "$CHECKSUM_PATH"
