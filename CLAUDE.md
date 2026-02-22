# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is SpineGuard

A Linux desktop app (Python/GTK4) that enforces regular break reminders for back health. It manages multiple concurrent timers (pomodoro work cycles, water reminders, supplement checks, sit-stand position switches) and displays full-screen break overlays that cannot be dismissed early.

## Running and Installing

```bash
# Run in development (no build step needed)
python3 -m spineguard.app

# Install system-wide for current user
./install.sh

# Uninstall
./uninstall.sh
```

There is no pyproject.toml, Makefile, or test suite. Dependencies are system packages, not pip packages.

**System dependencies:** `python3-gi`, `gir1.2-gtk-4.0`, optionally `gir1.2-gsound-1.0` (sound) and `gir1.2-appindicator3-0.1` (tray icon).

## Architecture

**Entry point:** `spineguard/app.py` → `SpineGuardApp` (Gtk.Application subclass). `do_activate()` wires up all components.

**GTK3/GTK4 split:** The main app uses GTK4, but the system tray requires GTK3 (AppIndicator3). These cannot coexist in one process, so `tray.py` spawns `tray_subprocess.py` as a separate GTK3 process. They communicate via bidirectional JSON messages over Unix domain sockets (`~/.local/share/spineguard/{main,tray}.sock`).

**Timer system** (`timers.py`): All timers use `GLib.timeout_add_seconds` with 1-second tick callbacks. A single global pause state affects all timers. Timer types:
- Pomodoro (25 min) → triggers break overlay, alternating walk/lie-down
- Water reminder (60 min) → desktop notification
- Supplement check (time-of-day match) → high-priority notification
- Position switch (30 min, sit-stand mode only) → short break overlay

**Configuration** (`config.py`): JSON at `~/.config/spineguard/config.json` with defaults dict and change-callback system for reactive updates.

**State persistence** (`timers.py`): Break alternation and position state saved to `~/.local/share/spineguard/state.json`, survives restarts.

**Break overlay** (`overlay.py`): Full-screen always-on-top GTK4 window with Cairo-drawn circular countdown. Three break types: walk, lie-down, position switch.

**Notifications** (`notifications.py`): Uses `Gio.Notification`. **Sound** (`sounds.py`): Prefers GSound, falls back to `canberra-gtk-play` CLI.

## Key Conventions

- Callbacks wire components together (e.g., `set_pomodoro_callback`, `set_water_callback`)
- All timing uses GLib event loop, never `time.sleep()` or threading timers
- Tips in `tips.py` are organized by break type with random selection
- The app installs to `~/.local/share/spineguard/` with a launcher at `~/.local/bin/spineguard`
