#!/usr/bin/env python3
"""Main SpineGuard application."""

import sys
from pathlib import Path
from typing import Optional

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")

from gi.repository import Gdk, Gio, GLib, Gtk

from .notifications import NotificationManager
from .overlay import BreakOverlay
from .sounds import SoundPlayer
from .timers import TimerManager
from .tray import TrayIcon


class SpineGuardApp(Gtk.Application):
    """Main SpineGuard application."""

    def __init__(self):
        super().__init__(
            application_id="com.spineguard.app",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )

        self._timer_manager: Optional[TimerManager] = None
        self._notification_manager: Optional[NotificationManager] = None
        self._sound_player: Optional[SoundPlayer] = None
        self._tray_icon: Optional[TrayIcon] = None
        self._current_overlay: Optional[BreakOverlay] = None

    def do_activate(self):
        """Called when the application is activated."""
        # Load CSS
        self._load_css()

        # Initialize components
        self._timer_manager = TimerManager()
        self._notification_manager = NotificationManager(self)
        self._sound_player = SoundPlayer()

        # Set up callbacks
        self._timer_manager.set_pomodoro_callback(self._on_pomodoro_complete)
        self._timer_manager.set_water_callback(self._on_water_reminder)
        self._timer_manager.set_supplement_callback(self._on_supplement_reminder)

        # Create tray icon
        self._tray_icon = TrayIcon(
            on_pause_toggle=self._on_pause_toggle,
            on_skip=self._on_skip,
            on_take_break=self._on_take_break,
            on_quit=self._on_quit,
            get_seconds_remaining=self._timer_manager.get_seconds_remaining,
            get_next_break_type=self._timer_manager.get_next_break_type,
            is_paused=self._timer_manager.is_paused,
        )

        # Start timers
        self._timer_manager.start()

        # Keep the application running (no visible window needed)
        self.hold()

    def _load_css(self):
        """Load custom CSS styling."""
        css_provider = Gtk.CssProvider()

        # Try to load from installed location first, then development location
        css_paths = [
            Path.home() / ".local" / "share" / "spineguard" / "style.css",
            Path(__file__).parent / "style.css",
        ]

        for css_path in css_paths:
            if css_path.exists():
                css_provider.load_from_path(str(css_path))
                Gtk.StyleContext.add_provider_for_display(
                    Gdk.Display.get_default(),
                    css_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
                )
                break

    def _on_pomodoro_complete(self, break_type: str):
        """Called when pomodoro timer completes - show break overlay."""
        if self._current_overlay:
            return  # Already showing a break

        # Play sound to announce break
        self._sound_player.play_break_start()

        duration = self._timer_manager.get_break_duration(break_type)

        self._current_overlay = BreakOverlay(
            break_type=break_type,
            duration_minutes=duration,
            on_complete=self._on_break_complete,
            on_skip=self._on_break_skipped,
            sound_player=self._sound_player,
        )
        self._current_overlay.present()

    def _on_break_complete(self):
        """Called when break is completed normally or early."""
        self._current_overlay = None
        self._timer_manager.break_completed()

    def _on_break_skipped(self):
        """Called when break is skipped (emergency)."""
        self._current_overlay = None
        self._timer_manager.skip_break()

    def _on_water_reminder(self):
        """Called for water reminders."""
        self._sound_player.play_water_reminder()
        self._notification_manager.show_water_reminder()

    def _on_supplement_reminder(self, morning: bool):
        """Called for supplement reminders."""
        self._sound_player.play_supplement_reminder()
        self._notification_manager.show_supplement_reminder(morning)

    def _on_pause_toggle(self):
        """Toggle pause state."""
        if self._timer_manager.is_paused():
            self._timer_manager.resume()
        else:
            self._timer_manager.pause()

    def _on_skip(self):
        """Skip the next break."""
        self._timer_manager.skip_break()

    def _on_take_break(self):
        """Take a break immediately."""
        self._timer_manager.take_break_now()

    def _on_quit(self):
        """Quit the application."""
        if self._timer_manager:
            self._timer_manager.stop()
        if self._tray_icon:
            self._tray_icon.cleanup()
        self.quit()


def main():
    """Entry point for SpineGuard."""
    app = SpineGuardApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
