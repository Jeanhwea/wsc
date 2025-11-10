#!/bin/bash

# WaterSortTool 打包脚本（macOS）

APP_NAME="WaterSortTool"
VERSION=$(git describe --tags --always --dirty="-dev")

# 创建输出目录
OUTPUT_DIR="output"
mkdir -p "$OUTPUT_DIR"

# 安装必要的打包工具
echo "安装打包依赖..."
pip3 install pyinstaller
# 检查架构
echo "检测系统架构..."
ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ]; then
    ARCH_NAME="mac-arm64"
elif [ "$ARCH" = "x86_64" ]; then
    ARCH_NAME="mac-x86_64"
else
    echo "不支持的架构：$ARCH"
    exit 1
fi

# 创建打包命令
echo "正在打包应用..."
pyinstaller  --name="$APP_NAME" \
    --windowed \
    -i logo.png \
    --clean \
    --noconsole \
    --add-data="requirements.txt:." \
    --collect-all="copy" \
    --collect-all="enum" \
    --collect-all="json" \
    --collect-all="shutil" \
    --collect-all="typing" \
    --collect-all="os" \
    --collect-all="sys" \
    --distpath="$OUTPUT_DIR/dist" \
    --workpath="$OUTPUT_DIR/build" \
    app.py

# 创建DMG安装包
echo "创建DMG安装包..."
DMG_NAME="${APP_NAME}-${ARCH_NAME}-v${VERSION}.dmg"
DMG_PATH="$OUTPUT_DIR/$DMG_NAME"
APP_BUNDLE="$OUTPUT_DIR/dist/${APP_NAME}.app"

# 创建临时目录
TEMP_DIR="$OUTPUT_DIR/temp"
mkdir -p "$TEMP_DIR"

# 检查应用程序是否成功创建
if [ ! -d "$APP_BUNDLE" ]; then
    echo "错误：应用程序包未成功创建！"
    echo "请检查PyInstaller的输出，可能存在打包错误。"
    exit 1
fi

# 复制应用到临时目录
cp -R "$APP_BUNDLE" "$TEMP_DIR/"

# 创建DMG
hdiutil create -volname "$APP_NAME" \
    -srcfolder "$TEMP_DIR" \
    -ov \
    -format UDZO "$DMG_PATH"

# 清理临时文件
rm -rf "$TEMP_DIR"
echo "打包完成！"
echo "DMG文件位置：$DMG_PATH"
