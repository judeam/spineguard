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

    # System sound IDs (freedesktop sound theme)
    SOUND_BREAK_START = "complete"  # A gentle completion/bell sound
    SOUND_WATER = "message"  # Message notification sound
    SOUND_SUPPLEMENT = "alarm-clock-elapsed"  # Alarm sound for supplements
    SOUND_BREAK_END = "bell"  # Bell when break ends

    def __init__(self):
        self._context: Optional[GSound.Context] = None
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

    def _play_sound_id(self, sound_id: str):
        """Play a sound by its freedesktop sound ID."""
        if not self._available:
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

    def play_break_start(self):
        """Play sound when a break starts."""
        self._play_sound_id(self.SOUND_BREAK_START)

    def play_break_end(self):
        """Play sound when a break ends."""
        self._play_sound_id(self.SOUND_BREAK_END)

    def play_water_reminder(self):
        """Play sound for water reminder."""
        self._play_sound_id(self.SOUND_WATER)

    def play_supplement_reminder(self):
        """Play sound for supplement reminder."""
        self._play_sound_id(self.SOUND_SUPPLEMENT)
