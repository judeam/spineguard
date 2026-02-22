# Progressive Routines + Break Variety — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace random routine selection with a progressive track system, add breathing exercises and eye-rest micro-breaks, and show streak/progression info on break overlays.

**Architecture:** Routines are reorganized into named tracks with leveled routines in `tips.py`. A new `RoutineProgress` class in `routines.py` manages track state, daily rotation, and level-up logic persisted to `state.json`. Two new timer types (breathing, eye-rest) are added to `TimerManager`. The existing `BreakOverlay` gains a breathing animation mode and track info display. A new lightweight `MicroBreakOverlay` handles 20-second eye-rest popups.

**Tech Stack:** Python 3.10+, GTK4, GLib, Cairo

**Note:** This project has no test suite (per CLAUDE.md). Each task includes manual verification steps instead of automated tests.

---

### Task 1: Reorganize routines into tracks (tips.py)

**Files:**
- Modify: `spineguard/tips.py`

**Step 1: Add track data structures**

Replace the flat `WALK_ROUTINES` and `LIE_DOWN_ROUTINES` lists with a track-based structure. Keep the existing routine dicts unchanged — just reorganize them into tracks and add new routines for levels that don't exist yet.

```python
# Add after the existing SUPPLEMENT_EVENING list (line 88), replacing WALK_ROUTINES and LIE_DOWN_ROUTINES

WALK_TRACKS = {
    "spinal_extension": {
        "name": "Spinal Extension",
        "focus": "McKenzie method",
        "routines": [
            # Level 1 — existing "McKenzie Standing Extensions" routine dict
            {
                "name": "McKenzie Standing Extensions",
                "benefit": "Relieves lower back pressure and improves spinal extension",
                "steps": [
                    {"instruction": "Stand with feet shoulder-width apart, hands on lower back", "duration_seconds": 10},
                    {"instruction": "Slowly lean backward, supporting with your hands — hold 5 seconds", "duration_seconds": 15},
                    {"instruction": "Return to upright. Repeat the extension", "duration_seconds": 15},
                    {"instruction": "Extend again — try to go slightly further each time", "duration_seconds": 15},
                    {"instruction": "Walk slowly with tall posture for the remaining time", "duration_seconds": 0},
                ],
            },
            # Level 2 — new
            {
                "name": "Wall Press-Ups",
                "benefit": "Progresses spinal extension with upper body support",
                "steps": [
                    {"instruction": "Stand facing a wall, hands at shoulder height, arms straight", "duration_seconds": 10},
                    {"instruction": "Lean your hips toward the wall while keeping hands planted — arch your back gently", "duration_seconds": 20},
                    {"instruction": "Push back to start. Repeat 5 times, going slightly deeper each rep", "duration_seconds": 30},
                    {"instruction": "Step back further from the wall for a deeper stretch. 3 more reps", "duration_seconds": 25},
                    {"instruction": "Walk with tall posture for the remaining time", "duration_seconds": 0},
                ],
            },
            # Level 3 — new
            {
                "name": "Standing Back Bends",
                "benefit": "Full range spinal extension without wall support",
                "steps": [
                    {"instruction": "Stand tall, feet hip-width apart, hands on lower back", "duration_seconds": 10},
                    {"instruction": "Breathe in, then slowly extend backward — reach your chest toward the ceiling", "duration_seconds": 20},
                    {"instruction": "Hold the extension 10 seconds. Breathe steadily", "duration_seconds": 15},
                    {"instruction": "Return to upright. Repeat 4 more times, reaching further each rep", "duration_seconds": 30},
                    {"instruction": "Walk with engaged core for the remaining time", "duration_seconds": 0},
                ],
            },
            # Level 4 — new
            {
                "name": "Dynamic Extension Walk",
                "benefit": "Combines spinal extension with walking movement",
                "steps": [
                    {"instruction": "Walk slowly. Every 5 steps, stop and do a standing back extension", "duration_seconds": 30},
                    {"instruction": "Continue walking. Add arm reaches overhead between extensions", "duration_seconds": 25},
                    {"instruction": "Walk with exaggerated arm swings and tall posture", "duration_seconds": 20},
                    {"instruction": "Final set: 3 standing extensions with 5-second holds", "duration_seconds": 20},
                    {"instruction": "Finish with a relaxed walk for the remaining time", "duration_seconds": 0},
                ],
            },
        ],
    },
    "lower_body": {
        "name": "Lower Body",
        "focus": "Glute/leg activation",
        "routines": [
            # Level 1 — existing "Gentle Walking Stretch Routine"
            {
                "name": "Gentle Walking Stretch Routine",
                "benefit": "Loosens hip flexors and mobilizes the spine gently",
                "steps": [
                    {"instruction": "Walk slowly, focusing on heel-to-toe gait", "duration_seconds": 30},
                    {"instruction": "Stop. Standing hip flexor stretch: step one foot forward, gently push hips forward — hold", "duration_seconds": 20},
                    {"instruction": "Switch legs and repeat the hip flexor stretch", "duration_seconds": 20},
                    {"instruction": "Standing tall, gently rotate your trunk left and right 5 times each", "duration_seconds": 20},
                    {"instruction": "Continue walking with engaged core for the remaining time", "duration_seconds": 0},
                ],
            },
            # Level 2 — existing "Single-Leg Balance & Glute Activation"
            {
                "name": "Single-Leg Balance & Glute Activation",
                "benefit": "Strengthens hip stabilizers and improves pelvic control",
                "steps": [
                    {"instruction": "Stand tall, feet hip-width apart. Shift weight to your left foot", "duration_seconds": 10},
                    {"instruction": "Lift your right foot off the floor. Balance for 20 seconds — squeeze your standing glute", "duration_seconds": 25},
                    {"instruction": "Switch sides. Balance on your right foot for 20 seconds", "duration_seconds": 25},
                    {"instruction": "Standing on one leg, slowly hinge forward at the hips (warrior 3). Hold 10 seconds each side", "duration_seconds": 30},
                    {"instruction": "Walk with engaged glutes and core for the remaining time", "duration_seconds": 0},
                ],
            },
            # Level 3 — existing "Wall Sit & Isometric Hold"
            {
                "name": "Wall Sit & Isometric Hold",
                "benefit": "Builds quad and core endurance to support the lower back",
                "steps": [
                    {"instruction": "Find a wall. Lean your back flat against it and slide down until knees are at 90 degrees", "duration_seconds": 10},
                    {"instruction": "Hold the wall sit — keep your lower back pressed into the wall. Breathe steadily", "duration_seconds": 30},
                    {"instruction": "Stand up and shake out your legs for 10 seconds", "duration_seconds": 15},
                    {"instruction": "Wall sit again — this time squeeze a fist between your knees to activate inner thighs", "duration_seconds": 30},
                    {"instruction": "Stand and walk slowly, focusing on tall posture for the remaining time", "duration_seconds": 0},
                ],
            },
            # Level 4 — new
            {
                "name": "Walking Lunges",
                "benefit": "Dynamic leg strengthening with spinal stability challenge",
                "steps": [
                    {"instruction": "Stand tall with hands on hips. Step forward into a lunge — front knee at 90 degrees", "duration_seconds": 15},
                    {"instruction": "Push off your front foot and step into the next lunge. 5 lunges per leg", "duration_seconds": 30},
                    {"instruction": "Rest 15 seconds, shake out your legs", "duration_seconds": 15},
                    {"instruction": "Repeat: 5 more lunges per leg, focusing on keeping your torso upright", "duration_seconds": 30},
                    {"instruction": "Walk slowly with tall posture for the remaining time", "duration_seconds": 0},
                ],
            },
        ],
    },
    "posture": {
        "name": "Posture",
        "focus": "Alignment",
        "routines": [
            # Level 1 — existing "Posture Reset Walk"
            {
                "name": "Posture Reset Walk",
                "benefit": "Resets spinal alignment and engages stabilizing muscles",
                "steps": [
                    {"instruction": "Stand tall. Pull shoulder blades together and down — hold 10 seconds", "duration_seconds": 15},
                    {"instruction": "Tuck your chin slightly (double chin). Hold 10 seconds", "duration_seconds": 15},
                    {"instruction": "Walk with this posture: shoulders back, chin tucked, core engaged", "duration_seconds": 30},
                    {"instruction": "Stop. Reach arms overhead, interlace fingers, stretch upward — hold", "duration_seconds": 15},
                    {"instruction": "Resume walking with good posture for the remaining time", "duration_seconds": 0},
                ],
            },
            # Level 2 — existing "Standing Pallof Press (Imaginary)"
            {
                "name": "Standing Pallof Press (Imaginary)",
                "benefit": "Anti-rotation core training to protect the spine under load",
                "steps": [
                    {"instruction": "Stand with feet shoulder-width apart, arms extended in front of your chest, hands clasped", "duration_seconds": 10},
                    {"instruction": "Brace your core. Slowly rotate your clasped hands to the left — resist with your trunk. Hold 5 seconds", "duration_seconds": 15},
                    {"instruction": "Return to centre. Rotate to the right — resist with your trunk. Hold 5 seconds", "duration_seconds": 15},
                    {"instruction": "Repeat: left hold 5s, centre, right hold 5s. Focus on keeping hips square", "duration_seconds": 20},
                    {"instruction": "Walk with engaged core, feeling your obliques activated, for the remaining time", "duration_seconds": 0},
                ],
            },
            # Level 3 — new
            {
                "name": "Thoracic Rotation Walk",
                "benefit": "Mobilizes the thoracic spine to reduce compensatory lumbar movement",
                "steps": [
                    {"instruction": "Walk slowly. Place hands behind your head, elbows wide", "duration_seconds": 15},
                    {"instruction": "With each step, rotate your upper body toward the leading leg. 10 steps", "duration_seconds": 25},
                    {"instruction": "Stop. Feet planted, rotate as far as comfortable to the left — hold 10 seconds", "duration_seconds": 15},
                    {"instruction": "Rotate to the right — hold 10 seconds", "duration_seconds": 15},
                    {"instruction": "Resume walking with gentle rotations for the remaining time", "duration_seconds": 0},
                ],
            },
            # Level 4 — new
            {
                "name": "Farmer's Walk",
                "benefit": "Builds grip, core, and postural endurance under load",
                "steps": [
                    {"instruction": "Pick up two heavy-ish objects (water bottles, books). Hold at your sides", "duration_seconds": 10},
                    {"instruction": "Walk with perfect posture: shoulders back and down, core braced, chin tucked", "duration_seconds": 30},
                    {"instruction": "Set down the weights. Shake out your arms. Rest 15 seconds", "duration_seconds": 15},
                    {"instruction": "Pick up again. Walk another 30 seconds — focus on not leaning to either side", "duration_seconds": 30},
                    {"instruction": "Set down and walk freely for the remaining time", "duration_seconds": 0},
                ],
            },
        ],
    },
}

LIE_DOWN_TRACKS = {
    "decompression": {
        "name": "Decompression",
        "focus": "Spinal relief",
        "routines": [
            # Level 1 — existing "90-90 Spinal Decompression"
            # (copy existing routine dict)
            # Level 2 — existing "Supine Relaxation & Breathing"
            # Level 3 — existing "Gentle Knee-to-Chest Stretch"
            # Level 4 — existing "Prone Press-Up Sequence"
        ],
    },
    "core_stability": {
        "name": "Core Stability",
        "focus": "Deep core",
        "routines": [
            # Level 1 — existing "Dead Bug Anti-Extension"
            # Level 2 — existing "Bird-Dog Core Stability"
            # Level 3 — existing "Side Plank Progression"
            # Level 4 — new "Hollow Body Hold"
        ],
    },
    "hip_glute": {
        "name": "Hip & Glute",
        "focus": "Posterior chain",
        "routines": [
            # Level 1 — existing "Clamshells & Hip Strengthening"
            # Level 2 — existing "Glute Bridge Progression"
            # Level 3 — existing "Side-Lying Hip Abduction Series"
            # Level 4 — new "Single-Leg Bridge"
        ],
    },
}
```

