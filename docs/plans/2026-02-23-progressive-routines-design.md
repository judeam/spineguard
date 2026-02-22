# Progressive Routines + Break Variety Design

## Problem

Breaks feel repetitive. Users comply but mentally disengage because the same overlays, tips, and routines appear without any sense of progress or novelty.

## Solution

Two complementary changes:

1. **Progressive routine system** - Replace random routine selection with structured tracks that users level through
2. **New break types** - Add breathing exercises and eye rest micro-breaks for variety

---

## 1. Routine Track System

### Walk Tracks

| Track | Focus | Routines (easy to hard) |
|-------|-------|------------------------|
| Spinal Extension | McKenzie method | Standing Extensions, Wall Press-Ups, Standing Back Bends, Dynamic Extension Walk |
| Lower Body | Glute/leg activation | Gentle Walking Stretch, Single-Leg Balance, Wall Sit, Walking Lunges |
| Posture | Alignment | Posture Reset Walk, Standing Pallof Press, Thoracic Rotation Walk, Farmer's Walk |

### Lie-Down Tracks

| Track | Focus | Routines (easy to hard) |
|-------|-------|------------------------|
| Decompression | Spinal relief | 90-90 Decompression, Supine Breathing, Knee-to-Chest, Prone Press-Up Sequence |
| Core Stability | Deep core | Dead Bug, Bird-Dog, Side Plank Progression, Hollow Body Hold |
| Hip & Glute | Posterior chain | Clamshells, Glute Bridge, Hip Abduction, Single-Leg Bridge |

### Progression Rules

- Start at Level 1 of each track
- After 5 completions of a routine, the next level unlocks
- Overlay shows track name, current level, completions toward next unlock (e.g., "3/5")
- Tracks rotate daily (Mon = Spinal Extension + Decompression, Tue = Lower Body + Core Stability, etc.)
- Users can pin a favorite track to override rotation

### Data Model

Added to `state.json`:

```json
{
  "routine_progress": {
    "walk_spinal_extension": {"level": 2, "completions": 3},
    "walk_lower_body": {"level": 1, "completions": 5}
  }
}
```

---

## 2. New Break Types

### Breathing Exercise Breaks (2 min)

- Inserted as a short break between pomodoro cycles, not replacing walk/lie-down
- Frequency: once every 3 pomodoro cycles (configurable)
- Animated breathing guide: circle expands on inhale, contracts on exhale
- Three rotating techniques: Box breathing (4-4-4-4), 4-7-8 relaxation, Diaphragmatic breathing
- Background color subtly shifts (cool blue inhale, warm exhale) via CSS

### Eye Rest Micro-Breaks (20 seconds)

- Based on the 20-20-20 rule
- Triggers every 20 minutes
- Small centered window (400x200px), not full-screen
- Auto-dismisses when done, no buttons
- Semi-transparent dark background
- Can be disabled independently

---

## 3. Overlay UI Changes

### Existing Overlay Modifications

- Track info bar below header: "Core Stability - Level 2 (3/5)"
- Level-up animation on unlock: text scale-up + color flash
- Streak counter in bottom corner: small "12-day streak" text

### Breathing Overlay Mode

- Reuses BreakOverlay, replaces countdown with animated breathing circle
- Circle smoothly scales between small (exhale) and large (inhale) at ~30ms intervals
- Phase text: "Inhale... 2... 3... 4"
- Subtle background color shifts

### Micro-Break Overlay (Eye Rest)

- New MicroBreakOverlay class - small centered dialog (400x200px)
- 20-second countdown text, auto-closes
- Semi-transparent background

### Streak Tracking

- Added to `state.json`: `"streak": {"current": 12, "last_date": "2026-02-23"}`
- Day counts toward streak if zero breaks were skipped
- Resets on any full skip (not "done early")

---

## 4. Configuration

### New Config Keys

```json
{
  "breathing_enabled": true,
  "breathing_frequency": 3,
  "eye_rest_enabled": true,
  "eye_rest_interval_minutes": 20,
  "routine_mode": "auto",
  "pinned_walk_track": null,
  "pinned_lie_down_track": null
}
```

### Settings UI

- New "Routines" page (page 4): track rotation mode, pinned track dropdowns, reset/view progress
- Timers page: breathing toggle + frequency, eye rest toggle + interval

---

## 5. Files Changed

| File | Changes |
|------|---------|
| tips.py | Reorganize routines into tracks with difficulty levels; add breathing content |
| timers.py | New breathing timer, eye rest timer; track completion counting |
| overlay.py | Track info bar, level-up animation, streak display, breathing animation mode |
| micro_overlay.py (new) | Lightweight 20-second popup for eye rest |
| config.py | 6 new config keys |
| settings.py | New Routines page; breathing/eye rest toggles |
| state.json | routine_progress dict, streak tracking |
| stats.py | Track breathing and eye rest completions |
| app.py | Wire up new timers and overlays |
