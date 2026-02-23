#!/usr/bin/env python3
"""Main SpineGuard application."""

import sys
from pathlib import Path
from typing import Optional

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")

from gi.repository import Gdk, Gio, GLib, Gtk

from .config import Config
from .idle import IdleDetector
from .notifications import NotificationManager
from .overlay import BlockingOverlay, BreakOverlay
from .screen_lock import ScreenLockDetector
from .settings import SettingsDialog
from .sounds import SoundPlayer
from .stats import StatsManager, StatsWindow
from .timers import BreakType, TimerManager
from .tray import TrayIcon
from .micro_overlay import MicroBreakOverlay
from .routines import RoutineProgress


class SpineGuardApp(Gtk.Application):
    """Main SpineGuard application."""

    def __init__(self):
        super().__init__(
            application_id="com.spineguard.app",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )

        self._config: Optional[Config] = None
        self._timer_manager: Optional[TimerManager] = None
        self._notification_manager: Optional[NotificationManager] = None
        self._sound_player: Optional[SoundPlayer] = None
        self._tray_icon: Optional[TrayIcon] = None
        self._stats_manager: Optional[StatsManager] = None
        self._screen_lock_detector: Optional[ScreenLockDetector] = None
        self._idle_detector: Optional[IdleDetector] = None

        self._current_overlay: Optional[BreakOverlay] = None
        self._blocking_overlays: list[BlockingOverlay] = []
        self._current_break_type: Optional[str] = None

        # Independent auto-pause flags
        self._lock_auto_paused: bool = False
        self._idle_auto_paused: bool = False

        # Singleton windows
        self._settings_window: Optional[SettingsDialog] = None
        self._stats_window: Optional[StatsWindow] = None
        self._routine_progress: Optional[RoutineProgress] = None
        self._current_micro_overlay: Optional[MicroBreakOverlay] = None

    def do_activate(self):
        """Called when the application is activated."""
        # Load CSS
        self._load_css()

        # Initialize components
        self._config = Config()
        self._timer_manager = TimerManager(self._config)
        self._notification_manager = NotificationManager(self)
        self._sound_player = SoundPlayer(config=self._config)
        self._stats_manager = StatsManager()
        self._routine_progress = RoutineProgress()

        # Set up timer callbacks
        self._timer_manager.set_pomodoro_callback(self._on_pomodoro_complete)
        self._timer_manager.set_water_callback(self._on_water_reminder)
        self._timer_manager.set_supplement_callback(self._on_supplement_reminder)
        self._timer_manager.set_position_callback(self._on_position_switch)
        self._timer_manager.set_physio_callback(self._on_physio_reminder)
        self._timer_manager.set_pre_break_warning_callback(self._on_pre_break_warning)
        self._timer_manager.set_breathing_callback(self._on_breathing_break)
        self._timer_manager.set_eye_rest_callback(self._on_eye_rest)

        # Register Gio actions for notification snooze buttons
        self._register_actions()

        # Create tray icon
        self._tray_icon = TrayIcon(
            on_pause_toggle=self._on_pause_toggle,
            on_skip=self._on_skip,
            on_take_break=self._on_take_break,
            on_quit=self._on_quit,
            get_seconds_remaining=self._timer_manager.get_seconds_remaining,
            get_next_break_type=self._timer_manager.get_next_break_type,
            is_paused=self._timer_manager.is_paused,
            config=self._config,
            get_position_seconds=self._timer_manager.get_position_seconds_remaining,
            get_current_position=self._timer_manager.get_current_position,
            on_show_settings=self._on_show_settings,
            on_show_stats=self._on_show_stats,
        )

        # Set up screen lock detection
        self._screen_lock_detector = ScreenLockDetector(
            on_lock=self._on_screen_lock,
            on_unlock=self._on_screen_unlock,
        )
        self._screen_lock_detector.start()

        # Set up idle detection
        self._idle_detector = IdleDetector(
            config=self._config,
            on_idle=self._on_idle,
            on_active=self._on_active,
        )
        self._idle_detector.start()

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

    def _register_actions(self):
        """Register Gio actions for notification button callbacks."""
        snooze_water = Gio.SimpleAction.new("snooze-water", None)
        snooze_water.connect("activate", lambda *_: self._timer_manager.snooze_water())
        self.add_action(snooze_water)

        snooze_supp_morning = Gio.SimpleAction.new("snooze-supplement-morning", None)
        snooze_supp_morning.connect("activate", lambda *_: self._timer_manager.snooze_supplement(True))
        self.add_action(snooze_supp_morning)

        snooze_supp_evening = Gio.SimpleAction.new("snooze-supplement-evening", None)
        snooze_supp_evening.connect("activate", lambda *_: self._timer_manager.snooze_supplement(False))
        self.add_action(snooze_supp_evening)

    # --- Break overlay helpers ---

    def _show_break_overlay(self, break_type, duration, on_complete, on_skip, on_done_early=None, context=None):
        """Create and show break overlay on all monitors."""
        self._current_break_type = break_type
        context = context or {}

        # Compute track info for walk/lie-down breaks
        track_info = None
        if break_type in (BreakType.WALK, BreakType.LIE_DOWN) and self._routine_progress:
            from . import tips
            tracks = tips.WALK_TRACKS if break_type == BreakType.WALK else tips.LIE_DOWN_TRACKS
            pinned_key = "pinned_walk_track" if break_type == BreakType.WALK else "pinned_lie_down_track"
            pinned = self._config.get(pinned_key) if self._config.get("routine_mode") == "manual" else None
            track_id = self._routine_progress.get_today_track_id(tracks, pinned)
            routine = self._routine_progress.get_routine(tracks, track_id)
            if routine:
                context["routine"] = routine
                context["track_id"] = track_id
                track_data = tracks[track_id]
                track_info = {
                    "track_name": track_data["name"],
                    "level": self._routine_progress.get_level(track_id),
                    "completions": self._routine_progress.get_completions(track_id),
                    "max_level": self._routine_progress.get_max_level(tracks, track_id),
                }

        streak = self._routine_progress.get_streak() if self._routine_progress else 0

        # Extract breathing exercise from context
        breathing_exercise = context.pop("breathing_exercise", None) if context else None

        display = Gdk.Display.get_default()
        monitors = display.get_monitors()
        n_monitors = monitors.get_n_items()

        primary_monitor = None
        if n_monitors > 0:
            primary_monitor = monitors.get_item(0)

        self._current_overlay = BreakOverlay(
            break_type=break_type,
            duration_minutes=duration,
            on_complete=on_complete,
            on_skip=on_skip,
            sound_player=self._sound_player,
            context=context,
            on_done_early=on_done_early,
            monitor=primary_monitor if n_monitors > 1 else None,
            track_info=track_info,
            streak=streak,
            breathing_exercise=breathing_exercise,
        )
        self._current_overlay.present()

        # Secondary monitors: blocking overlays
        self._blocking_overlays = []
        for i in range(1, n_monitors):
            monitor = monitors.get_item(i)
            blocker = BlockingOverlay(monitor=monitor)
            blocker.present()
            self._blocking_overlays.append(blocker)

        if n_monitors > 0:
            monitors.connect("items-changed", self._on_monitors_changed)

    def _close_blocking_overlays(self):
        """Close all secondary monitor blocking overlays."""
        for blocker in self._blocking_overlays:
            blocker.close()
        self._blocking_overlays.clear()

    def _on_monitors_changed(self, model, position, removed, added):
        """Handle monitor hotplug during a break."""
        if not self._current_overlay:
            return
        # Recreate blocking overlays for any new monitors
        display = Gdk.Display.get_default()
        monitors = display.get_monitors()
        # Close existing blockers and recreate
        self._close_blocking_overlays()
        for i in range(1, monitors.get_n_items()):
            monitor = monitors.get_item(i)
            blocker = BlockingOverlay(monitor=monitor)
            blocker.present()
            self._blocking_overlays.append(blocker)

    # --- Pomodoro break callbacks ---

    def _on_pomodoro_complete(self, break_type: str):
        """Called when pomodoro timer completes - show break overlay."""
        if self._current_overlay:
            return  # Already showing a break

        self._sound_player.play_break_start()
        duration = self._timer_manager.get_break_duration(break_type)

        self._show_break_overlay(
            break_type=break_type,
            duration=duration,
            on_complete=self._on_break_complete,
            on_skip=self._on_break_skipped,
            on_done_early=self._on_break_done_early,
        )

    def _on_break_complete(self):
        """Called when break timer runs to zero."""
        bt = self._current_break_type
        self._close_blocking_overlays()
        self._current_overlay = None
        self._current_break_type = None
        if bt:
            self._stats_manager.log_break_completed(bt)
        if bt in (BreakType.WALK, BreakType.LIE_DOWN) and self._routine_progress:
            from . import tips
            tracks = tips.WALK_TRACKS if bt == BreakType.WALK else tips.LIE_DOWN_TRACKS
            pinned_key = "pinned_walk_track" if bt == BreakType.WALK else "pinned_lie_down_track"
            pinned = self._config.get(pinned_key) if self._config.get("routine_mode") == "manual" else None
            track_id = self._routine_progress.get_today_track_id(tracks, pinned)
            self._routine_progress.record_completion(track_id, tracks)
        if self._routine_progress:
            self._routine_progress.record_day_completion()
        self._timer_manager.break_completed()

    def _on_break_done_early(self):
        """Called when user clicks Done Early."""
        bt = self._current_break_type
        self._close_blocking_overlays()
        self._current_overlay = None
        self._current_break_type = None
        if bt:
            self._stats_manager.log_break_done_early(bt)
        if bt in (BreakType.WALK, BreakType.LIE_DOWN) and self._routine_progress:
            from . import tips
            tracks = tips.WALK_TRACKS if bt == BreakType.WALK else tips.LIE_DOWN_TRACKS
            pinned_key = "pinned_walk_track" if bt == BreakType.WALK else "pinned_lie_down_track"
            pinned = self._config.get(pinned_key) if self._config.get("routine_mode") == "manual" else None
            track_id = self._routine_progress.get_today_track_id(tracks, pinned)
            self._routine_progress.record_completion(track_id, tracks)
        if self._routine_progress:
            self._routine_progress.record_day_completion()
        self._timer_manager.break_completed()

    def _on_break_skipped(self):
        """Called when break is skipped (emergency)."""
        bt = self._current_break_type
        self._close_blocking_overlays()
        self._current_overlay = None
        self._current_break_type = None
        if bt:
            self._stats_manager.log_break_skipped(bt)
        if self._routine_progress:
            self._routine_progress.record_skip()
        self._timer_manager.skip_break()

    # --- Position switch callbacks ---

    def _on_position_switch(self, break_type: str):
        """Called when position switch timer fires."""
        if self._current_overlay:
            self._timer_manager.position_switch_completed()
            return

        self._sound_player.play_break_start()

        current = self._timer_manager.get_current_position()
        next_position = "standing" if current == "sitting" else "sitting"
        duration = self._timer_manager.get_break_duration(break_type)

        self._show_break_overlay(
            break_type=break_type,
            duration=duration,
            on_complete=self._on_position_switch_complete,
            on_skip=self._on_position_switch_skipped,
            context={"next_position": next_position},
        )

    def _on_position_switch_complete(self):
        """Called when position switch break completes."""
        self._close_blocking_overlays()
        self._current_overlay = None
        self._current_break_type = None
        self._timer_manager.position_switch_completed()

    def _on_position_switch_skipped(self):
        """Called when position switch break is skipped."""
        self._close_blocking_overlays()
        self._current_overlay = None
        self._current_break_type = None
        self._timer_manager.position_switch_completed()

    # --- Physio break callbacks ---

    def _on_physio_reminder(self):
        """Called when physio workout time arrives."""
        if self._current_overlay:
            return  # Already showing a break

        self._sound_player.play_break_start()

        self._show_break_overlay(
            break_type=BreakType.PHYSIO,
            duration=None,
            on_complete=self._on_physio_complete,
            on_skip=self._on_physio_skipped,
        )

    def _on_physio_complete(self):
        """Called when user clicks Done on physio break."""
        bt = self._current_break_type
        self._close_blocking_overlays()
        self._current_overlay = None
        self._current_break_type = None
        if bt:
            self._stats_manager.log_break_completed(bt)

    def _on_physio_skipped(self):
        """Called when physio break is skipped."""
        bt = self._current_break_type
        self._close_blocking_overlays()
        self._current_overlay = None
        self._current_break_type = None
        if bt:
            self._stats_manager.log_break_skipped(bt)

    # --- Breathing break callbacks ---

    def _on_breathing_break(self):
        """Called when a breathing break should trigger."""
        if self._current_overlay:
            return

        from . import tips
        exercise = tips.get_breathing_exercise()

        self._sound_player.play_break_start()

        self._show_break_overlay(
            break_type=BreakType.BREATHING,
            duration=2,
            on_complete=self._on_breathing_complete,
            on_skip=self._on_breathing_skipped,
            on_done_early=self._on_breathing_done_early,
            context={"breathing_exercise": exercise},
        )

    def _on_breathing_complete(self):
        """Called when breathing break timer runs to zero."""
        bt = self._current_break_type
        self._close_blocking_overlays()
        self._current_overlay = None
        self._current_break_type = None
        if bt:
            self._stats_manager.log_break_completed(bt)

    def _on_breathing_done_early(self):
        """Called when user clicks Done Early on breathing break."""
        bt = self._current_break_type
        self._close_blocking_overlays()
        self._current_overlay = None
        self._current_break_type = None
        if bt:
            self._stats_manager.log_break_done_early(bt)

    def _on_breathing_skipped(self):
        """Called when breathing break is skipped."""
        bt = self._current_break_type
        self._close_blocking_overlays()
        self._current_overlay = None
        self._current_break_type = None
        if bt:
            self._stats_manager.log_break_skipped(bt)

    # --- Eye rest callbacks ---

    def _on_eye_rest(self):
        """Called when eye rest micro-break triggers."""
        if self._current_overlay or self._current_micro_overlay:
            return

        self._current_micro_overlay = MicroBreakOverlay(
            message="Look at something 20 feet away",
            duration_seconds=20,
            on_complete=self._on_eye_rest_complete,
        )
        self._current_micro_overlay.present()

    def _on_eye_rest_complete(self):
        """Called when eye rest micro-break auto-completes."""
        self._current_micro_overlay = None
        self._stats_manager.log_break_completed(BreakType.EYE_REST)

    # --- Notification callbacks ---

    def _on_water_reminder(self):
        """Called for water reminders."""
        self._sound_player.play_water_reminder()
        self._notification_manager.show_water_reminder()

    def _on_supplement_reminder(self, morning: bool):
        """Called for supplement reminders."""
        self._sound_player.play_supplement_reminder()
        self._notification_manager.show_supplement_reminder(morning)

    def _on_pre_break_warning(self, break_type: str, seconds: int):
        """Called when a pre-break warning should be shown."""
        self._notification_manager.show_pre_break_warning(break_type, seconds)

    # --- Screen lock / idle auto-pause ---

    def _on_screen_lock(self):
        """Called when screen is locked or system suspends."""
        if not self._timer_manager.is_paused():
            self._timer_manager.pause()
            self._lock_auto_paused = True

    def _on_screen_unlock(self):
        """Called when screen is unlocked or system resumes."""
        if self._lock_auto_paused:
            self._lock_auto_paused = False
            if not self._idle_auto_paused:
                self._timer_manager.resume()

    def _on_idle(self):
        """Called when user becomes idle."""
        if not self._timer_manager.is_paused():
            self._timer_manager.pause()
            self._idle_auto_paused = True

    def _on_active(self):
        """Called when user becomes active after being idle."""
        if self._idle_auto_paused:
            self._idle_auto_paused = False
            if not self._lock_auto_paused:
                self._timer_manager.resume()

    # --- Tray menu actions ---

    def _on_pause_toggle(self):
        """Toggle pause state."""
        if self._timer_manager.is_paused():
            self._lock_auto_paused = False
            self._idle_auto_paused = False
            self._timer_manager.resume()
        else:
            self._timer_manager.pause()

    def _on_skip(self):
        """Skip the next break."""
        self._timer_manager.skip_break()

    def _on_take_break(self):
        """Take a break immediately."""
        self._timer_manager.take_break_now()

    def _on_show_settings(self):
        """Show the settings dialog."""
        if self._settings_window:
            self._settings_window.present()
            return
        self._settings_window = SettingsDialog(self._config, application=self, routine_progress=self._routine_progress)
        self._settings_window.connect("close-request", self._on_settings_closed)
        self._settings_window.present()

    def _on_settings_closed(self, window):
        """Called when settings window is closed."""
        self._settings_window = None
        return False

    def _on_show_stats(self):
        """Show the statistics window."""
        if self._stats_window:
            self._stats_window.present()
            return
        self._stats_window = StatsWindow(self._stats_manager, application=self)
        self._stats_window.connect("close-request", self._on_stats_closed)
        self._stats_window.present()

    def _on_stats_closed(self, window):
        """Called when stats window is closed."""
        self._stats_window = None
        return False

    def _on_quit(self):
        """Quit the application."""
        if self._screen_lock_detector:
            self._screen_lock_detector.stop()
        if self._idle_detector:
            self._idle_detector.stop()
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