Also add any new routines that don't exist yet (Wall Press-Ups, Standing Back Bends, Dynamic Extension Walk, Walking Lunges, Thoracic Rotation Walk, Farmer's Walk, Hollow Body Hold, Single-Leg Bridge). Use the same `{"name", "benefit", "steps": [...]}` format.

**Step 2: Add breathing exercise data**

```python
BREATHING_EXERCISES = [
    {
        "name": "Box Breathing",
        "phases": [
            {"label": "Inhale", "seconds": 4},
            {"label": "Hold", "seconds": 4},
            {"label": "Exhale", "seconds": 4},
            {"label": "Hold", "seconds": 4},
        ],
    },
    {
        "name": "4-7-8 Relaxation",
        "phases": [
            {"label": "Inhale", "seconds": 4},
            {"label": "Hold", "seconds": 7},
            {"label": "Exhale", "seconds": 8},
        ],
    },
    {
        "name": "Diaphragmatic Breathing",
        "phases": [
            {"label": "Inhale deeply", "seconds": 5},
            {"label": "Exhale slowly", "seconds": 7},
        ],
    },
]
```

**Step 3: Update accessor functions**

Keep existing `get_walk_routine()` and `get_lie_down_routine()` working as fallbacks (return a random routine from all tracks), but add new functions:

