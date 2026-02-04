#!/bin/bash
# SpineGuard Uninstallation Script

set -e

echo "=========================================="
echo "  SpineGuard Uninstaller"
echo "=========================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Installation directories
INSTALL_DIR="$HOME/.local/share/spineguard"
BIN_DIR="$HOME/.local/bin"
AUTOSTART_DIR="$HOME/.config/autostart"
APPS_DIR="$HOME/.local/share/applications"
ICONS_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"

echo "Removing SpineGuard..."

# Kill running instance if any
if pgrep -f "spineguard" > /dev/null; then
    echo "  Stopping running instance..."
    pkill -f "spineguard" || true
fi

# Remove files
echo "  Removing application files..."
rm -rf "$INSTALL_DIR"
rm -f "$BIN_DIR/spineguard"
rm -f "$AUTOSTART_DIR/spineguard.desktop"
rm -f "$APPS_DIR/spineguard.desktop"
rm -f "$ICONS_DIR/spineguard.svg"

# Update icon cache
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
fi

echo
echo -e "${GREEN}=========================================="
echo "  SpineGuard has been uninstalled"
echo "==========================================${NC}"
echo
