#!/usr/bin/env bash
APP_PKG=WaterSortTool
GIT_TAG=$(git describe --tags --always --dirty=dev)
OUT_DIR=output
OS_ARCH=$(uname -m)
DMG_DIR=${OUT_DIR}/dmg
DMG_IMG=${OUT_DIR}/${APP_PKG}-${OS_ARCH}-${GIT_TAG}.dmg

# Build application
# source .venv/bin/activate
uv run python -m nuitka app.py

# Create dmg volume
mkdir -p ${DMG_DIR}
mv ${OUT_DIR}/${APP_PKG}.app ${DMG_DIR}
hdiutil create -volname ${APP_PKG} -srcfolder ${DMG_DIR} -ov -format UDZO ${DMG_IMG}
