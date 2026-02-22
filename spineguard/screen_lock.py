"""Screen lock/unlock and suspend/resume detection for SpineGuard."""

from typing import Callable, Optional

from gi.repository import Gio, GLib


class ScreenLockDetector:
    """Detects screen lock/unlock and suspend/resume via D-Bus signals."""

    def __init__(
        self,
        on_lock: Callable[[], None],
        on_unlock: Callable[[], None],
    ):
        self._on_lock = on_lock
        self._on_unlock = on_unlock
        self._subscription_ids: list[tuple] = []  # (bus, sub_id)

    def start(self):
        """Subscribe to D-Bus screen lock signals."""
        # Session bus signals
        try:
            session_bus = Gio.bus_get_sync(Gio.BusType.SESSION)
            if session_bus:
                # org.freedesktop.ScreenSaver.ActiveChanged
                sub_id = session_bus.signal_subscribe(
                    None,
                    "org.freedesktop.ScreenSaver",
                    "ActiveChanged",
                    "/org/freedesktop/ScreenSaver",
                    None,
                    Gio.DBusSignalFlags.NONE,
                    self._on_screensaver_changed,
                )
                self._subscription_ids.append((session_bus, sub_id))

                # org.gnome.ScreenSaver.ActiveChanged
                sub_id = session_bus.signal_subscribe(
                    None,
                    "org.gnome.ScreenSaver",
                    "ActiveChanged",
                    "/org/gnome/ScreenSaver",
                    None,
                    Gio.DBusSignalFlags.NONE,
                    self._on_screensaver_changed,
                )
                self._subscription_ids.append((session_bus, sub_id))
        except Exception as e:
            print(f"ScreenLockDetector: session bus error: {e}")

        # System bus signals
        try:
            system_bus = Gio.bus_get_sync(Gio.BusType.SYSTEM)
            if system_bus:
                # org.freedesktop.login1.Session Lock/Unlock
                sub_id = system_bus.signal_subscribe(
                    None,
                    "org.freedesktop.login1.Session",
                    "Lock",
                    None,
                    None,
                    Gio.DBusSignalFlags.NONE,
                    self._on_session_lock,
                )
                self._subscription_ids.append((system_bus, sub_id))

                sub_id = system_bus.signal_subscribe(
                    None,
                    "org.freedesktop.login1.Session",
                    "Unlock",
                    None,
                    None,
                    Gio.DBusSignalFlags.NONE,
                    self._on_session_unlock,
                )
                self._subscription_ids.append((system_bus, sub_id))

                # org.freedesktop.login1.Manager PrepareForSleep
                sub_id = system_bus.signal_subscribe(
                    None,
                    "org.freedesktop.login1.Manager",
                    "PrepareForSleep",
                    "/org/freedesktop/login1",
                    None,
                    Gio.DBusSignalFlags.NONE,
                    self._on_prepare_for_sleep,
                )
                self._subscription_ids.append((system_bus, sub_id))
        except Exception as e:
            print(f"ScreenLockDetector: system bus error: {e}")

    def stop(self):
        """Unsubscribe from all D-Bus signals."""
        for bus, sub_id in self._subscription_ids:
            try:
                bus.signal_unsubscribe(sub_id)
            except Exception:
                pass
        self._subscription_ids.clear()

    def _on_screensaver_changed(self, connection, sender, path, interface, signal, params):
        """Handle ScreenSaver ActiveChanged signal."""
        active = params.unpack()[0]
        if active:
            self._on_lock()
        else:
            self._on_unlock()

    def _on_session_lock(self, connection, sender, path, interface, signal, params):
        """Handle login1 Session Lock signal."""
        self._on_lock()

    def _on_session_unlock(self, connection, sender, path, interface, signal, params):
        """Handle login1 Session Unlock signal."""
        self._on_unlock()

    def _on_prepare_for_sleep(self, connection, sender, path, interface, signal, params):
        """Handle PrepareForSleep signal (suspend/resume)."""
        going_to_sleep = params.unpack()[0]
        if going_to_sleep:
            self._on_lock()
        else:
            self._on_unlock()
