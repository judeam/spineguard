"""Full-screen break overlay window for SpineGuard."""

import math
from typing import Callable, Optional

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")

from gi.repository import Gdk, GLib, Gtk

from . import tips
from .timers import BreakType


class BreakOverlay(Gtk.Window):
    """Full-screen overlay window for breaks."""

    def __init__(
        self,
        break_type: str,
        duration_minutes: int,
        on_complete: Callable[[], None],
        on_skip: Callable[[], None],
        sound_player=None,
    ):
        super().__init__()

        self._break_type = break_type
        self._duration_seconds = duration_minutes * 60
        self._seconds_remaining = self._duration_seconds
        self._on_complete = on_complete
        self._on_skip = on_skip
        self._sound_player = sound_player
        self._timer_id: Optional[int] = None

        self._setup_window()
        self._build_ui()
        self._start_countdown()

    def _setup_window(self):
        """Configure window properties."""
        self.set_title("SpineGuard Break")
        self.set_decorated(False)
        self.set_modal(True)
        self.fullscreen()

        # Keep above all other windows
        self.set_deletable(False)

        # Add CSS class for styling
        self.add_css_class("break-overlay")

        # Connect to show signal to ensure it stays on top
        self.connect("realize", self._on_realize)

    def _on_realize(self, widget):
        """Called when window is realized - set always on top."""
        surface = self.get_surface()
        if surface:
            # For GTK4, we use the toplevel's methods
            pass

    def _build_ui(self):
        """Build the overlay UI."""
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)
        main_box.set_halign(Gtk.Align.CENTER)
        main_box.set_valign(Gtk.Align.CENTER)
        main_box.add_css_class("overlay-content")

        # Break type header
        if self._break_type == BreakType.WALK:
            header_text = "Time to Walk"
            header_icon = "🚶"
            instruction = f"Walk around for {self._duration_seconds // 60} minutes"
        else:
            header_text = "Time to Lie Down"
            header_icon = "🛏️"
            instruction = f"Lie down and decompress for {self._duration_seconds // 60} minutes"

        # Icon
        icon_label = Gtk.Label(label=header_icon)
        icon_label.add_css_class("break-icon")
        main_box.append(icon_label)

        # Header
        header_label = Gtk.Label(label=header_text)
        header_label.add_css_class("break-header")
        main_box.append(header_label)

        # Instruction
        instruction_label = Gtk.Label(label=instruction)
        instruction_label.add_css_class("break-instruction")
        main_box.append(instruction_label)

        # Countdown timer display
        self._countdown_drawing = Gtk.DrawingArea()
        self._countdown_drawing.set_size_request(250, 250)
        self._countdown_drawing.set_draw_func(self._draw_countdown)
        self._countdown_drawing.add_css_class("countdown-area")
        main_box.append(self._countdown_drawing)

        # Health tip
        if self._break_type == BreakType.WALK:
            tip_text = tips.get_walk_tip()
        else:
            tip_text = tips.get_lie_down_tip()

        tip_label = Gtk.Label(label=tip_text)
        tip_label.set_wrap(True)
        tip_label.set_max_width_chars(60)
        tip_label.set_justify(Gtk.Justification.CENTER)
        tip_label.add_css_class("health-tip")
        main_box.append(tip_label)

        # Buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        button_box.set_halign(Gtk.Align.CENTER)
        button_box.set_margin_top(30)

        done_early_btn = Gtk.Button(label="Done Early")
        done_early_btn.add_css_class("done-button")
        done_early_btn.connect("clicked", self._on_done_early)
        button_box.append(done_early_btn)

        skip_btn = Gtk.Button(label="Skip (Emergency)")
        skip_btn.add_css_class("skip-button")
        skip_btn.connect("clicked", self._on_skip_clicked)
        button_box.append(skip_btn)

        main_box.append(button_box)

        self.set_child(main_box)

    def _draw_countdown(self, area, cr, width, height):
        """Draw the circular countdown timer."""
        # Center point
        cx = width / 2
        cy = height / 2
        radius = min(width, height) / 2 - 20

        # Calculate progress
        progress = self._seconds_remaining / self._duration_seconds

        # Background circle (dark)
        cr.set_source_rgba(0.2, 0.3, 0.35, 0.5)
        cr.arc(cx, cy, radius, 0, 2 * math.pi)
        cr.fill()

        # Progress arc (bright)
        cr.set_source_rgba(0.4, 0.8, 0.6, 0.9)
        cr.set_line_width(12)
        cr.arc(
            cx,
            cy,
            radius - 6,
            -math.pi / 2,
            -math.pi / 2 + (2 * math.pi * progress),
        )
        cr.stroke()

        # Time text
        minutes = self._seconds_remaining // 60
        seconds = self._seconds_remaining % 60
        time_text = f"{minutes}:{seconds:02d}"

        cr.set_source_rgba(0.95, 0.95, 0.95, 1.0)
        cr.select_font_face("Sans", 0, 1)
        cr.set_font_size(48)

        extents = cr.text_extents(time_text)
        cr.move_to(cx - extents.width / 2, cy + extents.height / 3)
        cr.show_text(time_text)

    def _start_countdown(self):
        """Start the countdown timer."""
        self._timer_id = GLib.timeout_add_seconds(1, self._tick)

    def _tick(self) -> bool:
        """Called every second to update countdown."""
        self._seconds_remaining -= 1
        self._countdown_drawing.queue_draw()

        if self._seconds_remaining <= 0:
            self._finish()
            return False

        return True

    def _finish(self):
        """Break completed normally."""
        if self._timer_id:
            GLib.source_remove(self._timer_id)
            self._timer_id = None
        if self._sound_player:
            self._sound_player.play_break_end()
        self.close()
        self._on_complete()

    def _on_done_early(self, button):
        """User finished break early."""
        if self._timer_id:
            GLib.source_remove(self._timer_id)
            self._timer_id = None
        self.close()
        self._on_complete()

    def _on_skip_clicked(self, button):
        """User skipped the break (emergency)."""
        if self._timer_id:
            GLib.source_remove(self._timer_id)
            self._timer_id = None
        self.close()
        self._on_skip()
