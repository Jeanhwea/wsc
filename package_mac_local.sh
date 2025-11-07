#!/usr/bin/env bash
set -euo pipefail

# ========== 基本信息 ==========
APP_NAME="WaterSortTool"
VERSION="1.3.0"
ENTRY="app.py"

# 输出目录
OUTPUT_DIR="output"
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

# ARM64 Conda 解释器
PY_ARM="/Users/a/miniconda3/envs/diff/bin/python"
# X86_64 Conda 解释器
PY_X86="/Users/a/miniforge3/envs/py311_x86/bin/python"
# 如需强制经 Rosetta 启动，也可写成：
# PY_X86="arch -x86_64 /Users/a/miniforge3/envs/py311_x86/bin/python"

# ========== 打包函数 ==========
build_one() {
  local ARCH_LABEL="$1"      # mac-arm64 / mac-x86_64
  local PY="$2"              # 解释器路径（可带 arch 前缀）
  local DIST_DIR="$OUTPUT_DIR/dist-$ARCH_LABEL"
  local BUILD_DIR="$OUTPUT_DIR/build-$ARCH_LABEL"
  local DMG_NAME="${APP_NAME}-${ARCH_LABEL}-v${VERSION}.dmg"
  local DMG_PATH="$OUTPUT_DIR/$DMG_NAME"

  echo "=============================="
  echo " 开始为 $ARCH_LABEL 打包 "
  echo " 使用解释器: $PY"
  # 打印真实二进制架构（去掉 arch 前缀后检测）
  eval "file \$(echo $PY | awk '{print \$NF}') || true"
  echo "=============================="

  # 避免旧 .spec 干扰
  rm -f "${APP_NAME}.spec" || true

  # 安装（各自环境独立）
  eval "$PY -m pip install -U pip pyinstaller"

  # 原始 PyInstaller 参数
  eval "$PY -m PyInstaller \
    --name=\"$APP_NAME\" \
    --windowed \
    --clean \
    --noconsole \
    --add-data=\"requirements.txt:.\" \
    --collect-all=\"copy\" \
    --collect-all=\"enum\" \
    --collect-all=\"json\" \
    --collect-all=\"shutil\" \
    --collect-all=\"typing\" \
    --collect-all=\"os\" \
    --collect-all=\"sys\" \
    --distpath=\"$DIST_DIR\" \
    --workpath=\"$BUILD_DIR\" \
    \"$ENTRY\""

  echo "打包完成，dist 内容："
  ls -lah "$DIST_DIR" || true

  local APP_BUNDLE="$DIST_DIR/${APP_NAME}.app"

  # 如果默认名没找到，兜底：在 dist 里找任何 .app
  if [ ! -d "$APP_BUNDLE" ]; then
    echo "未在默认位置找到 ${APP_NAME}.app，尝试自动查找 *.app ..."
    APP_BUNDLE="$(find "$DIST_DIR" -maxdepth 2 -type d -name '*.app' | head -n 1 || true)"
  fi

  if [ -z "$APP_BUNDLE" ] || [ ! -d "$APP_BUNDLE" ]; then
    echo "❌ 仍未找到 .app，请检查上面的 PyInstaller 日志与 dist 目录。"
    exit 1
  fi

  # 生成 DMG
  local TEMP_DIR="$OUTPUT_DIR/temp-$ARCH_LABEL"
  rm -rf "$TEMP_DIR" && mkdir -p "$TEMP_DIR"
  cp -R "$APP_BUNDLE" "$TEMP_DIR/"

  echo "创建 DMG：$DMG_PATH"
  hdiutil create -volname "$APP_NAME" \
    -srcfolder "$TEMP_DIR" \
    -ov -format UDZO "$DMG_PATH" >/dev/null

  rm -rf "$TEMP_DIR"
  echo "✅ 完成：$DMG_PATH"
}

# ========== 先打 ARM64 ==========
build_one "mac-arm64" "$PY_ARM"

# ========== 再打 X86_64 ==========
build_one "mac-x86_64" "$PY_X86"

# ========== 汇总 ==========
echo "🎉 全部完成，产物如下："
ls -lh "$OUTPUT_DIR"/*.dmg