```python
def get_track_routine(tracks: dict, track_id: str, level: int) -> dict | None:
    """Get the routine for a specific track and level (0-indexed)."""
    track = tracks.get(track_id)
    if not track:
        return None
    routines = track["routines"]
    if level < 0 or level >= len(routines):
        return None
    return routines[level]

def get_track_names(tracks: dict) -> list[tuple[str, str]]:
    """Get list of (track_id, display_name) tuples."""
    return [(tid, t["name"]) for tid, t in tracks.items()]

def get_breathing_exercise() -> dict:
    """Get a random breathing exercise."""
    return random.choice(BREATHING_EXERCISES)
```

**Step 4: Verify**

Run: `python3 -c "from spineguard import tips; print(tips.WALK_TRACKS.keys()); print(tips.get_breathing_exercise()['name'])"`
Expected: `dict_keys(['spinal_extension', 'lower_body', 'posture'])` and a breathing exercise name.

**Step 5: Commit**

```bash
git add spineguard/tips.py
git commit -m "feat: reorganize routines into tracks with levels and add breathing exercises"
```

---

### Task 2: Add routine progress management (routines.py)

**Files:**
- Create: `spineguard/routines.py`

**Step 1: Create the RoutineProgress class**

This class manages track state, daily rotation, level progression, and streak tracking. It reads/writes to `state.json` alongside existing state.

```python
"""Routine progression and streak tracking for SpineGuard."""

import json
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from . import tips

STATE_DIR = Path.home() / ".local" / "share" / "spineguard"
STATE_FILE = STATE_DIR / "state.json"

# Daily rotation: day-of-week (0=Mon) maps to track index
ROTATION = [0, 1, 2, 0, 1, 2, 0]  # Mon=0, Tue=1, Wed=2, Thu=0, ...

COMPLETIONS_TO_LEVEL_UP = 5


class RoutineProgress:
    """Manages routine track progression and streak tracking."""

    def __init__(self):
        self._progress: dict = {}  # {"walk_spinal_extension": {"level": 0, "completions": 0}, ...}
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
            # Check if yesterday was the last active date
            yesterday = (date.today().replace(day=date.today().day) - __import__("datetime").timedelta(days=1)).isoformat()
            if self._streak.get("last_date") != yesterday:
                # Streak broken (missed a day)
                self._streak["current"] = 0
            self._streak["skipped_today"] = False
        return self._streak.get("current", 0)

    def record_day_completion(self):
        """Mark today as a completed day (call at end of day or on each break completion)."""
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
```

**Step 2: Verify**

Run: `python3 -c "from spineguard.routines import RoutineProgress; rp = RoutineProgress(); print(rp.get_streak())"`
Expected: `0` (no streak data yet)

**Step 3: Commit**

```bash
git add spineguard/routines.py
git commit -m "feat: add routine progress management with tracks, levels, and streaks"
```

---

### Task 3: Add config keys (config.py)

