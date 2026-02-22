# Contributing to SpineGuard

Thanks for your interest in contributing to SpineGuard!

## Development Setup

### System Dependencies

**Debian/Ubuntu:**
```bash
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-gsound-1.0 gir1.2-appindicator3-0.1
```

**Arch Linux:**
```bash
sudo pacman -S python-gobject gtk4 gsound libappindicator-gtk3
```

### Running from Source

No build step or virtual environment is needed. All dependencies are system packages.

```bash
git clone https://github.com/judeam/spineguard.git
cd spineguard
python3 -m spineguard.app
```

## Architecture Notes

### GTK3/GTK4 Split

The main application uses **GTK4**, but the system tray requires **GTK3** (AppIndicator3). These cannot coexist in one process, so the app spawns `tray_subprocess.py` as a separate GTK3 process. The two processes communicate via bidirectional JSON messages over Unix domain sockets.

If your change touches the tray icon, test with both the main app and the subprocess.

### GLib Event Loop

All timing uses `GLib.timeout_add_seconds` with 1-second tick callbacks. Never use `time.sleep()` or threading timers — these will block the GTK main loop and freeze the UI.

### Configuration

Settings are stored in `~/.config/spineguard/config.json`. The `Config` class in `config.py` provides a change-callback system so components react to setting changes immediately.

### State Persistence

Break alternation (walk/lie-down) and sit-stand position are saved to `~/.local/share/spineguard/state.json` so they survive restarts.

## Making Changes

1. Fork the repository and create a feature branch from `main`
2. Make your changes
3. Test manually by running `python3 -m spineguard.app`
4. Submit a pull request with a clear description of the change

### Code Style

- Follow the existing patterns in the codebase
- Wire components together using callbacks (e.g., `set_pomodoro_callback`)
- Keep the GLib event loop convention — no blocking calls

### What Needs Work

- There is no test suite yet — contributions adding tests are very welcome
- See the [Issues](https://github.com/judeam/spineguard/issues) page for open tasks

## Reporting Issues

Open an issue at https://github.com/judeam/spineguard/issues with:
- Your Linux distribution and version
- Desktop environment (GNOME, KDE, etc.)
- Steps to reproduce the problem
- Any error output from the terminal
