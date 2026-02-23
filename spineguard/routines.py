"""Routine progression and streak tracking for SpineGuard."""

import json
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

from . import tips
from .config import STATE_DIR, STATE_FILE

# Daily rotation: day-of-week (0=Mon) maps to track index
ROTATION = [0, 1, 2, 0, 1, 2, 0]  # Mon=0, Tue=1, Wed=2, Thu=0, ...

COMPLETIONS_TO_LEVEL_UP = 5


class RoutineProgress:
    """Manages routine track progression and streak tracking."""

    def __init__(self):
        self._progress: dict = {}
        self._streak: dict = {"current": 0, "last_date": None, "skipped_today": False}
        self._load()

    def _load(self):
        """Load progress from state.json."""
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r") as f:
                    state = json.load(f)
                    self._progress = state.get("routine_progress", {})
                    self._streak = state.get("streak", {"current": 0, "last_date": None, "skipped_today": False})
            except (json.JSONDecodeError, IOError):
                pass

    def _save(self):
        """Save progress to state.json (merge with existing state)."""
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        state = {}
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, "r") as f:
                    state = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        state["routine_progress"] = self._progress
        state["streak"] = self._streak
        try:
            with open(STATE_FILE, "w") as f:
                json.dump(state, f)
        except IOError:
            pass

    def get_today_track_id(self, tracks: dict, pinned: Optional[str] = None) -> str:
        """Get today's track ID based on rotation or pinned preference."""
        if pinned and pinned in tracks:
            return pinned
        track_ids = list(tracks.keys())
        day_index = ROTATION[date.today().weekday()]
        return track_ids[day_index % len(track_ids)]

    def get_level(self, track_id: str) -> int:
        """Get current level (0-indexed) for a track."""
        return self._progress.get(track_id, {}).get("level", 0)

    def get_completions(self, track_id: str) -> int:
        """Get completions toward next level."""
        return self._progress.get(track_id, {}).get("completions", 0)

    def get_max_level(self, tracks: dict, track_id: str) -> int:
        """Get max level for a track."""
        track = tracks.get(track_id)
        if not track:
            return 0
        return len(track["routines"]) - 1

    def record_completion(self, track_id: str, tracks: dict) -> bool:
        """Record a routine completion. Returns True if level-up occurred."""
        if track_id not in self._progress:
            self._progress[track_id] = {"level": 0, "completions": 0}

        entry = self._progress[track_id]
        entry["completions"] += 1

        leveled_up = False
        max_level = self.get_max_level(tracks, track_id)

        if entry["completions"] >= COMPLETIONS_TO_LEVEL_UP and entry["level"] < max_level:
            entry["level"] += 1
            entry["completions"] = 0
            leveled_up = True

        self._save()
        return leveled_up

    def get_routine(self, tracks: dict, track_id: str):
        """Get the current routine for a track based on progress level."""
        level = self.get_level(track_id)
        return tips.get_track_routine(tracks, track_id, level)

    # --- Streak ---

    def get_streak(self) -> int:
        """Get current streak count."""
        today = date.today().isoformat()
        if self._streak.get("last_date") != today:
            yesterday = (date.today() - timedelta(days=1)).isoformat()
            if self._streak.get("last_date") != yesterday:
                self._streak["current"] = 0
            self._streak["skipped_today"] = False
        return self._streak.get("current", 0)

    def record_day_completion(self):
        """Mark today as a completed day."""
        today = date.today().isoformat()
        if not self._streak.get("skipped_today", False):
            if self._streak.get("last_date") != today:
                self._streak["current"] = self._streak.get("current", 0) + 1
                self._streak["last_date"] = today
        self._save()

    def record_skip(self):
        """Record that a break was skipped today. Resets streak."""
        self._streak["skipped_today"] = True
        self._streak["current"] = 0
        self._streak["last_date"] = date.today().isoformat()
        self._save()

    def reset_progress(self):
        """Reset all track progress (for settings reset button)."""
        self._progress = {}
        self._save()
