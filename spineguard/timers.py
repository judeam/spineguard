"""Timer management for SpineGuard."""

import json
import os
from datetime import datetime, time as dt_time
from pathlib import Path
from typing import Callable, Optional

from gi.repository import GLib

# Configuration
POMODORO_MINUTES = 25
WALK_BREAK_MINUTES = 5
LIE_DOWN_BREAK_MINUTES = 10
WATER_INTERVAL_MINUTES = 60

# Supplement times
SUPPLEMENT_MORNING = dt_time(8, 0)
SUPPLEMENT_EVENING = dt_time(20, 0)

# State directory
STATE_DIR = Path.home() / ".local" / "share" / "spineguard"
STATE_FILE = STATE_DIR / "state.json"


class BreakType:
    WALK = "walk"
    LIE_DOWN = "lie_down"


class TimerManager:
    """Manages all timers for SpineGuard."""

    def __init__(self):
        self._pomodoro_callback: Optional[Callable[[str], None]] = None
        self._water_callback: Optional[Callable[[], None]] = None
        self._supplement_callback: Optional[Callable[[bool], None]] = None

        self._pomodoro_timer_id: Optional[int] = None
        self._water_timer_id: Optional[int] = None
        self._supplement_timer_id: Optional[int] = None
        self._countdown_timer_id: Optional[int] = None

        self._seconds_remaining: int = POMODORO_MINUTES * 60
        self._paused: bool = False
        self._next_break_type: str = BreakType.WALK

        self._load_state()

    def _ensure_state_dir(self):
        """Create state directory if it doesn't exist."""
        STATE_DIR.mkdir(parents=True, exist_ok=True)

    def _load_state(self):
        """Load persisted state from disk."""
        self._ensure_state_dir()
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r") as f:
                    state = json.load(f)
                    self._next_break_type = state.get("next_break_type", BreakType.WALK)
            except (json.JSONDecodeError, IOError):
                pass

    def _save_state(self):
        """Save state to disk."""
        self._ensure_state_dir()
        state = {"next_break_type": self._next_break_type}
        try:
            with open(STATE_FILE, "w") as f:
                json.dump(state, f)
        except IOError:
            pass

    def set_pomodoro_callback(self, callback: Callable[[str], None]):
        """Set callback for when pomodoro timer completes. Receives break type."""
        self._pomodoro_callback = callback

    def set_water_callback(self, callback: Callable[[], None]):
        """Set callback for water reminders."""
        self._water_callback = callback

    def set_supplement_callback(self, callback: Callable[[bool], None]):
        """Set callback for supplement reminders. Receives True for morning."""
        self._supplement_callback = callback

    def start(self):
        """Start all timers."""
        self._start_pomodoro_countdown()
        self._start_water_timer()
        self._schedule_supplement_check()

    def stop(self):
        """Stop all timers."""
        if self._pomodoro_timer_id:
            GLib.source_remove(self._pomodoro_timer_id)
            self._pomodoro_timer_id = None
        if self._countdown_timer_id:
            GLib.source_remove(self._countdown_timer_id)
            self._countdown_timer_id = None
        if self._water_timer_id:
            GLib.source_remove(self._water_timer_id)
            self._water_timer_id = None
        if self._supplement_timer_id:
            GLib.source_remove(self._supplement_timer_id)
            self._supplement_timer_id = None

    def pause(self):
        """Pause the pomodoro timer."""
        self._paused = True

    def resume(self):
        """Resume the pomodoro timer."""
        self._paused = False

    def is_paused(self) -> bool:
        """Check if timer is paused."""
        return self._paused

    def skip_break(self):
        """Skip the current break and start next cycle."""
        self._alternate_break_type()
        self.reset_pomodoro()

    def take_break_now(self):
        """Trigger a break immediately."""
        if self._pomodoro_callback:
            self._pomodoro_callback(self._next_break_type)

    def reset_pomodoro(self):
        """Reset the pomodoro timer to full duration."""
        self._seconds_remaining = POMODORO_MINUTES * 60
        self._start_pomodoro_countdown()

    def get_seconds_remaining(self) -> int:
        """Get seconds remaining until next break."""
        return self._seconds_remaining

    def get_next_break_type(self) -> str:
        """Get the type of the next break."""
        return self._next_break_type

    def get_break_duration(self, break_type: str) -> int:
        """Get duration in minutes for a break type."""
        if break_type == BreakType.WALK:
            return WALK_BREAK_MINUTES
        return LIE_DOWN_BREAK_MINUTES

    def break_completed(self):
        """Called when a break is completed. Alternates break type and resets timer."""
        self._alternate_break_type()
        self.reset_pomodoro()

    def _alternate_break_type(self):
        """Switch between walk and lie down breaks."""
        if self._next_break_type == BreakType.WALK:
            self._next_break_type = BreakType.LIE_DOWN
        else:
            self._next_break_type = BreakType.WALK
        self._save_state()

    def _start_pomodoro_countdown(self):
        """Start the countdown timer that ticks every second."""
        if self._countdown_timer_id:
            GLib.source_remove(self._countdown_timer_id)
        self._countdown_timer_id = GLib.timeout_add_seconds(1, self._pomodoro_tick)

    def _pomodoro_tick(self) -> bool:
        """Called every second to update countdown."""
        if self._paused:
            return True

        self._seconds_remaining -= 1

        if self._seconds_remaining <= 0:
            if self._pomodoro_callback:
                self._pomodoro_callback(self._next_break_type)
            return False

        return True

    def _start_water_timer(self):
        """Start the water reminder timer."""
        if self._water_timer_id:
            GLib.source_remove(self._water_timer_id)
        self._water_timer_id = GLib.timeout_add_seconds(
            WATER_INTERVAL_MINUTES * 60, self._water_reminder
        )

    def _water_reminder(self) -> bool:
        """Called when water reminder is due."""
        if self._water_callback:
            self._water_callback()
        return True

    def _schedule_supplement_check(self):
        """Schedule periodic checks for supplement times."""
        if self._supplement_timer_id:
            GLib.source_remove(self._supplement_timer_id)
        self._supplement_timer_id = GLib.timeout_add_seconds(
            60, self._check_supplement_time
        )
        self._check_supplement_time()

    def _check_supplement_time(self) -> bool:
        """Check if it's time for supplements."""
        now = datetime.now().time()

        if self._is_time_match(now, SUPPLEMENT_MORNING):
            if self._supplement_callback:
                self._supplement_callback(True)
        elif self._is_time_match(now, SUPPLEMENT_EVENING):
            if self._supplement_callback:
                self._supplement_callback(False)

        return True

    def _is_time_match(self, current: dt_time, target: dt_time) -> bool:
        """Check if current time matches target (within same minute)."""
        return current.hour == target.hour and current.minute == target.minute
