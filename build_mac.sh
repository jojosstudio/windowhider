#!/bin/bash
# Build script for Window Hider macOS
# Run this on a macOS system with Python installed

echo "=========================================="
echo "Window Hider macOS Builder"
echo "=========================================="

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Error: This script must be run on macOS"
    exit 1
fi

echo ""
echo "📦 Step 1: Installing dependencies..."
pip3 install py2app pyobjc-framework-Cocoa pyobjc-framework-Quartz

echo ""
echo "🔨 Step 2: Building macOS app bundle..."
rm -rf build dist
python3 setup_mac.py py2app

echo ""
echo "📱 Step 3: Creating DMG installer..."

# Check if create-dmg is installed
if ! command -v create-dmg &> /dev/null; then
    echo "Installing create-dmg..."
    brew install create-dmg
fi

# Create DMG
create-dmg \
  --volname "Window Hider Installer" \
  --volicon "icon_mac.icns" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --app-drop-link 450 185 \
  --icon "Window Hider.app" 150 185 \
  "WindowHider-macOS.dmg" \
  "dist/Window Hider.app"

echo ""
echo "✅ Build complete!"
echo ""
echo "📁 Output files:"
echo "  - dist/Window Hider.app (App bundle)"
echo "  - WindowHider-macOS.dmg (Installer)"
echo ""
echo "=========================================="
