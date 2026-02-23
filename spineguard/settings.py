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
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        page.set_margin_top(28)
        page.set_margin_bottom(28)
        page.set_margin_start(28)
        page.set_margin_end(28)

        page.append(self._page_header("Timers", "Configure work cycles and break durations"))

        # Work cycle section
        page.append(self._section_header("WORK CYCLE"))

        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        card.add_css_class("panel-card")
        card.set_margin_bottom(20)

        card.append(self._setting_row(
            "Pomodoro duration", "Minutes of focused work before a break",
            self._make_spin(self._config.get("pomodoro_minutes"), 1, 120, "pomodoro_minutes"),
        ))
        card.append(self._thin_divider())
        card.append(self._setting_row(
            "Pre-break warning", "Notification minutes before break starts (0 = off)",
            self._make_spin(self._config.get("pre_break_warning_minutes"), 0, 10, "pre_break_warning_minutes"),
        ))
        card.append(self._thin_divider())
        card.append(self._setting_row(
            "Mode", "Standard (no standing) or Sit-Stand desk",
            self._make_mode_dropdown(),
        ))

        page.append(card)

        # Break durations section
        page.append(self._section_header("BREAK DURATIONS"))

        card2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        card2.add_css_class("panel-card")
        card2.set_margin_bottom(20)

        card2.append(self._setting_row(
            "Walk break", "Minutes for walking breaks",
            self._make_spin(self._config.get("walk_break_minutes"), 1, 30, "walk_break_minutes"),
        ))
        card2.append(self._thin_divider())
        card2.append(self._setting_row(
            "Lie-down break", "Minutes for decompression breaks",
            self._make_spin(self._config.get("lie_down_break_minutes"), 1, 30, "lie_down_break_minutes"),
        ))
        card2.append(self._thin_divider())
        card2.append(self._setting_row(
            "Water reminder", "Minutes between hydration reminders",
            self._make_spin(self._config.get("water_interval_minutes"), 5, 180, "water_interval_minutes"),
        ))

        page.append(card2)

        # Sit-stand section
        page.append(self._section_header("SIT-STAND DESK"))

        card3 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        card3.add_css_class("panel-card")
        card3.set_margin_bottom(20)

        card3.append(self._setting_row(
            "Position switch interval", "Minutes between sit/stand transitions",
            self._make_spin(self._config.get("position_switch_interval_minutes"), 5, 120, "position_switch_interval_minutes"),
        ))
        card3.append(self._thin_divider())
        card3.append(self._setting_row(
            "Position switch break", "Minutes for the transition break",
            self._make_spin(self._config.get("position_switch_break_minutes"), 1, 10, "position_switch_break_minutes"),
        ))

        page.append(card3)

        # Extra breaks section
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

        scrolled.set_child(page)
        return scrolled

    # ── Notifications Page ───────────────────────────────────

    def _build_notifications_page(self) -> Gtk.Widget:
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        page.set_margin_top(28)
        page.set_margin_bottom(28)
        page.set_margin_start(28)
        page.set_margin_end(28)

        page.append(self._page_header("Alerts", "Supplements, idle detection, and notification timing"))

        # Supplements
        page.append(self._section_header("SUPPLEMENTS"))

        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        card.add_css_class("panel-card")
        card.set_margin_bottom(20)

        card.append(self._setting_row(
            "Morning time", "When to remind for morning supplements",
            self._make_time_picker(
                self._config.get("supplement_morning_hour"),
                self._config.get("supplement_morning_minute"),
                "supplement_morning_hour", "supplement_morning_minute",
            ),
        ))
        card.append(self._thin_divider())
        card.append(self._setting_row(
            "Evening time", "When to remind for evening supplements",
            self._make_time_picker(
                self._config.get("supplement_evening_hour"),
                self._config.get("supplement_evening_minute"),
                "supplement_evening_hour", "supplement_evening_minute",
            ),
        ))

        page.append(card)

        # Physio workout
        page.append(self._section_header("PHYSIO WORKOUT"))

        physio_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        physio_card.add_css_class("panel-card")
        physio_card.set_margin_bottom(20)

        physio_switch = Gtk.Switch()
        physio_switch.set_active(self._config.get("physio_enabled"))
        physio_switch.connect("notify::active", self._on_physio_toggle)
        physio_switch.set_valign(Gtk.Align.CENTER)

        physio_card.append(self._setting_row(
            "Daily physio reminder", "Show a break overlay at the scheduled time",
            physio_switch,
        ))
        physio_card.append(self._thin_divider())
        physio_card.append(self._setting_row(
            "Physio time", "When to prompt for your physio workout",
            self._make_time_picker(
                self._config.get("physio_hour"),
                self._config.get("physio_minute"),
                "physio_hour", "physio_minute",
            ),
        ))

        page.append(physio_card)

        # Idle detection
        page.append(self._section_header("IDLE DETECTION"))

        card2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        card2.add_css_class("panel-card")
        card2.set_margin_bottom(20)

        idle_switch = Gtk.Switch()
        idle_switch.set_active(self._config.get("idle_detection_enabled"))
        idle_switch.connect("notify::active", self._on_idle_toggle)
        idle_switch.set_valign(Gtk.Align.CENTER)

        card2.append(self._setting_row(
            "Auto-pause when idle", "Pause timers when you step away from the keyboard",
            idle_switch,
        ))
        card2.append(self._thin_divider())
        card2.append(self._setting_row(
            "Idle threshold", "Minutes of inactivity before auto-pause",
            self._make_spin(self._config.get("idle_threshold_minutes"), 1, 30, "idle_threshold_minutes"),
        ))

        page.append(card2)

        scrolled.set_child(page)
        return scrolled

    # ── Sounds Page ──────────────────────────────────────────

    def _build_sounds_page(self) -> Gtk.Widget:
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        page.set_margin_top(28)
        page.set_margin_bottom(28)
        page.set_margin_start(28)
        page.set_margin_end(28)

        page.append(self._page_header("Sounds", "Choose notification sounds for each event"))

        sound_ids = ["complete", "bell", "message", "dialog-information", "dialog-warning"]

        page.append(self._section_header("SOUND EVENTS"))

        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        card.add_css_class("panel-card")
        card.set_margin_bottom(20)

        sound_settings = [
            ("Break start", "Sound when a break begins", "sound_break_start"),
            ("Break end", "Sound when a break timer completes", "sound_break_end"),
            ("Water reminder", "Hydration notification sound", "sound_water"),
            ("Supplement reminder", "Supplement notification sound", "sound_supplement"),
        ]

        for i, (label, desc, config_key) in enumerate(sound_settings):
            options = sound_ids + ["Custom file..."]
            dropdown = Gtk.DropDown.new_from_strings(options)

            current_val = self._config.get(config_key)
            if current_val in sound_ids:
                dropdown.set_selected(sound_ids.index(current_val))
            else:
                dropdown.set_selected(len(sound_ids))

            dropdown.connect("notify::selected", self._make_sound_handler(config_key, options, sound_ids))

            card.append(self._setting_row(label, desc, dropdown))
            if i < len(sound_settings) - 1:
                card.append(self._thin_divider())

        page.append(card)

        scrolled.set_child(page)
        return scrolled

    # ── Shared UI Builders ───────────────────────────────────

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

        # Pinned tracks
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