**Files:**
- Modify: `spineguard/config.py`

**Step 1: Add new defaults**

Add these keys to the `DEFAULTS` dict after `"physio_minute": 0`:

```python
    "breathing_enabled": True,
    "breathing_frequency": 3,
    "eye_rest_enabled": True,
    "eye_rest_interval_minutes": 20,
    "routine_mode": "auto",
    "pinned_walk_track": None,
    "pinned_lie_down_track": None,
```

**Step 2: Verify**

Run: `python3 -c "from spineguard.config import Config; c = Config(); print(c.get('breathing_enabled'), c.get('eye_rest_interval_minutes'), c.get('routine_mode'))"`
Expected: `True 20 auto`

**Step 3: Commit**

```bash
git add spineguard/config.py
git commit -m "feat: add config keys for breathing, eye rest, and routine mode"
```

---

### Task 4: Add breathing and eye rest timers (timers.py)

**Files:**
- Modify: `spineguard/timers.py`

**Step 1: Add BreakType constants**

Add to the `BreakType` class:

```python
    BREATHING = "breathing"
    EYE_REST = "eye_rest"
```

**Step 2: Add timer fields to `__init__`**

Add after the existing position switch timer fields:

```python
        # Breathing break timer
        self._breathing_callback: Optional[Callable[[], None]] = None
        self._breathing_countdown_id: Optional[int] = None
        self._breathing_seconds_remaining: int = 0
        self._pomodoro_cycle_count: int = 0

        # Eye rest timer
        self._eye_rest_callback: Optional[Callable[[], None]] = None
        self._eye_rest_countdown_id: Optional[int] = None
        self._eye_rest_seconds_remaining: int = 0
```

**Step 3: Add callback setters**

```python
    def set_breathing_callback(self, callback: Callable[[], None]):
        """Set callback for breathing break reminders."""
        self._breathing_callback = callback

    def set_eye_rest_callback(self, callback: Callable[[], None]):
        """Set callback for eye rest micro-breaks."""
        self._eye_rest_callback = callback
```

**Step 4: Add breathing timer methods**

```python
    # --- Breathing timer ---

    def _start_breathing_timer(self):
        """Start the breathing break countdown based on pomodoro cycle count."""
        if self._breathing_countdown_id:
            GLib.source_remove(self._breathing_countdown_id)
            self._breathing_countdown_id = None

    def _check_breathing_break(self):
        """Check if a breathing break should trigger after a pomodoro cycle."""
        if not self._config.get("breathing_enabled"):
            return
        freq = self._config.get("breathing_frequency")
        if freq and self._pomodoro_cycle_count > 0 and self._pomodoro_cycle_count % freq == 0:
            if self._breathing_callback:
                self._breathing_callback()

    def get_breathing_seconds_remaining(self) -> int:
        return self._breathing_seconds_remaining
```

**Step 5: Add eye rest timer methods**

```python
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
        if self._eye_rest_countdown_id:
            GLib.source_remove(self._eye_rest_countdown_id)
            self._eye_rest_countdown_id = None
        self._eye_rest_seconds_remaining = 0

    def _eye_rest_tick(self) -> bool:
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
```

**Step 6: Update `start()` and `stop()`**

In `start()`, add after the physio/position timer starts:
```python
        self._start_eye_rest_timer()
```

In `stop()`, add:
```python
        self._stop_eye_rest_timer()
```

**Step 7: Track pomodoro cycles**

In `break_completed()`, increment the cycle counter and check for breathing break:
```python
    def break_completed(self):
        """Called when a break is completed. Alternates break type and resets timer."""
        self._pomodoro_cycle_count += 1
        self._alternate_break_type()
        self.reset_pomodoro()
        self._check_breathing_break()
```

**Step 8: Update `_on_config_change`**

Add handling for `eye_rest_enabled` and `breathing_enabled`:
```python
        elif key == "eye_rest_enabled":
            if value:
                self._start_eye_rest_timer()
            else:
                self._stop_eye_rest_timer()
```

**Step 9: Verify**

Run: `python3 -c "from spineguard.config import Config; from spineguard.timers import TimerManager, BreakType; print(BreakType.BREATHING, BreakType.EYE_REST)"`
Expected: `breathing eye_rest`

**Step 10: Commit**

```bash
git add spineguard/timers.py
git commit -m "feat: add breathing and eye rest timers to TimerManager"
```

---

### Task 5: Create micro-break overlay (micro_overlay.py)

**Files:**
- Create: `spineguard/micro_overlay.py`

**Step 1: Write the MicroBreakOverlay class**

