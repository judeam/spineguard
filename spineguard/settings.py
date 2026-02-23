"""Settings dialog for SpineGuard."""

from typing import Optional

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gio, Gtk

from .config import Config


class SettingsDialog(Gtk.Window):
    """Refined GTK4 preferences dialog with sidebar navigation."""

    def __init__(self, config: Config, application: Optional[Gtk.Application] = None, routine_progress=None):
        super().__init__(title="SpineGuard — Settings")
        if application:
            self.set_application(application)
        self._config = config
        self._routine_progress = routine_progress
        self.set_default_size(620, 560)
        self.set_resizable(True)
        self.add_css_class("settings-window")
        self._build_ui()

    def _build_ui(self):
        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        stack.set_transition_duration(150)

        stack.add_titled(self._build_timers_page(), "timers", "Timers")
        stack.add_titled(self._build_notifications_page(), "notifications", "Alerts")
        stack.add_titled(self._build_sounds_page(), "sounds", "Sounds")
        stack.add_titled(self._build_routines_page(), "routines", "Routines")

        sidebar = Gtk.StackSidebar()
        sidebar.set_stack(stack)
        sidebar.set_size_request(160, -1)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        hbox.append(sidebar)

        sep = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL)
        hbox.append(sep)

        stack.set_hexpand(True)
        hbox.append(stack)

        self.set_child(hbox)

    # ── Timers Page ──────────────────────────────────────────

    def _build_timers_page(self) -> Gtk.Widget:
        scrolled, page = self._build_page("Timers", "Configure work cycles and break durations")

        page.append(self._section_header("WORK CYCLE"))
        page.append(self._build_card([
            ("Pomodoro duration", "Minutes of focused work before a break",
             self._make_spin(self._config.get("pomodoro_minutes"), 1, 120, "pomodoro_minutes")),
            ("Pre-break warning", "Notification minutes before break starts (0 = off)",
             self._make_spin(self._config.get("pre_break_warning_minutes"), 0, 10, "pre_break_warning_minutes")),
            ("Mode", "Standard (no standing) or Sit-Stand desk",
             self._make_mode_dropdown()),
        ]))

        page.append(self._section_header("BREAK DURATIONS"))
        page.append(self._build_card([
            ("Walk break", "Minutes for walking breaks",
             self._make_spin(self._config.get("walk_break_minutes"), 1, 30, "walk_break_minutes")),
            ("Lie-down break", "Minutes for decompression breaks",
             self._make_spin(self._config.get("lie_down_break_minutes"), 1, 30, "lie_down_break_minutes")),
            ("Water reminder", "Minutes between hydration reminders",
             self._make_spin(self._config.get("water_interval_minutes"), 5, 180, "water_interval_minutes")),
        ]))

        page.append(self._section_header("SIT-STAND DESK"))
        page.append(self._build_card([
            ("Position switch interval", "Minutes between sit/stand transitions",
             self._make_spin(self._config.get("position_switch_interval_minutes"), 5, 120, "position_switch_interval_minutes")),
            ("Position switch break", "Minutes for the transition break",
             self._make_spin(self._config.get("position_switch_break_minutes"), 1, 10, "position_switch_break_minutes")),
        ]))

        page.append(self._section_header("EXTRA BREAKS"))

        breathing_switch = Gtk.Switch()
        breathing_switch.set_active(self._config.get("breathing_enabled"))
        breathing_switch.connect("notify::active", lambda s, _: self._config.set("breathing_enabled", s.get_active()))
        breathing_switch.set_valign(Gtk.Align.CENTER)

        eye_rest_switch = Gtk.Switch()
        eye_rest_switch.set_active(self._config.get("eye_rest_enabled"))
        eye_rest_switch.connect("notify::active", lambda s, _: self._config.set("eye_rest_enabled", s.get_active()))
        eye_rest_switch.set_valign(Gtk.Align.CENTER)

        page.append(self._build_card([
            ("Breathing exercises", "Short breathing breaks between pomodoro cycles", breathing_switch),
            ("Breathing frequency", "Trigger every N pomodoro cycles",
             self._make_spin(self._config.get("breathing_frequency"), 1, 10, "breathing_frequency")),
            ("Eye rest micro-breaks", "20-20-20 rule: brief popup every N minutes", eye_rest_switch),
            ("Eye rest interval", "Minutes between eye rest reminders",
             self._make_spin(self._config.get("eye_rest_interval_minutes"), 5, 60, "eye_rest_interval_minutes")),
        ]))

        return scrolled

    # ── Notifications Page ───────────────────────────────────

    def _build_notifications_page(self) -> Gtk.Widget:
        scrolled, page = self._build_page("Alerts", "Supplements, idle detection, and notification timing")

        page.append(self._section_header("SUPPLEMENTS"))
        page.append(self._build_card([
            ("Morning time", "When to remind for morning supplements",
             self._make_time_picker(
                 self._config.get("supplement_morning_hour"),
                 self._config.get("supplement_morning_minute"),
                 "supplement_morning_hour", "supplement_morning_minute")),
            ("Evening time", "When to remind for evening supplements",
             self._make_time_picker(
                 self._config.get("supplement_evening_hour"),
                 self._config.get("supplement_evening_minute"),
                 "supplement_evening_hour", "supplement_evening_minute")),
        ]))

        page.append(self._section_header("PHYSIO WORKOUT"))

        physio_switch = Gtk.Switch()
        physio_switch.set_active(self._config.get("physio_enabled"))
        physio_switch.connect("notify::active", self._on_physio_toggle)
        physio_switch.set_valign(Gtk.Align.CENTER)

        page.append(self._build_card([
            ("Daily physio reminder", "Show a break overlay at the scheduled time", physio_switch),
            ("Physio time", "When to prompt for your physio workout",
             self._make_time_picker(
                 self._config.get("physio_hour"),
                 self._config.get("physio_minute"),
                 "physio_hour", "physio_minute")),
        ]))

        page.append(self._section_header("IDLE DETECTION"))

        idle_switch = Gtk.Switch()
        idle_switch.set_active(self._config.get("idle_detection_enabled"))
        idle_switch.connect("notify::active", self._on_idle_toggle)
        idle_switch.set_valign(Gtk.Align.CENTER)

        page.append(self._build_card([
            ("Auto-pause when idle", "Pause timers when you step away from the keyboard", idle_switch),
            ("Idle threshold", "Minutes of inactivity before auto-pause",
             self._make_spin(self._config.get("idle_threshold_minutes"), 1, 30, "idle_threshold_minutes")),
        ]))

        return scrolled

    # ── Sounds Page ──────────────────────────────────────────

    def _build_sounds_page(self) -> Gtk.Widget:
        scrolled, page = self._build_page("Sounds", "Choose notification sounds for each event")

        sound_ids = ["complete", "bell", "message", "dialog-information", "dialog-warning"]
        sound_settings = [
            ("Break start", "Sound when a break begins", "sound_break_start"),
            ("Break end", "Sound when a break timer completes", "sound_break_end"),
            ("Water reminder", "Hydration notification sound", "sound_water"),
            ("Supplement reminder", "Supplement notification sound", "sound_supplement"),
        ]

        rows = []
        for label, desc, config_key in sound_settings:
            options = sound_ids + ["Custom file..."]
            dropdown = Gtk.DropDown.new_from_strings(options)
            current_val = self._config.get(config_key)
            if current_val in sound_ids:
                dropdown.set_selected(sound_ids.index(current_val))
            else:
                dropdown.set_selected(len(sound_ids))
            dropdown.connect("notify::selected", self._make_sound_handler(config_key, options, sound_ids))
            rows.append((label, desc, dropdown))

        page.append(self._section_header("SOUND EVENTS"))
        page.append(self._build_card(rows))

        return scrolled

    # ── Shared UI Builders ───────────────────────────────────

    def _build_page(self, title: str, subtitle: str):
        """Create a scrolled page with standard margins and header. Returns (scrolled, page)."""
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        page.set_margin_top(28)
        page.set_margin_bottom(28)
        page.set_margin_start(28)
        page.set_margin_end(28)
        page.append(self._page_header(title, subtitle))
        scrolled.set_child(page)
        return scrolled, page

    def _build_card(self, rows) -> Gtk.Box:
        """Build a card with setting rows separated by dividers.

        rows: list of (label, description, control) tuples.
        """
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        card.add_css_class("panel-card")
        card.set_margin_bottom(20)
        for i, (label, desc, control) in enumerate(rows):
            if i > 0:
                card.append(self._thin_divider())
            card.append(self._setting_row(label, desc, control))
        return card

    def _build_track_dropdown(self, tracks: dict, config_key: str) -> Gtk.DropDown:
        """Build a dropdown for pinning a specific exercise track."""
        names = ["Auto"] + [t["name"] for t in tracks.values()]
        ids = [None] + list(tracks.keys())
        dropdown = Gtk.DropDown.new_from_strings(names)
        current = self._config.get(config_key)
        if current in ids:
            dropdown.set_selected(ids.index(current))
        dropdown.connect("notify::selected", lambda d, _: self._config.set(
            config_key, ids[d.get_selected()] if d.get_selected() > 0 else None
        ))
        return dropdown

    def _page_header(self, title: str, subtitle: str) -> Gtk.Box:
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        box.set_margin_bottom(24)

        t = Gtk.Label(label=title)
        t.add_css_class("settings-page-title")
        t.set_halign(Gtk.Align.START)
        box.append(t)

        s = Gtk.Label(label=subtitle)
        s.add_css_class("settings-page-subtitle")
        s.set_halign(Gtk.Align.START)
        box.append(s)

        return box

    def _section_header(self, text: str) -> Gtk.Label:
        label = Gtk.Label(label=text)
        label.add_css_class("settings-section-header")
        label.set_halign(Gtk.Align.START)
        label.set_margin_bottom(10)
        label.set_margin_top(4)
        return label

    def _thin_divider(self) -> Gtk.Box:
        div = Gtk.Box()
        div.add_css_class("settings-divider")
        div.set_margin_start(16)
        div.set_margin_end(16)
        return div

    def _setting_row(self, label: str, description: str, control: Gtk.Widget) -> Gtk.Box:
        """Build a single setting row with label, description, and control."""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        row.add_css_class("setting-row")

        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        text_box.set_hexpand(True)
        text_box.set_valign(Gtk.Align.CENTER)

        lbl = Gtk.Label(label=label)
        lbl.add_css_class("setting-label")
        lbl.set_halign(Gtk.Align.START)
        text_box.append(lbl)

        desc = Gtk.Label(label=description)
        desc.add_css_class("setting-sublabel")
        desc.set_halign(Gtk.Align.START)
        text_box.append(desc)

        row.append(text_box)

        control.set_valign(Gtk.Align.CENTER)
        row.append(control)

        return row

    def _make_spin(self, value, min_val, max_val, config_key: str) -> Gtk.SpinButton:
        adjustment = Gtk.Adjustment(value=value, lower=min_val, upper=max_val, step_increment=1)
        spin = Gtk.SpinButton(adjustment=adjustment)
        spin.set_numeric(True)
        spin.connect("value-changed", lambda w, k=config_key: self._config.set(k, int(w.get_value())))
        return spin

    def _make_mode_dropdown(self) -> Gtk.DropDown:
        dropdown = Gtk.DropDown.new_from_strings(["Standard", "Sit-Stand"])
        current = 1 if self._config.get("mode") == "sit_stand" else 0
        dropdown.set_selected(current)
        dropdown.connect("notify::selected", self._on_mode_changed)
        return dropdown

    def _make_time_picker(self, hour, minute, hour_key, minute_key) -> Gtk.Box:
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        box.set_valign(Gtk.Align.CENTER)

        h_spin = Gtk.SpinButton(adjustment=Gtk.Adjustment(value=hour, lower=0, upper=23, step_increment=1))
        h_spin.set_numeric(True)
        h_spin.connect("value-changed", lambda w, k=hour_key: self._config.set(k, int(w.get_value())))
        box.append(h_spin)

        colon = Gtk.Label(label=":")
        colon.add_css_class("time-colon")
        box.append(colon)

        m_spin = Gtk.SpinButton(adjustment=Gtk.Adjustment(value=minute, lower=0, upper=59, step_increment=1))
        m_spin.set_numeric(True)
        m_spin.connect("value-changed", lambda w, k=minute_key: self._config.set(k, int(w.get_value())))
        box.append(m_spin)

        return box

    def _make_sound_handler(self, config_key, options, sound_ids):
        def handler(dropdown, _pspec):
            idx = dropdown.get_selected()
            if idx < len(sound_ids):
                self._config.set(config_key, sound_ids[idx])
            else:
                self._choose_sound_file(config_key)
        return handler

    def _choose_sound_file(self, config_key: str):
        dialog = Gtk.FileDialog()
        dialog.set_title("Choose Sound File")

        filter_audio = Gtk.FileFilter()
        filter_audio.set_name("Audio files")
        filter_audio.add_mime_type("audio/*")
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(filter_audio)
        dialog.set_filters(filters)

        def on_response(dialog, result):
            try:
                file = dialog.open_finish(result)
                if file:
                    self._config.set(config_key, file.get_path())
            except Exception:
                pass

        dialog.open(self, None, on_response)

    # ── Routines Page ────────────────────────────────────────

    def _build_routines_page(self) -> Gtk.Widget:
        scrolled, page = self._build_page("Routines", "Manage exercise track rotation and progression")

        from . import tips

        # Rotation mode
        page.append(self._section_header("TRACK ROTATION"))

        mode_dropdown = Gtk.DropDown.new_from_strings(["Auto-rotate daily", "Manual selection"])
        current_mode = 1 if self._config.get("routine_mode") == "manual" else 0
        mode_dropdown.set_selected(current_mode)
        mode_dropdown.connect("notify::selected", lambda d, _: self._config.set(
            "routine_mode", "manual" if d.get_selected() == 1 else "auto"
        ))

        page.append(self._build_card([
            ("Rotation mode", "How tracks are selected each day", mode_dropdown),
        ]))

        # Pinned tracks
        page.append(self._section_header("PINNED TRACKS"))
        page.append(self._build_card([
            ("Walk track", "Pin a specific walk track",
             self._build_track_dropdown(tips.WALK_TRACKS, "pinned_walk_track")),
            ("Lie-down track", "Pin a specific lie-down track",
             self._build_track_dropdown(tips.LIE_DOWN_TRACKS, "pinned_lie_down_track")),
        ]))

        # Reset progress
        page.append(self._section_header("PROGRESS"))

        reset_btn = Gtk.Button(label="Reset All Progress")
        reset_btn.add_css_class("skip-button")
        reset_btn.connect("clicked", self._on_reset_progress)

        page.append(self._build_card([
            ("Reset progress", "Clear all track levels and completions", reset_btn),
        ]))

        return scrolled

    def _on_reset_progress(self, button):
        """Reset all routine progress."""
        if self._routine_progress:
            self._routine_progress.reset_progress()

    # ── Handlers ─────────────────────────────────────────────

    def _on_mode_changed(self, dropdown, _pspec):
        self._config.set("mode", "sit_stand" if dropdown.get_selected() == 1 else "recovery")

    def _on_idle_toggle(self, switch, _pspec):
        self._config.set("idle_detection_enabled", switch.get_active())

    def _on_physio_toggle(self, switch, _pspec):
        self._config.set("physio_enabled", switch.get_active())
