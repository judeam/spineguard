#!/bin/bash
# SpineGuard Installation Script

set -e

echo "=========================================="
echo "  SpineGuard Installer"
echo "  Back Health Pomodoro Timer"
echo "=========================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Installation directories
INSTALL_DIR="$HOME/.local/share/spineguard"
BIN_DIR="$HOME/.local/bin"
AUTOSTART_DIR="$HOME/.config/autostart"
APPS_DIR="$HOME/.local/share/applications"
ICONS_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"
ICONS_256="$HOME/.local/share/icons/hicolor/256x256/apps"
ICONS_128="$HOME/.local/share/icons/hicolor/128x128/apps"
ICONS_64="$HOME/.local/share/icons/hicolor/64x64/apps"
ICONS_48="$HOME/.local/share/icons/hicolor/48x48/apps"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Checking dependencies..."

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
        echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"
    else
        echo -e "${RED}✗${NC} Python 3.10+ required, found $PYTHON_VERSION"
        exit 1
    fi
else
    echo -e "${RED}✗${NC} Python 3 not found"
    exit 1
fi

# Check for PyGObject (GTK4)
if python3 -c "import gi; gi.require_version('Gtk', '4.0')" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} PyGObject (GTK4) found"
else
    echo -e "${RED}✗${NC} PyGObject with GTK4 not found"
    echo "  Install with: sudo apt install python3-gi gir1.2-gtk-4.0 libadwaita-1-0"
    exit 1
fi

# Check for AppIndicator3
if python3 -c "import gi; gi.require_version('AppIndicator3', '0.1')" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} AppIndicator3 found"
else
    echo -e "${YELLOW}!${NC} AppIndicator3 not found - system tray may not work"
    echo "  Install with: sudo apt install gir1.2-appindicator3-0.1"
fi

echo
echo "Installing SpineGuard..."

# Create directories
echo "  Creating directories..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"
mkdir -p "$AUTOSTART_DIR"
mkdir -p "$APPS_DIR"
mkdir -p "$ICONS_DIR"
mkdir -p "$ICONS_256"
mkdir -p "$ICONS_128"
mkdir -p "$ICONS_64"
mkdir -p "$ICONS_48"

# Copy application files
echo "  Copying application files..."
cp -r "$SCRIPT_DIR/spineguard" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/spineguard/style.css" "$INSTALL_DIR/"

# Create launcher script
echo "  Creating launcher..."
cat > "$BIN_DIR/spineguard" << 'EOF'
#!/bin/bash
# SpineGuard Launcher
INSTALL_DIR="$HOME/.local/share/spineguard"
cd "$INSTALL_DIR"
exec python3 -m spineguard.app "$@"
EOF
chmod +x "$BIN_DIR/spineguard"

# Install desktop file for app menu
echo "  Installing desktop entry..."
cp "$SCRIPT_DIR/data/spineguard.desktop" "$APPS_DIR/"

# Install autostart file
echo "  Setting up autostart..."
cat > "$AUTOSTART_DIR/spineguard.desktop" << EOF
[Desktop Entry]
Type=Application
Name=SpineGuard
Comment=Back Health Pomodoro Timer
Exec=$BIN_DIR/spineguard
Icon=spineguard
Categories=Utility;Health;
StartupNotify=false
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

# Install app icons (PNG at multiple sizes)
echo "  Installing icons..."
if [ -d "$SCRIPT_DIR/assets" ]; then
    cp "$SCRIPT_DIR/assets/icon-256.png" "$ICONS_256/spineguard.png"
    cp "$SCRIPT_DIR/assets/icon-128.png" "$ICONS_128/spineguard.png"
    cp "$SCRIPT_DIR/assets/icon-64.png"  "$ICONS_64/spineguard.png"
    cp "$SCRIPT_DIR/assets/icon-48.png"  "$ICONS_48/spineguard.png"
    cp "$SCRIPT_DIR/assets/logo.png"     "$ICONS_DIR/spineguard.png"
fi

# Install tray icon (spine + clock badge)
echo "  Installing tray icon..."
if [ -d "$SCRIPT_DIR/assets" ]; then
    cp "$SCRIPT_DIR/assets/tray-48.png" "$INSTALL_DIR/tray-icon.png"
    cp "$SCRIPT_DIR/assets/tray-24.png" "$INSTALL_DIR/tray-icon-24.png"
    cp "$SCRIPT_DIR/assets/tray-22.png" "$INSTALL_DIR/tray-icon-22.png"
fi

# Update icon cache (if available)
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
fi

# Ensure ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo
    echo -e "${YELLOW}Note:${NC} Add ~/.local/bin to your PATH by adding this to your ~/.bashrc:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

echo
echo -e "${GREEN}=========================================="
echo "  Installation Complete!"
echo "==========================================${NC}"
echo
echo "To start SpineGuard now:"
echo "  spineguard"
echo
echo "SpineGuard will automatically start on login."
echo
echo "To uninstall, run:"
echo "  $SCRIPT_DIR/uninstall.sh"
echo