```python
"""Lightweight micro-break overlay for SpineGuard (eye rest, etc.)."""

from typing import Callable, Optional

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")

from gi.repository import Gdk, GLib, Gtk


class MicroBreakOverlay(Gtk.Window):
    """Small centered popup for brief micro-breaks (e.g., 20-second eye rest)."""

    def __init__(
        self,
        message: str,
        duration_seconds: int,
        on_complete: Callable[[], None],
    ):
        super().__init__()

        self._duration_seconds = duration_seconds
        self._seconds_remaining = duration_seconds
        self._on_complete = on_complete
        self._timer_id: Optional[int] = None

        self.set_title("SpineGuard")
        self.set_default_size(400, 200)
        self.set_resizable(False)
        self.set_decorated(False)
        self.set_deletable(False)
        if hasattr(self, "set_keep_above"):
            self.set_keep_above(True)
        self.add_css_class("micro-break-overlay")

        # Center the window
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)

        # Build UI
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)
        box.set_margin_top(30)
        box.set_margin_bottom(30)
        box.set_margin_start(30)
        box.set_margin_end(30)

        icon_label = Gtk.Label(label="\U0001f440")  # 👀
        icon_label.add_css_class("micro-break-icon")
        box.append(icon_label)

        msg_label = Gtk.Label(label=message)
        msg_label.add_css_class("micro-break-message")
        msg_label.set_wrap(True)
        msg_label.set_justify(Gtk.Justification.CENTER)
        box.append(msg_label)

        self._countdown_label = Gtk.Label(label=f"{duration_seconds}s")
        self._countdown_label.add_css_class("micro-break-countdown")
        box.append(self._countdown_label)

        self.set_child(box)

        self.connect("realize", self._on_realize)
        self._timer_id = GLib.timeout_add_seconds(1, self._tick)

    def _on_realize(self, widget):
        try:
            surface = self.get_surface()
            if surface and hasattr(surface, "set_keep_above"):
                surface.set_keep_above(True)
        except Exception:
            pass

    def _tick(self) -> bool:
        self._seconds_remaining -= 1
        if self._seconds_remaining <= 0:
            self.close()
            self._on_complete()
            return False
        self._countdown_label.set_text(f"{self._seconds_remaining}s")
        return True

    def close(self):
        if self._timer_id:
            GLib.source_remove(self._timer_id)
            self._timer_id = None
        super().close()
```

**Step 2: Verify**

Run: `python3 -c "from spineguard.micro_overlay import MicroBreakOverlay; print('import ok')"`
Expected: `import ok`

**Step 3: Commit**

```bash
git add spineguard/micro_overlay.py
git commit -m "feat: add MicroBreakOverlay for eye rest micro-breaks"
```

---

### Task 6: Add breathing animation mode to BreakOverlay (overlay.py)

**Files:**
- Modify: `spineguard/overlay.py`

**Step 1: Add BreakType.BREATHING to imports and add new constructor parameters**

The overlay needs to accept:
- `track_info`: optional dict with `{"track_name": str, "level": int, "completions": int, "max_level": int}` for showing progression
- `streak`: optional int for showing streak count
- `breathing_exercise`: optional dict for breathing mode

Add these to `__init__` signature and store them:
```python
    def __init__(
        self,
        break_type: str,
        duration_minutes: Optional[int],
        on_complete: Callable[[], None],
        on_skip: Callable[[], None],
        sound_player=None,
        context: Optional[dict] = None,
        on_done_early: Optional[Callable[[], None]] = None,
        monitor: Optional[Gdk.Monitor] = None,
        track_info: Optional[dict] = None,
        streak: int = 0,
        breathing_exercise: Optional[dict] = None,
    ):
```

Store them:
```python
        self._track_info = track_info
        self._streak = streak
        self._breathing_exercise = breathing_exercise
        self._breath_phase_index = 0
        self._breath_phase_elapsed = 0
        self._breath_circle_scale = 0.3  # 0.3 = exhaled, 1.0 = inhaled
```

**Step 2: Add breathing case to `_build_ui`**

Add a new branch for `BreakType.BREATHING` in `_build_ui` (before the walk/lie-down branches):

```python
        if self._break_type == BreakType.BREATHING:
            header_text = "Breathing Exercise"
            header_icon = "\U0001f32c\ufe0f"  # 🌬️
            instruction = self._breathing_exercise["name"] if self._breathing_exercise else "Breathe deeply"
```

For breathing mode, replace the countdown drawing area with a breathing circle drawing area and add the phase label:

```python
        if self._break_type == BreakType.BREATHING and self._breathing_exercise:
            # Breathing circle instead of countdown
            self._breath_drawing = Gtk.DrawingArea()
            self._breath_drawing.set_size_request(250, 250)
            self._breath_drawing.set_draw_func(self._draw_breathing_circle)
            main_box.append(self._breath_drawing)

            # Phase label
            first_phase = self._breathing_exercise["phases"][0]
            self._phase_label = Gtk.Label(label=f"{first_phase['label']}...")
            self._phase_label.add_css_class("breathing-phase-label")
            main_box.append(self._phase_label)
        else:
            # Existing countdown drawing area code
            ...
```

**Step 3: Add track info bar**

After the instruction label, before the countdown area, add track info if provided:

```python
        if self._track_info:
            ti = self._track_info
            track_text = f"{ti['track_name']} — Level {ti['level'] + 1}/{ti['max_level'] + 1} ({ti['completions']}/{5})"
            track_label = Gtk.Label(label=track_text)
            track_label.add_css_class("track-info-label")
            main_box.append(track_label)
```

**Step 4: Add streak display**

After the button box, add:

```python
        if self._streak > 0:
            streak_label = Gtk.Label(label=f"\U0001f525 {self._streak}-day streak")
            streak_label.add_css_class("streak-label")
            streak_label.set_halign(Gtk.Align.CENTER)
            streak_label.set_margin_top(20)
            main_box.append(streak_label)
```

**Step 5: Add breathing circle draw function**

