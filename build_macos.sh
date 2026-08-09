#!/bin/bash
# Build CORA.app and package it as a distributable .dmg.
#
# Usage: ./build_macos.sh [--skip-app]
#   --skip-app   package the existing dist/CORA.app instead of rebuilding it
set -euo pipefail

cd "$(dirname "$0")"

VERSION=$(python3 -c "exec(open('cora/_version.py').read()); print(__version__)")
APP="dist/CORA.app"
DMG="dist/CORA-${VERSION}.dmg"
VOLNAME="CORA ${VERSION}"
PYTHON="${PYTHON:-.venv/bin/python}"

if [ "${1:-}" != "--skip-app" ]; then
    if [ ! -x "$PYTHON" ]; then
        echo "Build environment missing. Create it with:"
        echo "  python3.11 -m venv .venv && .venv/bin/pip install -r requirements.txt pyinstaller"
        exit 1
    fi
    echo "==> Building $APP"
    "$PYTHON" -m PyInstaller cora_gui.spec --noconfirm --clean
fi

[ -d "$APP" ] || { echo "$APP not found"; exit 1; }

echo "==> Staging disk image contents"
STAGE=$(mktemp -d)
trap 'rm -rf "$STAGE"' EXIT

cp -R "$APP" "$STAGE/CORA.app"
ln -s /Applications "$STAGE/Applications"

cat > "$STAGE/README.txt" <<EOF
CORA - Coastal Risk Analyzer ${VERSION}

To install, drag CORA.app onto the Applications folder in this window.

This build is not signed with an Apple Developer ID, so macOS Gatekeeper
will block the first launch. To open it:

  1. Right-click (or Control-click) CORA.app in Applications
  2. Choose "Open"
  3. Confirm "Open" in the dialog

You only need to do this once.

Settings, downloaded DEM tiles and caches are stored in
~/Library/Application Support/CORA
EOF

echo "==> Creating $DMG"
rm -f "$DMG"
hdiutil create \
    -volname "$VOLNAME" \
    -srcfolder "$STAGE" \
    -fs HFS+ \
    -format UDZO \
    -imagekey zlib-level=9 \
    -ov \
    "$DMG"

echo
echo "Done: $DMG ($(du -h "$DMG" | cut -f1))"
