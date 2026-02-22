"""Idle detection for SpineGuard.

Detects user inactivity via X11 (XScreenSaver extension) or
Wayland/GNOME (Mutter IdleMonitor D-Bus interface).
"""

import ctypes
import ctypes.util
from typing import Callable, Optional

from gi.repository import Gio, GLib

from .config import Config


class _X11IdleBackend:
    """X11 idle detection using XScreenSaver extension via ctypes."""

    def __init__(self):
        self._available = False
        self._dpy = None
        self._xss = None
        self._info = None

        try:
            x11_path = ctypes.util.find_library("X11")
            xss_path = ctypes.util.find_library("Xss")
            if not x11_path or not xss_path:
                return

            self._x11 = ctypes.cdll.LoadLibrary(x11_path)
            self._xss = ctypes.cdll.LoadLibrary(xss_path)

            self._x11.XOpenDisplay.restype = ctypes.c_void_p
            self._x11.XOpenDisplay.argtypes = [ctypes.c_char_p]

            self._dpy = self._x11.XOpenDisplay(None)
            if not self._dpy:
                return

            # XScreenSaverInfo struct
            class XScreenSaverInfo(ctypes.Structure):
                _fields_ = [
                    ("window", ctypes.c_ulong),
                    ("state", ctypes.c_int),
                    ("kind", ctypes.c_int),
                    ("til_or_since", ctypes.c_ulong),
                    ("idle", ctypes.c_ulong),
                    ("eventMask", ctypes.c_ulong),
                ]

            self._xss.XScreenSaverAllocInfo.restype = ctypes.POINTER(XScreenSaverInfo)
            self._xss.XScreenSaverQueryInfo.argtypes = [
                ctypes.c_void_p,
                ctypes.c_ulong,
                ctypes.POINTER(XScreenSaverInfo),
            ]
            self._xss.XScreenSaverQueryInfo.restype = ctypes.c_int

            self._x11.XDefaultRootWindow.argtypes = [ctypes.c_void_p]
            self._x11.XDefaultRootWindow.restype = ctypes.c_ulong

            self._info = self._xss.XScreenSaverAllocInfo()
            self._available = True
        except (OSError, AttributeError):
            pass

    @property
    def available(self) -> bool:
        return self._available

    def get_idle_ms(self) -> int:
        """Get idle time in milliseconds."""
        if not self._available:
            return 0
        try:
            root = self._x11.XDefaultRootWindow(self._dpy)
            self._xss.XScreenSaverQueryInfo(self._dpy, root, self._info)
            return self._info.contents.idle
        except Exception:
            return 0


class _WaylandIdleBackend:
    """GNOME/Wayland idle detection using Mutter IdleMonitor D-Bus."""

    def __init__(self):
        self._available = False
        self._proxy = None

        try:
            self._proxy = Gio.DBusProxy.new_for_bus_sync(
                Gio.BusType.SESSION,
                Gio.DBusProxyFlags.NONE,
                None,
                "org.gnome.Mutter.IdleMonitor",
                "/org/gnome/Mutter/IdleMonitor/Core",
                "org.gnome.Mutter.IdleMonitor",
                None,
            )
            # Test the call
            result = self._proxy.call_sync(
                "GetIdletime",
                None,
                Gio.DBusCallFlags.NONE,
                1000,
                None,
            )
            self._available = True
        except Exception:
            pass

    @property
    def available(self) -> bool:
        return self._available

    def get_idle_ms(self) -> int:
        """Get idle time in milliseconds."""
        if not self._available:
            return 0
        try:
            result = self._proxy.call_sync(
                "GetIdletime",
                None,
                Gio.DBusCallFlags.NONE,
                1000,
                None,
            )
            return result.unpack()[0]
        except Exception:
            return 0


class IdleDetector:
    """Detects user idle state and fires callbacks on transitions."""

    def __init__(
        self,
        config: Config,
        on_idle: Callable[[], None],
        on_active: Callable[[], None],
    ):
        self._config = config
        self._on_idle = on_idle
        self._on_active = on_active
        self._is_idle = False
        self._poll_id: Optional[int] = None
        self._backend: Optional[object] = None

        # Try X11 first, then Wayland/GNOME
        x11 = _X11IdleBackend()
        if x11.available:
            self._backend = x11
        else:
            wayland = _WaylandIdleBackend()
            if wayland.available:
                self._backend = wayland

        if not self._backend:
            print("IdleDetector: no idle detection backend available")

    def start(self):
        """Start polling for idle state."""
        if not self._backend:
            return
        if not self._config.get("idle_detection_enabled"):
            return
        self._poll_id = GLib.timeout_add_seconds(10, self._poll)

    def stop(self):
        """Stop polling."""
        if self._poll_id:
            GLib.source_remove(self._poll_id)
            self._poll_id = None

    def _poll(self) -> bool:
        """Check idle state every 10 seconds."""
        if not self._config.get("idle_detection_enabled"):
            return True

        idle_ms = self._backend.get_idle_ms()
        threshold_ms = self._config.get("idle_threshold_minutes") * 60 * 1000

        if idle_ms >= threshold_ms and not self._is_idle:
            self._is_idle = True
            self._on_idle()
        elif idle_ms < threshold_ms and self._is_idle:
            self._is_idle = False
            self._on_active()

        return True