```python
    def _draw_breathing_circle(self, area, cr, width, height):
        """Draw the animated breathing circle."""
        import math
        cx = width / 2
        cy = height / 2
        max_radius = min(width, height) / 2 - 20
        radius = max_radius * self._breath_circle_scale

        # Outer guide ring
        cr.set_source_rgba(0.2, 0.3, 0.35, 0.3)
        cr.arc(cx, cy, max_radius, 0, 2 * math.pi)
        cr.stroke()

        # Breathing circle
        phase = self._get_current_breath_phase()
        if phase and phase["label"].lower().startswith("inhale"):
            cr.set_source_rgba(0.3, 0.6, 0.9, 0.6)  # Cool blue
        elif phase and phase["label"].lower().startswith("exhale"):
            cr.set_source_rgba(0.9, 0.5, 0.3, 0.6)  # Warm
        else:
            cr.set_source_rgba(0.4, 0.7, 0.7, 0.6)  # Teal for hold
        cr.arc(cx, cy, radius, 0, 2 * math.pi)
        cr.fill()

    def _get_current_breath_phase(self):
        if not self._breathing_exercise:
            return None
        phases = self._breathing_exercise["phases"]
        if self._breath_phase_index < len(phases):
            return phases[self._breath_phase_index]
        return None
```

**Step 6: Update `_tick` for breathing animation**

Add breathing phase advancement to `_tick` (for breathing break type):

```python
        # Advance breathing phases
        if self._break_type == BreakType.BREATHING and self._breathing_exercise:
            self._breath_phase_elapsed += 1
            phases = self._breathing_exercise["phases"]
            if self._breath_phase_index < len(phases):
                current_phase = phases[self._breath_phase_index]
                # Animate circle scale
                phase_progress = self._breath_phase_elapsed / current_phase["seconds"]
                label = current_phase["label"].lower()
                if "inhale" in label:
                    self._breath_circle_scale = 0.3 + 0.7 * min(phase_progress, 1.0)
                elif "exhale" in label:
                    self._breath_circle_scale = 1.0 - 0.7 * min(phase_progress, 1.0)
                # else hold: keep current scale

                if self._breath_phase_elapsed >= current_phase["seconds"]:
                    self._breath_phase_index = (self._breath_phase_index + 1) % len(phases)
                    self._breath_phase_elapsed = 0
                    next_phase = phases[self._breath_phase_index]
                    remaining = self._seconds_remaining
                    count = current_phase["seconds"]
                    self._phase_label.set_text(f"{next_phase['label']}... {next_phase['seconds']}s")

            if hasattr(self, "_breath_drawing"):
                self._breath_drawing.queue_draw()
```

**Step 7: Verify**

Run: `python3 -c "from spineguard.overlay import BreakOverlay; print('import ok')"`
Expected: `import ok`

**Step 8: Commit**

```bash
git add spineguard/overlay.py
git commit -m "feat: add breathing animation mode, track info, and streak display to overlay"
```

---

### Task 7: Update stats tracking (stats.py)

**Files:**
- Modify: `spineguard/stats.py`

**Step 1: Add new break types to metadata**

Add to `_BREAK_META`:

```python
    "breathing":       {"icon": "\U0001f32c\ufe0f", "name": "Breathing Breaks"},
    "eye_rest":        {"icon": "\U0001f440", "name": "Eye Rest Breaks"},
```

**Step 2: Update breakdown loop**

In `_render_period`, add `"breathing"` and `"eye_rest"` to the breakdown loop:

```python
            for break_type in ("walk", "lie_down", "position_switch", "breathing", "eye_rest"):
```

**Step 3: Commit**

```bash
git add spineguard/stats.py
git commit -m "feat: add breathing and eye rest break types to statistics"
```

---

### Task 8: Add CSS styles for new components (style.css)

**Files:**
- Modify: `spineguard/style.css`

**Step 1: Add new styles**

Append these styles after the existing `.position-switch .health-tip` block (around line 102):

```css
/* Track info bar */
.track-info-label {
    font-size: 15px;
    font-weight: 500;
    color: #3a9cc5;
    padding: 8px 16px;
    background-color: rgba(58, 156, 197, 0.08);
    border-radius: 8px;
    letter-spacing: 0.3px;
}

/* Streak counter */
.streak-label {
    font-size: 16px;
    font-weight: 500;
    color: #e8b84a;
    letter-spacing: 0.3px;
}

/* Breathing phase label */
.breathing-phase-label {
    font-size: 24px;
    font-weight: 400;
    color: #8a9bb0;
    margin-top: 10px;
}

/* Micro-break overlay */
.micro-break-overlay {
    background-color: rgba(11, 22, 34, 0.92);
    border-radius: 20px;
    border: 1px solid rgba(58, 156, 197, 0.15);
    box-shadow: 0 8px 40px rgba(0, 0, 0, 0.6);
}

.micro-break-icon {
    font-size: 48px;
}

.micro-break-message {
    font-size: 20px;
    font-weight: 500;
    color: #e4eef5;
}

.micro-break-countdown {
    font-size: 36px;
    font-weight: 700;
    color: #3a9cc5;
}

/* Level-up flash */
.level-up-label {
    font-size: 28px;
    font-weight: 800;
    color: #45d48a;
    animation: fadeIn 300ms ease-out;
}
```

**Step 2: Commit**

```bash
git add spineguard/style.css
git commit -m "feat: add CSS styles for track info, streak, breathing, and micro-break overlay"
```

---

### Task 9: Update settings dialog (settings.py)

**Files:**
- Modify: `spineguard/settings.py`

**Step 1: Add Routines page to settings**

In `_build_ui`, add a fourth page:

```python
        stack.add_titled(self._build_routines_page(), "routines", "Routines")
```

**Step 2: Add breathing and eye rest settings to Timers page**

