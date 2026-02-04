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

SOCKET_PATH = Path.home() / ".local" / "share" / "spineguard" / "tray.sock"


class TrayProcess:
    """Tray icon running in separate GTK3 process."""

    def __init__(self):
        self._indicator = None
        self._pause_item = None
        self._status_item = None
        self._status = {"seconds": 1500, "break_type": "walk", "paused": False}
        self._socket = None
        self._running = True

        self._setup_indicator()
        self._setup_socket()

    def _setup_indicator(self):
        """Set up the AppIndicator."""
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

        quit_item = Gtk.MenuItem(label="Quit SpineGuard")
        quit_item.connect("activate", self._on_quit)
        menu.append(quit_item)

        menu.show_all()
        self._indicator.set_menu(menu)

    def _setup_socket(self):
        """Set up socket to receive updates from main process."""
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

        break_name = "Walk" if break_type == "walk" else "Lie Down"

        if paused:
            status = f"PAUSED - {minutes}:{secs:02d} until {break_name}"
            self._pause_item.set_label("Resume")
        else:
            status = f"{minutes}:{secs:02d} until {break_name}"
            self._pause_item.set_label("Pause")

        self._status_item.set_label(status)
        self._indicator.set_title(f"SpineGuard - {status}")

    def _send_command(self, cmd):
        """Send command to main process."""
        main_socket = Path.home() / ".local" / "share" / "spineguard" / "main.sock"
        if main_socket.exists():
            try:
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
                sock.sendto(json.dumps({"command": cmd}).encode(), str(main_socket))
                sock.close()
            except Exception:
                pass

    def _on_pause(self, item):
        self._send_command("pause_toggle")

    def _on_skip(self, item):
        self._send_command("skip")

    def _on_break(self, item):
        self._send_command("take_break")

    def _on_quit(self, item):
        self._send_command("quit")
        Gtk.main_quit()

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
