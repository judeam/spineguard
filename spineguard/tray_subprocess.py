#!/usr/bin/env python3
"""Standalone tray icon process for SpineGuard.

This runs as a separate process to avoid GTK3/GTK4 conflicts.
Communicates with main app via a simple socket protocol.
"""

import json
import os
import socket
import sys
import threading
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")

# Try AppIndicator3 first, fall back to AyatanaAppIndicator3
try:
    gi.require_version("AppIndicator3", "0.1")
    from gi.repository import AppIndicator3
    INDICATOR_TYPE = "AppIndicator3"
except (ValueError, ImportError):
    try:
        gi.require_version("AyatanaAppIndicator3", "0.1")
        from gi.repository import AyatanaAppIndicator3 as AppIndicator3
        INDICATOR_TYPE = "AyatanaAppIndicator3"
    except (ValueError, ImportError):
        print("No AppIndicator library found", file=sys.stderr)
        sys.exit(1)

from gi.repository import GLib, Gtk

# Keybinder is X11-only; silently unavailable on Wayland
try:
    gi.require_version("Keybinder", "3.0")
    from gi.repository import Keybinder
    HAS_KEYBINDER = True
except (ValueError, ImportError):
    HAS_KEYBINDER = False

_runtime_dir = os.environ.get("XDG_RUNTIME_DIR", str(Path.home() / ".local" / "share"))
SOCKET_DIR = Path(_runtime_dir) / "spineguard"
SOCKET_PATH = SOCKET_DIR / "tray.sock"
CONFIG_FILE = Path.home() / ".config" / "spineguard" / "config.json"


def _find_tray_icon() -> Path:
    """Locate the tray icon across install methods."""
    candidates = [
        Path.home() / ".local" / "share" / "spineguard" / "tray-icon.png",  # install.sh
        Path("/usr/share/spineguard/tray-icon.png"),  # system package
        Path(__file__).parent.parent / "assets" / "tray-48.png",  # development
    ]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]


TRAY_ICON = _find_tray_icon()