In `_build_timers_page`, add a new section after the Sit-Stand Desk section:

```python
        # Breathing & Eye Rest section
        page.append(self._section_header("EXTRA BREAKS"))

        card4 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        card4.add_css_class("panel-card")
        card4.set_margin_bottom(20)

        breathing_switch = Gtk.Switch()
        breathing_switch.set_active(self._config.get("breathing_enabled"))
        breathing_switch.connect("notify::active", lambda s, _: self._config.set("breathing_enabled", s.get_active()))
        breathing_switch.set_valign(Gtk.Align.CENTER)

        card4.append(self._setting_row(
            "Breathing exercises", "Short breathing breaks between pomodoro cycles",
            breathing_switch,
        ))
        card4.append(self._thin_divider())
        card4.append(self._setting_row(
            "Breathing frequency", "Trigger every N pomodoro cycles",
            self._make_spin(self._config.get("breathing_frequency"), 1, 10, "breathing_frequency"),
        ))
        card4.append(self._thin_divider())

        eye_rest_switch = Gtk.Switch()
        eye_rest_switch.set_active(self._config.get("eye_rest_enabled"))
        eye_rest_switch.connect("notify::active", lambda s, _: self._config.set("eye_rest_enabled", s.get_active()))
        eye_rest_switch.set_valign(Gtk.Align.CENTER)

        card4.append(self._setting_row(
            "Eye rest micro-breaks", "20-20-20 rule: brief popup every N minutes",
            eye_rest_switch,
        ))
        card4.append(self._thin_divider())
        card4.append(self._setting_row(
            "Eye rest interval", "Minutes between eye rest reminders",
            self._make_spin(self._config.get("eye_rest_interval_minutes"), 5, 60, "eye_rest_interval_minutes"),
        ))

        page.append(card4)
```

**Step 3: Build the Routines page**

```python
    def _build_routines_page(self) -> Gtk.Widget:
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        page.set_margin_top(28)
        page.set_margin_bottom(28)
        page.set_margin_start(28)
        page.set_margin_end(28)

        page.append(self._page_header("Routines", "Manage exercise track rotation and progression"))

        # Rotation mode
        page.append(self._section_header("TRACK ROTATION"))

        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        card.add_css_class("panel-card")
        card.set_margin_bottom(20)

        mode_dropdown = Gtk.DropDown.new_from_strings(["Auto-rotate daily", "Manual selection"])
        current_mode = 1 if self._config.get("routine_mode") == "manual" else 0
        mode_dropdown.set_selected(current_mode)
        mode_dropdown.connect("notify::selected", lambda d, _: self._config.set(
            "routine_mode", "manual" if d.get_selected() == 1 else "auto"
        ))

        card.append(self._setting_row(
            "Rotation mode", "How tracks are selected each day",
            mode_dropdown,
        ))

        page.append(card)

        # Pinned tracks (only relevant in manual mode)
        page.append(self._section_header("PINNED TRACKS"))

        from . import tips

        pin_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        pin_card.add_css_class("panel-card")
        pin_card.set_margin_bottom(20)

        walk_names = ["Auto"] + [t["name"] for t in tips.WALK_TRACKS.values()]
        walk_ids = [None] + list(tips.WALK_TRACKS.keys())
        walk_dropdown = Gtk.DropDown.new_from_strings(walk_names)
        current_pin = self._config.get("pinned_walk_track")
        if current_pin in walk_ids:
            walk_dropdown.set_selected(walk_ids.index(current_pin))
        walk_dropdown.connect("notify::selected", lambda d, _: self._config.set(
            "pinned_walk_track", walk_ids[d.get_selected()] if d.get_selected() > 0 else None
        ))

        pin_card.append(self._setting_row(
            "Walk track", "Pin a specific walk track",
            walk_dropdown,
        ))
        pin_card.append(self._thin_divider())

        ld_names = ["Auto"] + [t["name"] for t in tips.LIE_DOWN_TRACKS.values()]
        ld_ids = [None] + list(tips.LIE_DOWN_TRACKS.keys())
        ld_dropdown = Gtk.DropDown.new_from_strings(ld_names)
        current_ld_pin = self._config.get("pinned_lie_down_track")
        if current_ld_pin in ld_ids:
            ld_dropdown.set_selected(ld_ids.index(current_ld_pin))
        ld_dropdown.connect("notify::selected", lambda d, _: self._config.set(
            "pinned_lie_down_track", ld_ids[d.get_selected()] if d.get_selected() > 0 else None
        ))

        pin_card.append(self._setting_row(
            "Lie-down track", "Pin a specific lie-down track",
            ld_dropdown,
        ))

        page.append(pin_card)

        # Reset progress
        page.append(self._section_header("PROGRESS"))

        reset_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        reset_card.add_css_class("panel-card")
        reset_card.set_margin_bottom(20)

        reset_btn = Gtk.Button(label="Reset All Progress")
        reset_btn.add_css_class("skip-button")
        reset_btn.connect("clicked", self._on_reset_progress)

        reset_card.append(self._setting_row(
            "Reset progress", "Clear all track levels and completions",
            reset_btn,
        ))

        page.append(reset_card)

        scrolled.set_child(page)
        return scrolled

    def _on_reset_progress(self, button):
        """Reset all routine progress after confirmation."""
        from .routines import RoutineProgress
        rp = RoutineProgress()
        rp.reset_progress()
```

**Step 4: Verify**

Run: `python3 -c "from spineguard.settings import SettingsDialog; print('import ok')"`
Expected: `import ok`

