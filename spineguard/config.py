"""Configuration management for SpineGuard."""

import json
from pathlib import Path
from typing import Any, Callable, Optional

CONFIG_DIR = Path.home() / ".config" / "spineguard"
CONFIG_FILE = CONFIG_DIR / "config.json"

STATE_DIR = Path.home() / ".local" / "share" / "spineguard"
STATE_FILE = STATE_DIR / "state.json"
STATS_FILE = STATE_DIR / "stats.jsonl"

DEFAULTS = {
    "mode": "recovery",
    "pomodoro_minutes": 25,
    "walk_break_minutes": 5,
    "lie_down_break_minutes": 10,
    "water_interval_minutes": 60,
    "supplement_morning_hour": 8,
    "supplement_morning_minute": 0,
    "supplement_evening_hour": 20,
    "supplement_evening_minute": 0,
    "position_switch_interval_minutes": 30,
    "position_switch_break_minutes": 1,
    "idle_threshold_minutes": 2,
    "idle_detection_enabled": True,
    "pre_break_warning_minutes": 2,
    "hotkey_pause": "ctrl+shift+p",
    "hotkey_break": "ctrl+shift+b",
    "sound_break_start": "complete",
    "sound_break_end": "bell",
    "sound_water": "message",
    "sound_supplement": "message",
    "physio_enabled": True,
    "physio_hour": 14,
    "physio_minute": 0,
    "breathing_enabled": True,
    "breathing_frequency": 3,
    "eye_rest_enabled": True,
    "eye_rest_interval_minutes": 20,
    "routine_mode": "auto",
    "pinned_walk_track": None,
    "pinned_lie_down_track": None,
}


class Config:
    """Manages SpineGuard configuration with JSON persistence."""

    def __init__(self):
        self._data: dict = {}
        self._callbacks: list[Callable[[str, Any], None]] = []
        self._load()

    def _load(self):
        """Load config from disk, writing defaults on first run."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r") as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._data = {}

        # Merge in any missing defaults
        changed = False
        for key, value in DEFAULTS.items():
            if key not in self._data:
                self._data[key] = value
                changed = True

        if changed:
            self._save()

    def _save(self):
        """Save config to disk."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self._data, f, indent=2)
        except IOError:
            pass

    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value."""
        return self._data.get(key, default if default is not None else DEFAULTS.get(key))

    def set(self, key: str, value: Any):
        """Set a config value and notify callbacks."""
        old_value = self._data.get(key)
        if old_value == value:
            return
        self._data[key] = value
        self._save()
        for callback in self._callbacks:
            callback(key, value)

    def on_change(self, callback: Callable[[str, Any], None]):
        """Register a callback for config changes. Called with (key, value)."""
        self._callbacks.append(callback)

    @property
    def is_sit_stand(self) -> bool:
        """Check if sit-stand desk mode is active."""
        return self.get("mode") == "sit_stand"

    @property
    def mode(self) -> str:
        """Get the current mode."""
        return self.get("mode")
