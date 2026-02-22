"""Full-screen break overlay window for SpineGuard."""

import math
import random
from typing import Callable, Optional

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")

from gi.repository import Gdk, GLib, Gtk

from . import tips
from .timers import BreakType


class BlockingOverlay(Gtk.Window):
    """Simple fullscreen dark overlay for secondary monitors during breaks."""

    def __init__(self, monitor: Optional[Gdk.Monitor] = None):
        super().__init__()
        self.set_title("SpineGuard Break")
        self.set_decorated(False)
        self.set_deletable(False)
        if hasattr(self, "set_keep_above"):
            self.set_keep_above(True)
        self.add_css_class("break-overlay")

        label = Gtk.Label(label="Break in progress")
        label.add_css_class("break-header")
        label.set_halign(Gtk.Align.CENTER)
        label.set_valign(Gtk.Align.CENTER)
        self.set_child(label)

        if monitor:
            self.fullscreen_on_monitor(monitor)
        else:
            self.fullscreen()

        self.connect("realize", self._on_realize)

    def _on_realize(self, widget):
        try:
            surface = self.get_surface()
            if surface and hasattr(surface, "set_keep_above"):
                surface.set_keep_above(True)
        except Exception:
            pass


class BreakOverlay(Gtk.Window):
    """Full-screen overlay window for breaks."""

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
    ):
        super().__init__()

        self._break_type = break_type
        self._untimed = duration_minutes is None
        self._duration_seconds = (duration_minutes * 60) if duration_minutes else 0
        self._seconds_remaining = self._duration_seconds
        self._seconds_elapsed = 0
        self._on_complete = on_complete
        self._on_skip = on_skip
        self._on_done_early_cb = on_done_early
        self._sound_player = sound_player
        self._context = context or {}
        self._timer_id: Optional[int] = None
        self._monitor = monitor

        # Routine tracking (set by _build_ui if a routine is selected)
        self._routine = None
        self._routine_step_index = 0
        self._routine_step_elapsed = 0
        self._tip_label: Optional[Gtk.Label] = None

        # Done button delay for untimed breaks
        self._done_button: Optional[Gtk.Button] = None
        self._done_delay_remaining: int = 10

        self._setup_window()
        self._build_ui()
        self._start_countdown()

    def _setup_window(self):
        """Configure window properties."""
        self.set_title("SpineGuard Break")
        self.set_decorated(False)
        if self._monitor:
            self.fullscreen_on_monitor(self._monitor)
        else:
            self.fullscreen()

        # Keep above all other windows
        self.set_deletable(False)
        if hasattr(self, "set_keep_above"):
            self.set_keep_above(True)

        # Add CSS class for styling
        self.add_css_class("break-overlay")

        # Connect to realize signal to ensure it stays on top
        self.connect("realize", self._on_realize)

    def _on_realize(self, widget):
        """Called when window is realized - set always on top via surface."""
        try:
            surface = self.get_surface()
            if surface and hasattr(surface, "set_keep_above"):
                surface.set_keep_above(True)
        except Exception:
            # Wayland compositors may not support this — known limitation
            pass

    def _build_ui(self):
        """Build the overlay UI."""
        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)
        main_box.set_halign(Gtk.Align.CENTER)
        main_box.set_valign(Gtk.Align.CENTER)
        main_box.add_css_class("overlay-content")

        # Break type header
        if self._break_type == BreakType.PHYSIO:
            header_text = "Time for Physio"
            header_icon = "\U0001f3cb\ufe0f"
            instruction = "Do your physio workout"
        elif self._break_type == BreakType.POSITION_SWITCH:
            next_position = self._context.get("next_position", "standing")
            if next_position == "standing":
                header_text = "Time to Stand"
                header_icon = "🧍"
                instruction = "Stand up and adjust your desk"
            else:
                header_text = "Time to Sit"
                header_icon = "🪑"
                instruction = "Lower your desk and sit down"
            self.add_css_class("position-switch")
        elif self._break_type == BreakType.WALK:
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

        # Health tip or routine
        if self._break_type == BreakType.PHYSIO:
            tip_text = tips.get_physio_tip()
            self._tip_label = Gtk.Label(label=tip_text)
            self._tip_label.set_wrap(True)
            self._tip_label.set_max_width_chars(60)
            self._tip_label.set_justify(Gtk.Justification.CENTER)
            self._tip_label.add_css_class("health-tip")
            main_box.append(self._tip_label)
        else:
            use_routine = (
                self._break_type != BreakType.POSITION_SWITCH
                and random.random() < 0.7
            )

            if use_routine:
                if self._break_type == BreakType.WALK:
                    self._routine = tips.get_walk_routine()
                else:
                    self._routine = tips.get_lie_down_routine()

                # Routine name as header
                routine_header = Gtk.Label(label=self._routine["name"])
                routine_header.add_css_class("break-instruction")
                main_box.append(routine_header)

                # Current step instruction (updated in _tick)
                first_step = self._routine["steps"][0]["instruction"]
                self._tip_label = Gtk.Label(label=first_step)
                self._tip_label.set_wrap(True)
                self._tip_label.set_max_width_chars(60)
                self._tip_label.set_justify(Gtk.Justification.CENTER)
                self._tip_label.add_css_class("health-tip")
                main_box.append(self._tip_label)
            else:
                if self._break_type == BreakType.POSITION_SWITCH:
                    tip_text = tips.get_position_switch_tip()
                elif self._break_type == BreakType.WALK:
                    tip_text = tips.get_walk_tip()
                else:
                    tip_text = tips.get_lie_down_tip()

                self._tip_label = Gtk.Label(label=tip_text)
                self._tip_label.set_wrap(True)
                self._tip_label.set_max_width_chars(60)
                self._tip_label.set_justify(Gtk.Justification.CENTER)
                self._tip_label.add_css_class("health-tip")
                main_box.append(self._tip_label)

        # Buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        button_box.set_halign(Gtk.Align.CENTER)
        button_box.set_margin_top(30)

        if self._untimed:
            self._done_button = Gtk.Button(label=f"Done ({self._done_delay_remaining}s)")
            self._done_button.add_css_class("done-button")
            self._done_button.set_sensitive(False)
            self._done_button.connect("clicked", self._on_done_early)
            button_box.append(self._done_button)
        else:
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
        """Draw the circular countdown/count-up timer."""
        # Center point
        cx = width / 2
        cy = height / 2
        radius = min(width, height) / 2 - 20

        # Background circle (dark)
        cr.set_source_rgba(0.2, 0.3, 0.35, 0.5)
        cr.arc(cx, cy, radius, 0, 2 * math.pi)
        cr.fill()

        if not self._untimed:
            # Progress arc (bright) — only for timed breaks
            progress = self._seconds_remaining / self._duration_seconds
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
        if self._untimed:
            display_seconds = self._seconds_elapsed
        else:
            display_seconds = self._seconds_remaining
        minutes = display_seconds // 60
        seconds = display_seconds % 60
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
        if self._untimed:
            self._seconds_elapsed += 1
            # Handle Done button enable countdown
            if self._done_delay_remaining > 0:
                self._done_delay_remaining -= 1
                if self._done_delay_remaining <= 0:
                    if self._done_button:
                        self._done_button.set_label("Done")
                        self._done_button.set_sensitive(True)
                elif self._done_button:
                    self._done_button.set_label(f"Done ({self._done_delay_remaining}s)")
            self._countdown_drawing.queue_draw()
            return True

        self._seconds_remaining -= 1
        self._countdown_drawing.queue_draw()

        # Advance routine step if active
        if self._routine and self._tip_label:
            self._routine_step_elapsed += 1
            steps = self._routine["steps"]
            if self._routine_step_index < len(steps):
                current_step = steps[self._routine_step_index]
                step_duration = current_step["duration_seconds"]
                # duration_seconds == 0 means "fill remaining time"
                if step_duration > 0 and self._routine_step_elapsed >= step_duration:
                    self._routine_step_index += 1
                    self._routine_step_elapsed = 0
                    if self._routine_step_index < len(steps):
                        self._tip_label.set_text(steps[self._routine_step_index]["instruction"])

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
        if self._on_done_early_cb:
            self._on_done_early_cb()
        else:
            self._on_complete()

    def _on_skip_clicked(self, button):
        """User skipped the break (emergency)."""
        if self._timer_id:
            GLib.source_remove(self._timer_id)
            self._timer_id = None
        self.close()
        self._on_skip()
