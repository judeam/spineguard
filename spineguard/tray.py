"""System tray management for SpineGuard.

Uses a subprocess running GTK3 for the tray icon to avoid
conflicts with the main GTK4 application.
"""

import json
import os
import socket
import subprocess
import sys
from pathlib import Path
from typing import Callable, Optional

from gi.repository import GLib

from .config import Config
from .timers import BreakType

_runtime_dir = os.environ.get("XDG_RUNTIME_DIR", str(Path.home() / ".local" / "share"))
SOCKET_DIR = Path(_runtime_dir) / "spineguard"
TRAY_SOCKET = SOCKET_DIR / "tray.sock"
MAIN_SOCKET = SOCKET_DIR / "main.sock"


class TrayIcon:
    """Manages system tray icon via subprocess."""

    def __init__(
        self,
        on_pause_toggle: Callable[[], None],
        on_skip: Callable[[], None],
        on_take_break: Callable[[], None],
        on_quit: Callable[[], None],
        get_seconds_remaining: Callable[[], int],
        get_next_break_type: Callable[[], str],
        is_paused: Callable[[], bool],
        config: Optional[Config] = None,
        get_position_seconds: Optional[Callable[[], int]] = None,
        get_current_position: Optional[Callable[[], str]] = None,
        *,
        on_show_settings: Optional[Callable[[], None]] = None,
        on_show_stats: Optional[Callable[[], None]] = None,
    ):
        self._on_pause_toggle = on_pause_toggle
        self._on_skip = on_skip
        self._on_take_break = on_take_break
        self._on_quit = on_quit
        self._get_seconds_remaining = get_seconds_remaining
        self._get_next_break_type = get_next_break_type
        self._is_paused = is_paused
        self._config = config
        self._get_position_seconds = get_position_seconds
        self._get_current_position = get_current_position
        self._on_show_settings = on_show_settings
        self._on_show_stats = on_show_stats

        self._tray_process: Optional[subprocess.Popen] = None
        self._socket: Optional[socket.socket] = None
        self._update_timer_id: Optional[int] = None
        self._available = False
        self._get_water_seconds: Optional[Callable[[], int]] = None

        self._setup_main_socket()
        self._start_tray_subprocess()

        if self._available:
            self._start_updates()

    def _setup_main_socket(self):
        """Set up socket to receive commands from tray subprocess."""
        SOCKET_DIR.mkdir(parents=True, exist_ok=True)

        if MAIN_SOCKET.exists():
            MAIN_SOCKET.unlink()

        self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self._socket.bind(str(MAIN_SOCKET))
        self._socket.setblocking(False)

        GLib.io_add_watch(
            self._socket.fileno(),
            GLib.IO_IN,
            self._on_command,
        )

    def _start_tray_subprocess(self):
        """Start the tray icon subprocess."""
        # Find the tray subprocess script
        script_dir = Path(__file__).parent
        tray_script = script_dir / "tray_subprocess.py"

        if not tray_script.exists():
            # Try installed location
            tray_script = SOCKET_DIR / "spineguard" / "tray_subprocess.py"

        if not tray_script.exists():
            print("Tray subprocess script not found - tray disabled")
            return

        try:
            self._tray_process = subprocess.Popen(
                [sys.executable, str(tray_script)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self._available = True
            print("SpineGuard tray icon started")
        except Exception as e:
            print(f"Failed to start tray subprocess: {e}")

    def _on_command(self, fd, condition):
        """Handle commands from tray subprocess."""
        try:
            data = self._socket.recv(1024)
            msg = json.loads(data.decode())
            cmd = msg.get("command")

            if cmd == "pause_toggle":
                self._on_pause_toggle()
            elif cmd == "skip":
                self._on_skip()
            elif cmd == "take_break":
                self._on_take_break()
            elif cmd == "toggle_mode":
                if self._config:
                    new_mode = "recovery" if self._config.is_sit_stand else "sit_stand"
                    self._config.set("mode", new_mode)
            elif cmd == "show_settings":
                if self._on_show_settings:
                    self._on_show_settings()
            elif cmd == "show_stats":
                if self._on_show_stats:
                    self._on_show_stats()
            elif cmd == "quit":
                self._on_quit()

        except (BlockingIOError, json.JSONDecodeError):
            pass

        return True

    def _start_updates(self):
        """Start periodic updates to tray subprocess."""
        self._update_timer_id = GLib.timeout_add_seconds(1, self._send_update)
        self._send_update()

    def _send_update(self) -> bool:
        """Send status update to tray subprocess."""
        if not self._available or not TRAY_SOCKET.exists():
            return True

        try:
            seconds = self._get_seconds_remaining()
            break_type = self._get_next_break_type()
            paused = self._is_paused()

            msg = {
                "seconds": seconds,
                "break_type": break_type,
                "paused": paused,
                "mode": self._config.mode if self._config else "recovery",
                "position_seconds": self._get_position_seconds() if self._get_position_seconds else 0,
                "current_position": self._get_current_position() if self._get_current_position else "sitting",
            }

            sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            sock.sendto(json.dumps(msg).encode(), str(TRAY_SOCKET))
            sock.close()

        except Exception:
            pass

        return True

    def is_available(self) -> bool:
        """Check if tray icon is available."""
        return self._available

    def cleanup(self):
        """Clean up resources."""
        if self._update_timer_id:
            GLib.source_remove(self._update_timer_id)
            self._update_timer_id = None

        # Send quit to tray subprocess
        if self._available and TRAY_SOCKET.exists():
            try:
                sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
                sock.sendto(json.dumps({"command": "quit"}).encode(), str(TRAY_SOCKET))
                sock.close()
            except Exception:
                pass

        if self._tray_process:
            self._tray_process.terminate()
            self._tray_process.wait(timeout=2)
            self._tray_process = None

        if self._socket:
            self._socket.close()
            self._socket = None

        if MAIN_SOCKET.exists():
            MAIN_SOCKET.unlink()