**Step 5: Commit**

```bash
git add spineguard/settings.py
git commit -m "feat: add Routines page and breathing/eye rest toggles to settings"
```

---

### Task 10: Wire everything together in app.py

**Files:**
- Modify: `spineguard/app.py`

**Step 1: Add imports**

```python
from .micro_overlay import MicroBreakOverlay
from .routines import RoutineProgress
```

**Step 2: Add new instance variables to `__init__`**

```python
        self._routine_progress: Optional[RoutineProgress] = None
        self._current_micro_overlay: Optional[MicroBreakOverlay] = None
```

**Step 3: Initialize in `do_activate`**

After `self._stats_manager = StatsManager()`, add:
```python
        self._routine_progress = RoutineProgress()
```

**Step 4: Set up new timer callbacks**

After the existing callback wiring, add:
```python
        self._timer_manager.set_breathing_callback(self._on_breathing_break)
        self._timer_manager.set_eye_rest_callback(self._on_eye_rest)
```

**Step 5: Add breathing break handler**

```python
    def _on_breathing_break(self):
        """Called when a breathing break should trigger."""
        if self._current_overlay:
            return

        from . import tips
        exercise = tips.get_breathing_exercise()

        self._sound_player.play_break_start()

        self._show_break_overlay(
            break_type=BreakType.BREATHING,
            duration=2,  # 2 minutes
            on_complete=self._on_breathing_complete,
            on_skip=self._on_breathing_skipped,
            on_done_early=self._on_breathing_done_early,
            context={"breathing_exercise": exercise},
        )

    def _on_breathing_complete(self):
        bt = self._current_break_type
        self._close_blocking_overlays()
        self._current_overlay = None
        self._current_break_type = None
        if bt:
            self._stats_manager.log_break_completed(bt)

    def _on_breathing_done_early(self):
        bt = self._current_break_type
        self._close_blocking_overlays()
        self._current_overlay = None
        self._current_break_type = None
        if bt:
            self._stats_manager.log_break_done_early(bt)

    def _on_breathing_skipped(self):
        bt = self._current_break_type
        self._close_blocking_overlays()
        self._current_overlay = None
        self._current_break_type = None
        if bt:
            self._stats_manager.log_break_skipped(bt)
```

**Step 6: Add eye rest handler**

```python
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
        self._current_micro_overlay = None
        self._stats_manager.log_break_completed(BreakType.EYE_REST)
```

**Step 7: Update `_show_break_overlay` to pass track info, streak, and breathing data**

Modify `_show_break_overlay` to compute track info and pass it to `BreakOverlay`:

```python
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
```

**Step 8: Update break completion to record routine progress and streak**

In `_on_break_complete`, after logging stats, add:
```python
        if bt in (BreakType.WALK, BreakType.LIE_DOWN) and self._routine_progress:
            from . import tips
            tracks = tips.WALK_TRACKS if bt == BreakType.WALK else tips.LIE_DOWN_TRACKS
            pinned_key = "pinned_walk_track" if bt == BreakType.WALK else "pinned_lie_down_track"
            pinned = self._config.get(pinned_key) if self._config.get("routine_mode") == "manual" else None
            track_id = self._routine_progress.get_today_track_id(tracks, pinned)
            self._routine_progress.record_completion(track_id, tracks)
        if self._routine_progress:
            self._routine_progress.record_day_completion()
```

Similarly update `_on_break_done_early` to also call `record_day_completion()`.

In `_on_break_skipped`, add:
```python
        if self._routine_progress:
            self._routine_progress.record_skip()
```

**Step 9: Update overlay to use track routine instead of random**

In `BreakOverlay._build_ui` (overlay.py), modify the routine selection logic so that when a `context["routine"]` is provided, it uses that instead of calling `tips.get_walk_routine()` / `tips.get_lie_down_routine()`:

```python
            if use_routine:
                if "routine" in self._context:
                    self._routine = self._context["routine"]
                elif self._break_type == BreakType.WALK:
                    self._routine = tips.get_walk_routine()
                else:
                    self._routine = tips.get_lie_down_routine()
```

**Step 10: Verify**

Run: `python3 -c "from spineguard.app import SpineGuardApp; print('import ok')"`
Expected: `import ok`

**Step 11: Commit**

```bash
git add spineguard/app.py spineguard/overlay.py
git commit -m "feat: wire up progressive routines, breathing breaks, eye rest, and streak tracking"
```

---

### Task 11: Manual integration test

**Step 1: Run the app**

```bash
python3 -m spineguard.app
```

**Step 2: Test checklist**

- [ ] App starts without errors
- [ ] System tray appears
- [ ] Settings → Routines page shows track rotation, pinned track dropdowns, reset button
- [ ] Settings → Timers page shows breathing and eye rest toggles
- [ ] Take Break Now → overlay shows track info bar (e.g., "Spinal Extension — Level 1/4 (0/5)")
- [ ] Overlay shows streak counter (0-day streak on first run)
- [ ] Exercise routine follows track progression (Level 1 routine for new tracks)
- [ ] After eye rest interval (set to 1 min for testing), micro-break popup appears and auto-closes after 20s
- [ ] Stats window shows breathing and eye rest in breakdown
- [ ] Config changes for breathing/eye rest toggles take effect immediately

**Step 3: Fix any issues found**

**Step 4: Final commit with any fixes**

```bash
git add -A
git commit -m "fix: address integration test findings"
```
