"""Sound effects for SpineGuard notifications."""

import subprocess
from typing import Optional

import gi

# Try to use GSound for playing sounds
try:
    gi.require_version("GSound", "1.0")
    from gi.repository import GSound
    HAS_GSOUND = True
except (ValueError, ImportError):
    HAS_GSOUND = False


class SoundPlayer:
    """Plays notification sounds."""

    # Default sound IDs (freedesktop sound theme)
    SOUND_BREAK_START = "complete"
    SOUND_WATER = "message"
    SOUND_SUPPLEMENT = "message"
    SOUND_BREAK_END = "bell"

    def __init__(self, config=None):
        self._config = config
        self._context = None
        self._available = False

        if HAS_GSOUND:
            try:
                self._context = GSound.Context()
                self._context.init()
                self._available = True
            except Exception as e:
                print(f"GSound init failed: {e}")

        if not self._available:
            # Check if canberra-gtk-play is available as fallback
            try:
                subprocess.run(
                    ["which", "canberra-gtk-play"],
                    capture_output=True,
                    check=True,
                )
                self._available = True
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("No sound backend available (install libgsound or libcanberra-gtk3)")

    def _get_sound(self, config_key: str, default: str) -> str:
        """Get sound ID from config, falling back to default."""
        if self._config:
            return self._config.get(config_key, default)
        return default

    def _play_sound_id(self, sound_id: str):
        """Play a sound by its freedesktop sound ID."""
        if not self._available:
            return

        # If sound_id starts with /, treat as file path
        if sound_id.startswith("/"):
            self._play_file(sound_id)
            return

        if self._context:
            try:
                self._context.play_simple({
                    GSound.ATTR_EVENT_ID: sound_id,
                    GSound.ATTR_EVENT_DESCRIPTION: "SpineGuard notification",
                })
            except Exception:
                pass
        else:
            # Fallback to canberra-gtk-play
            try:
                subprocess.Popen(
                    ["canberra-gtk-play", "-i", sound_id],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception:
                pass

    def _play_file(self, path: str):
        """Play a sound file by path."""
        if self._context:
            try:
                self._context.play_simple({
                    GSound.ATTR_MEDIA_FILENAME: path,
                    GSound.ATTR_EVENT_DESCRIPTION: "SpineGuard notification",
                })
            except Exception:
                pass
        else:
            try:
                subprocess.Popen(
                    ["canberra-gtk-play", "-f", path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception:
                pass

    def play_break_start(self):
        """Play sound when a break starts."""
        sound = self._get_sound("sound_break_start", self.SOUND_BREAK_START)
        self._play_sound_id(sound)

    def play_break_end(self):
        """Play sound when a break ends."""
        sound = self._get_sound("sound_break_end", self.SOUND_BREAK_END)
        self._play_sound_id(sound)

    def play_water_reminder(self):
        """Play sound for water reminder."""
        sound = self._get_sound("sound_water", self.SOUND_WATER)
        self._play_sound_id(sound)

    def play_supplement_reminder(self):
        """Play sound for supplement reminder."""
        sound = self._get_sound("sound_supplement", self.SOUND_SUPPLEMENT)
        self._play_sound_id(sound)