class TrayProcess:
    """Tray icon running in separate GTK3 process."""

    def __init__(self):
        self._indicator = None
        self._pause_item = None
        self._status_item = None
        self._mode_item = None
        self._position_item = None
        self._status = {
            "seconds": 1500, "break_type": "walk", "paused": False,
            "mode": "recovery", "position_seconds": 0, "current_position": "sitting",
        }
        self._socket = None
        self._running = True

        self._setup_indicator()
        self._setup_socket()
        self._setup_keybindings()

    def _setup_indicator(self):
        """Set up the AppIndicator."""
        # Use custom tray icon if installed, fall back to system icon
        if TRAY_ICON.exists():
            self._indicator = AppIndicator3.Indicator.new(
                "spineguard",
                str(TRAY_ICON),
                AppIndicator3.IndicatorCategory.APPLICATION_STATUS,
            )
            self._indicator.set_icon_theme_path(str(TRAY_ICON.parent))
        else:
            self._indicator = AppIndicator3.Indicator.new(
                "spineguard",
                "appointment-soon",
                AppIndicator3.IndicatorCategory.APPLICATION_STATUS,
            )
        self._indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        menu = Gtk.Menu()

        self._status_item = Gtk.MenuItem(label="Starting...")
        self._status_item.set_sensitive(False)
        menu.append(self._status_item)

        menu.append(Gtk.SeparatorMenuItem())

        self._pause_item = Gtk.MenuItem(label="Pause")
        self._pause_item.connect("activate", self._on_pause)
        menu.append(self._pause_item)

        skip_item = Gtk.MenuItem(label="Skip Next Break")
        skip_item.connect("activate", self._on_skip)
        menu.append(skip_item)

        break_item = Gtk.MenuItem(label="Take Break Now")
        break_item.connect("activate", self._on_break)
        menu.append(break_item)

        menu.append(Gtk.SeparatorMenuItem())

        self._mode_item = Gtk.MenuItem(label="Mode: Standard")
        self._mode_item.connect("activate", self._on_toggle_mode)
        menu.append(self._mode_item)

        self._position_item = Gtk.MenuItem(label="")
        self._position_item.set_sensitive(False)
        menu.append(self._position_item)

        menu.append(Gtk.SeparatorMenuItem())

        stats_item = Gtk.MenuItem(label="Statistics...")
        stats_item.connect("activate", self._on_stats)
        menu.append(stats_item)

        settings_item = Gtk.MenuItem(label="Settings...")
        settings_item.connect("activate", self._on_settings)
        menu.append(settings_item)

        menu.append(Gtk.SeparatorMenuItem())

        quit_item = Gtk.MenuItem(label="Quit SpineGuard")
        quit_item.connect("activate", self._on_quit)
        menu.append(quit_item)

        menu.show_all()
        self._indicator.set_menu(menu)

    def _setup_socket(self):
        """Set up socket to receive updates from main process."""
        SOCKET_DIR.mkdir(parents=True, exist_ok=True)
        if SOCKET_PATH.exists():
            SOCKET_PATH.unlink()

        self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self._socket.bind(str(SOCKET_PATH))
        self._socket.setblocking(False)

        GLib.io_add_watch(
            self._socket.fileno(),
            GLib.IO_IN,
            self._on_socket_data,
        )

    def _on_socket_data(self, fd, condition):
        """Handle incoming socket data."""
        try:
            data = self._socket.recv(1024)
            msg = json.loads(data.decode())

            if "seconds" in msg:
                self._status = msg
                self._update_display()
            elif "command" in msg:
                if msg["command"] == "quit":
                    Gtk.main_quit()

        except (BlockingIOError, json.JSONDecodeError):
            pass

        return True

    def _update_display(self):
        """Update the tray display."""
        seconds = self._status.get("seconds", 0)
        minutes = seconds // 60
        secs = seconds % 60
        break_type = self._status.get("break_type", "walk")
        paused = self._status.get("paused", False)
        mode = self._status.get("mode", "recovery")

        break_name = "Walk" if break_type == "walk" else "Lie Down"

        if paused:
            status = f"PAUSED - {minutes}:{secs:02d} until {break_name}"
            self._pause_item.set_label("Resume")
        else:
            status = f"{minutes}:{secs:02d} until {break_name}"
            self._pause_item.set_label("Pause")

        self._status_item.set_label(status)
        self._indicator.set_title(f"SpineGuard - {status}")

        # Update mode item
        if mode == "sit_stand":
            self._mode_item.set_label("Mode: Sit-Stand (click to switch)")
            # Show position countdown
            pos_seconds = self._status.get("position_seconds", 0)
            current_pos = self._status.get("current_position", "sitting")
            pos_name = "Standing" if current_pos == "standing" else "Sitting"
            if pos_seconds > 0:
                pm = pos_seconds // 60
                ps = pos_seconds % 60
                self._position_item.set_label(f"{pos_name} - switch in {pm}:{ps:02d}")
            else:
                self._position_item.set_label(f"{pos_name}")
            self._position_item.show()
        else:
            self._mode_item.set_label("Mode: Standard (click to switch)")
            self._position_item.hide()

    def _send_command(self, cmd):
        """Send command to main process."""
        main_socket = SOCKET_DIR / "main.sock"
        if main_socket.exists():
            try:
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
                sock.sendto(json.dumps({"command": cmd}).encode(), str(main_socket))
                sock.close()
            except Exception:
                pass

    def _on_toggle_mode(self, item):
        self._send_command("toggle_mode")

    def _on_pause(self, item):
        self._send_command("pause_toggle")

    def _on_skip(self, item):
        self._send_command("skip")

    def _on_break(self, item):
        self._send_command("take_break")

    def _on_stats(self, item):
        self._send_command("show_stats")

    def _on_settings(self, item):
        self._send_command("show_settings")

    def _on_quit(self, item):
        self._send_command("quit")
        Gtk.main_quit()

    def _setup_keybindings(self):
        """Set up global keyboard shortcuts via Keybinder (X11 only)."""
        if not HAS_KEYBINDER:
            return

        try:
            Keybinder.init()
        except Exception:
            return

        # Read config directly (subprocess has no Config object)
        config = {}
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

        pause_key = config.get("hotkey_pause", "ctrl+shift+p")
        break_key = config.get("hotkey_break", "ctrl+shift+b")

        pause_accel = self._to_gtk_accelerator(pause_key)
        break_accel = self._to_gtk_accelerator(break_key)

        try:
            Keybinder.bind(pause_accel, lambda _: self._send_command("pause_toggle"))
        except Exception:
            pass
        try:
            Keybinder.bind(break_accel, lambda _: self._send_command("take_break"))
        except Exception:
            pass

    @staticmethod
    def _to_gtk_accelerator(hotkey: str) -> str:
        """Convert 'ctrl+shift+p' format to '<Primary><Shift>p' GTK accelerator format."""
        parts = hotkey.lower().split("+")
        accel = ""
        key = parts[-1] if parts else ""
        for part in parts[:-1]:
            if part in ("ctrl", "control"):
                accel += "<Primary>"
            elif part == "shift":
                accel += "<Shift>"
            elif part == "alt":
                accel += "<Alt>"
            elif part == "super":
                accel += "<Super>"
        return accel + key

    def run(self):
        """Run the GTK main loop."""
        Gtk.main()

    def cleanup(self):
        """Clean up resources."""
        if self._socket:
            self._socket.close()
        if SOCKET_PATH.exists():
            SOCKET_PATH.unlink()


def main():
    tray = TrayProcess()
    try:
        tray.run()
    finally:
        tray.cleanup()


if __name__ == "__main__":
    main()
