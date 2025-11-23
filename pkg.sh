#!/usr/bin/env bash
set -eux

APP_PKG=WaterSortTool
GIT_TAG=$(git describe --tags --always --dirty="-dev")
OUT_DIR=output
OS_NAME=$(uname -s)
OS_ARCH=$(uname -m)
DMG_DIR=${OUT_DIR}/dmg
DMG_VOL=${APP_PKG}-${OS_NAME}-${OS_ARCH}-${GIT_TAG}
DMG_IMG=${OUT_DIR}/${DMG_VOL}.dmg

# Clean old builds
rm -rf ${OUT_DIR}

# Build application
# source .venv/bin/activate
uv run python -m nuitka app.py

# Create dmg volume
mkdir -p ${DMG_DIR}
mv ${OUT_DIR}/${APP_PKG}.app ${DMG_DIR}
ln -s /Applications ${DMG_DIR}/Applications
hdiutil create -volname ${DMG_VOL} -srcfolder ${DMG_DIR} -ov -format UDZO ${DMG_IMG}
