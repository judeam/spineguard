#!/bin/bash
# SpineGuard Installation Script

set -e

echo "=========================================="
echo "  SpineGuard Installer"
echo "  L5-S1 Recovery Pomodoro Timer"
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
Comment=L5-S1 Recovery Pomodoro Timer
Exec=$BIN_DIR/spineguard
Icon=spineguard
Categories=Utility;Health;
StartupNotify=false
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

# Create simple SVG icon
echo "  Installing icon..."
cat > "$ICONS_DIR/spineguard.svg" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#3a7ca5"/>
      <stop offset="100%" style="stop-color:#1a4a6a"/>
    </linearGradient>
  </defs>
  <circle cx="32" cy="32" r="30" fill="url(#bg)"/>
  <path d="M32 8 L32 32 L48 32" stroke="#7ec8a3" stroke-width="4" fill="none" stroke-linecap="round"/>
  <circle cx="32" cy="32" r="4" fill="#7ec8a3"/>
  <text x="32" y="54" text-anchor="middle" fill="#e8f4f8" font-size="8" font-family="sans-serif">SPINE</text>
</svg>
EOF

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
