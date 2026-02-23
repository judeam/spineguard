"""Lightweight micro-break overlay for SpineGuard (eye rest, etc.)."""

from typing import Callable, Optional

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")

from gi.repository import GLib, Gtk

from .overlay import _keep_above_on_realize


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

        # Build UI
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)
        box.set_margin_top(30)
        box.set_margin_bottom(30)
        box.set_margin_start(30)
        box.set_margin_end(30)

        icon_label = Gtk.Label(label="\U0001f440")  # eyes emoji
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

        self.connect("realize", _keep_above_on_realize)
        self._timer_id = GLib.timeout_add_seconds(1, self._tick)

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
