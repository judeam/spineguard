"""Timer management for SpineGuard."""

import json
from datetime import datetime, time as dt_time
from pathlib import Path
from typing import Any, Callable, Optional

from gi.repository import GLib

from .config import Config

# State directory
STATE_DIR = Path.home() / ".local" / "share" / "spineguard"
STATE_FILE = STATE_DIR / "state.json"


class BreakType:
    WALK = "walk"
    LIE_DOWN = "lie_down"
    POSITION_SWITCH = "position_switch"
    PHYSIO = "physio"
    BREATHING = "breathing"
    EYE_REST = "eye_rest"


class TimerManager:
    """Manages all timers for SpineGuard."""

    def __init__(self, config: Config):
        self._config = config

        self._pomodoro_callback: Optional[Callable[[str], None]] = None
        self._water_callback: Optional[Callable[[], None]] = None
        self._supplement_callback: Optional[Callable[[bool], None]] = None
        self._position_callback: Optional[Callable[[str], None]] = None
        self._physio_callback: Optional[Callable[[], None]] = None
        self._pre_break_warning_callback: Optional[Callable[[str, int], None]] = None
        self._warning_fired: bool = False

        self._pomodoro_timer_id: Optional[int] = None
        self._supplement_timer_id: Optional[int] = None
        self._physio_timer_id: Optional[int] = None
        self._countdown_timer_id: Optional[int] = None

        # Water timer fields (1-second tick, respects pause)
        self._water_countdown_id: Optional[int] = None
        self._water_seconds_remaining: int = 0

        # Position switch timer fields
        self._position_timer_id: Optional[int] = None
        self._position_countdown_id: Optional[int] = None
        self._position_seconds_remaining: int = 0
        self._current_position: str = "sitting"

        # Breathing break timer
        self._breathing_callback: Optional[Callable[[], None]] = None
        self._pomodoro_cycle_count: int = 0

        # Eye rest timer
        self._eye_rest_callback: Optional[Callable[[], None]] = None
        self._eye_rest_countdown_id: Optional[int] = None
        self._eye_rest_seconds_remaining: int = 0

        self._seconds_remaining: int = self._config.get("pomodoro_minutes") * 60
        self._paused: bool = False
        self._next_break_type: str = BreakType.WALK

        self._load_state()

        # Listen for live config changes
        self._config.on_change(self._on_config_change)

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
                    self._current_position = state.get("current_position", "sitting")
            except (json.JSONDecodeError, IOError):
                pass

    def _save_state(self):
        """Save state to disk."""
        self._ensure_state_dir()
        state = {
            "next_break_type": self._next_break_type,
            "current_position": self._current_position,
        }
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

    def set_position_callback(self, callback: Callable[[str], None]):
        """Set callback for position switch reminders. Receives break type."""
        self._position_callback = callback

    def set_physio_callback(self, callback: Callable[[], None]):
        """Set callback for physio workout reminders."""
        self._physio_callback = callback

    def set_pre_break_warning_callback(self, callback: Callable[[str, int], None]):
        """Set callback for pre-break warnings. Receives (break_type, seconds_remaining)."""
        self._pre_break_warning_callback = callback

    def set_breathing_callback(self, callback: Callable[[], None]):
        """Set callback for breathing break reminders."""
        self._breathing_callback = callback

    def set_eye_rest_callback(self, callback: Callable[[], None]):
        """Set callback for eye rest micro-breaks."""
        self._eye_rest_callback = callback

    def start(self):
        """Start all timers."""
        self._start_pomodoro_countdown()
        self._start_water_timer()
        self._schedule_supplement_check()
        if self._config.get("physio_enabled"):
            self._schedule_physio_check()
        if self._config.is_sit_stand:
            self._start_position_timer()
        self._start_eye_rest_timer()

    def stop(self):
        """Stop all timers."""
        if self._pomodoro_timer_id:
            GLib.source_remove(self._pomodoro_timer_id)
            self._pomodoro_timer_id = None
        if self._countdown_timer_id:
            GLib.source_remove(self._countdown_timer_id)
            self._countdown_timer_id = None
        if self._water_countdown_id:
            GLib.source_remove(self._water_countdown_id)
            self._water_countdown_id = None
        if self._supplement_timer_id:
            GLib.source_remove(self._supplement_timer_id)
            self._supplement_timer_id = None
        if self._physio_timer_id:
            GLib.source_remove(self._physio_timer_id)
            self._physio_timer_id = None
        self._stop_position_timer()
        self._stop_eye_rest_timer()

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
        self._seconds_remaining = self._config.get("pomodoro_minutes") * 60
        self._warning_fired = False
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
            return self._config.get("walk_break_minutes")
        elif break_type == BreakType.POSITION_SWITCH:
            return self._config.get("position_switch_break_minutes")
        return self._config.get("lie_down_break_minutes")

    def break_completed(self):
        """Called when a break is completed. Alternates break type and resets timer."""
        self._pomodoro_cycle_count += 1
        self._alternate_break_type()
        self.reset_pomodoro()
        self._check_breathing_break()

    def _alternate_break_type(self):
        """Switch between walk and lie down breaks."""
        if self._next_break_type == BreakType.WALK:
            self._next_break_type = BreakType.LIE_DOWN
        else:
            self._next_break_type = BreakType.WALK
        self._save_state()

    # --- Position switch timer ---

    def get_position_seconds_remaining(self) -> int:
        """Get seconds remaining until next position switch."""
        return self._position_seconds_remaining

    def get_current_position(self) -> str:
        """Get the current sit/stand position."""
        return self._current_position

    def position_switch_completed(self):
        """Called when a position switch break completes. Toggle position and restart timer."""
        self._current_position = "standing" if self._current_position == "sitting" else "sitting"
        self._save_state()
        self._start_position_timer()

    def _start_position_timer(self):
        """Start the position switch countdown."""
        self._stop_position_timer()
        interval = self._config.get("position_switch_interval_minutes")
        self._position_seconds_remaining = interval * 60
        self._position_countdown_id = GLib.timeout_add_seconds(1, self._position_tick)

    def _stop_position_timer(self):
        """Stop the position switch timer."""
        if self._position_countdown_id:
            GLib.source_remove(self._position_countdown_id)
            self._position_countdown_id = None
        self._position_seconds_remaining = 0

    def _position_tick(self) -> bool:
        """Called every second to update position switch countdown."""
        if self._paused:
            return True

        self._position_seconds_remaining -= 1

        if self._position_seconds_remaining <= 0:
            if self._position_callback:
                self._position_callback(BreakType.POSITION_SWITCH)
            return False

        return True

    # --- Breathing timer ---

    def _check_breathing_break(self):
        """Check if a breathing break should trigger after a pomodoro cycle."""
        if not self._config.get("breathing_enabled"):
            return
        freq = self._config.get("breathing_frequency")
        if freq and self._pomodoro_cycle_count > 0 and self._pomodoro_cycle_count % freq == 0:
            if self._breathing_callback:
                self._breathing_callback()

    # --- Eye rest timer ---

    def _start_eye_rest_timer(self):
        """Start the eye rest micro-break countdown."""
        self._stop_eye_rest_timer()
        if not self._config.get("eye_rest_enabled"):
            return
        interval = self._config.get("eye_rest_interval_minutes")
        self._eye_rest_seconds_remaining = interval * 60
        self._eye_rest_countdown_id = GLib.timeout_add_seconds(1, self._eye_rest_tick)

    def _stop_eye_rest_timer(self):
        """Stop the eye rest timer."""
        if self._eye_rest_countdown_id:
            GLib.source_remove(self._eye_rest_countdown_id)
            self._eye_rest_countdown_id = None
        self._eye_rest_seconds_remaining = 0

    def _eye_rest_tick(self) -> bool:
        """Called every second to update eye rest countdown."""
        if self._paused:
            return True
        self._eye_rest_seconds_remaining -= 1
        if self._eye_rest_seconds_remaining <= 0:
            if self._eye_rest_callback:
                self._eye_rest_callback()
            # Restart
            interval = self._config.get("eye_rest_interval_minutes")
            self._eye_rest_seconds_remaining = interval * 60
        return True

    def _on_config_change(self, key: str, value: Any):
        """Handle live config changes."""
        if key == "mode":
            if value == "sit_stand":
                self._start_position_timer()
            else:
                self._stop_position_timer()
        elif key == "physio_enabled":
            if value:
                self._schedule_physio_check()
            else:
                if self._physio_timer_id:
                    GLib.source_remove(self._physio_timer_id)
                    self._physio_timer_id = None
        elif key == "eye_rest_enabled":
            if value:
                self._start_eye_rest_timer()
            else:
                self._stop_eye_rest_timer()

    # --- Pomodoro timer ---

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

        # Pre-break warning
        warning_minutes = self._config.get("pre_break_warning_minutes")
        if (
            warning_minutes
            and not self._warning_fired
            and self._seconds_remaining == warning_minutes * 60
            and self._pre_break_warning_callback
        ):
            self._warning_fired = True
            self._pre_break_warning_callback(self._next_break_type, self._seconds_remaining)

        if self._seconds_remaining <= 0:
            if self._pomodoro_callback:
                self._pomodoro_callback(self._next_break_type)
            return False

        return True

    def get_water_seconds_remaining(self) -> int:
        """Get seconds remaining until next water reminder."""
        return self._water_seconds_remaining

    def snooze_water(self, minutes: int = 10):
        """Snooze the water timer by restarting with a shorter interval."""
        if self._water_countdown_id:
            GLib.source_remove(self._water_countdown_id)
            self._water_countdown_id = None
        self._water_seconds_remaining = minutes * 60
        self._water_countdown_id = GLib.timeout_add_seconds(1, self._water_tick)

    def snooze_supplement(self, morning: bool, minutes: int = 10):
        """Snooze a supplement reminder by scheduling a one-shot re-fire."""
        def _re_fire():
            if self._supplement_callback:
                self._supplement_callback(morning)
            return False  # One-shot
        GLib.timeout_add_seconds(minutes * 60, _re_fire)

    def _start_water_timer(self):
        """Start the water reminder countdown."""
        if self._water_countdown_id:
            GLib.source_remove(self._water_countdown_id)
        interval = self._config.get("water_interval_minutes")
        self._water_seconds_remaining = interval * 60
        self._water_countdown_id = GLib.timeout_add_seconds(1, self._water_tick)

    def _water_tick(self) -> bool:
        """Called every second to update water countdown."""
        if self._paused:
            return True

        self._water_seconds_remaining -= 1

        if self._water_seconds_remaining <= 0:
            if self._water_callback:
                self._water_callback()
            # Restart the water timer
            interval = self._config.get("water_interval_minutes")
            self._water_seconds_remaining = interval * 60
            return True

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

        morning = dt_time(
            self._config.get("supplement_morning_hour"),
            self._config.get("supplement_morning_minute"),
        )
        evening = dt_time(
            self._config.get("supplement_evening_hour"),
            self._config.get("supplement_evening_minute"),
        )

        if self._is_time_match(now, morning):
            if self._supplement_callback:
                self._supplement_callback(True)
        elif self._is_time_match(now, evening):
            if self._supplement_callback:
                self._supplement_callback(False)

        return True

    def _is_time_match(self, current: dt_time, target: dt_time) -> bool:
        """Check if current time matches target (within same minute)."""
        return current.hour == target.hour and current.minute == target.minute

    # --- Physio timer ---

    def _schedule_physio_check(self):
        """Schedule periodic checks for physio workout time."""
        if self._physio_timer_id:
            GLib.source_remove(self._physio_timer_id)
        self._physio_timer_id = GLib.timeout_add_seconds(
            60, self._check_physio_time
        )
        self._check_physio_time()

    def _check_physio_time(self) -> bool:
        """Check if it's time for the physio workout."""
        now = datetime.now().time()
        target = dt_time(
            self._config.get("physio_hour"),
            self._config.get("physio_minute"),
        )
        if self._is_time_match(now, target):
            if self._physio_callback:
                self._physio_callback()
        return True

    def snooze_physio(self, minutes: int = 10):
        """Snooze the physio reminder by scheduling a one-shot re-fire."""
        def _re_fire():
            if self._physio_callback:
                self._physio_callback()
            return False  # One-shot
        GLib.timeout_add_seconds(minutes * 60, _re_fire)
