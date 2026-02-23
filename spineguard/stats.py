"""Break statistics logging and display for SpineGuard."""

import json
import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk

from .config import STATE_DIR, STATS_FILE


class StatsManager:
    """Logs break events to a JSONL file and provides summaries."""

    def __init__(self):
        STATE_DIR.mkdir(parents=True, exist_ok=True)

    def _append(self, event: dict):
        """Append an event to the stats log."""
        event["timestamp"] = datetime.now().isoformat()
        try:
            with open(STATS_FILE, "a") as f:
                f.write(json.dumps(event) + "\n")
        except IOError:
            pass

    def log_break_completed(self, break_type: str):
        self._append({"event": "break_completed", "break_type": break_type})

    def log_break_skipped(self, break_type: str):
        self._append({"event": "break_skipped", "break_type": break_type})

    def log_break_done_early(self, break_type: str):
        self._append({"event": "break_done_early", "break_type": break_type})

    def _read_events(self) -> list[dict]:
        if not STATS_FILE.exists():
            return []
        events = []
        try:
            with open(STATS_FILE, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            events.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        except IOError:
            pass
        return events

    def _filter_by_date(self, events: list[dict], start_date: datetime) -> list[dict]:
        result = []
        for ev in events:
            try:
                ts = datetime.fromisoformat(ev["timestamp"])
                if ts >= start_date:
                    result.append(ev)
            except (KeyError, ValueError):
                continue
        return result

    def _summarize(self, events: list[dict]) -> dict:
        summary = {
            "completed": 0,
            "skipped": 0,
            "done_early": 0,
            "by_type": {},
        }
        for ev in events:
            event_type = ev.get("event", "")
            break_type = ev.get("break_type", "unknown")

            if event_type == "break_completed":
                summary["completed"] += 1
            elif event_type == "break_skipped":
                summary["skipped"] += 1
            elif event_type == "break_done_early":
                summary["done_early"] += 1

            if break_type not in summary["by_type"]:
                summary["by_type"][break_type] = {"completed": 0, "skipped": 0, "done_early": 0}
            if event_type == "break_completed":
                summary["by_type"][break_type]["completed"] += 1
            elif event_type == "break_skipped":
                summary["by_type"][break_type]["skipped"] += 1
            elif event_type == "break_done_early":
                summary["by_type"][break_type]["done_early"] += 1

        return summary

    def get_today_summary(self) -> dict:
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        events = self._filter_by_date(self._read_events(), today)
        return self._summarize(events)

    def get_week_summary(self) -> dict:
        week_ago = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=7)
        events = self._filter_by_date(self._read_events(), week_ago)
        return self._summarize(events)


# ── Break type display metadata ──────────────────────────────

_BREAK_META = {
    "walk":            {"icon": "\U0001f6b6", "name": "Walk Breaks"},
    "lie_down":        {"icon": "\U0001f6cf\ufe0f", "name": "Lie-Down Breaks"},
    "position_switch": {"icon": "\U0001f9cd", "name": "Position Switches"},
    "breathing":       {"icon": "\U0001f32c\ufe0f", "name": "Breathing Breaks"},
    "eye_rest":        {"icon": "\U0001f440", "name": "Eye Rest Breaks"},
}


class StatsWindow(Gtk.Window):
    """Dashboard-style statistics window."""

    def __init__(self, stats_manager: StatsManager, application: Optional[Gtk.Application] = None):
        super().__init__(title="SpineGuard — Statistics")
        if application:
            self.set_application(application)
        self._stats = stats_manager
        self.set_default_size(520, 640)
        self.add_css_class("stats-window")

        self._period = "today"  # "today" or "week"
        self._content_box: Optional[Gtk.Box] = None
        self._build_ui()

    def _build_ui(self):
        """Build the full stats dashboard."""
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        outer.set_margin_top(32)
        outer.set_margin_bottom(32)
        outer.set_margin_start(28)
        outer.set_margin_end(28)

        # ── Window title ─────────────────────────────────
        title = Gtk.Label(label="Statistics")
        title.add_css_class("settings-page-title")
        title.set_halign(Gtk.Align.START)
        outer.append(title)

        subtitle = Gtk.Label(label="Your break compliance overview")
        subtitle.add_css_class("settings-page-subtitle")
        subtitle.set_halign(Gtk.Align.START)
        subtitle.set_margin_bottom(24)
        outer.append(subtitle)

        # ── Period tabs ──────────────────────────────────
        tab_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        tab_box.set_margin_bottom(20)

        self._tab_today = Gtk.Button(label="TODAY")
        self._tab_today.add_css_class("stats-period-tab")
        self._tab_today.add_css_class("stats-period-tab-active")
        self._tab_today.connect("clicked", lambda _: self._switch_period("today"))
        tab_box.append(self._tab_today)

        self._tab_week = Gtk.Button(label="7 DAYS")
        self._tab_week.add_css_class("stats-period-tab")
        self._tab_week.connect("clicked", lambda _: self._switch_period("week"))
        tab_box.append(self._tab_week)

        outer.append(tab_box)

        # ── Content area (rebuilt on period switch) ──────
        self._content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        outer.append(self._content_box)

        scrolled.set_child(outer)
        self.set_child(scrolled)

        self._render_period()

    def _switch_period(self, period: str):
        if period == self._period:
            return
        self._period = period

        # Update tab styling
        if period == "today":
            self._tab_today.add_css_class("stats-period-tab-active")
            self._tab_week.remove_css_class("stats-period-tab-active")
        else:
            self._tab_week.add_css_class("stats-period-tab-active")
            self._tab_today.remove_css_class("stats-period-tab-active")

        self._render_period()

    def _render_period(self):
        """Render the stats content for the active period."""
        # Clear existing content
        child = self._content_box.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self._content_box.remove(child)
            child = next_child

        summary = self._stats.get_today_summary() if self._period == "today" else self._stats.get_week_summary()
        total = summary["completed"] + summary["done_early"] + summary["skipped"]

        # ── Hero: compliance percentage ──────────────────
        hero_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        hero_card.add_css_class("panel-card")
        hero_card.set_halign(Gtk.Align.FILL)
        hero_card.set_margin_bottom(16)

        hero_inner = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=24)
        hero_inner.set_halign(Gtk.Align.CENTER)
        hero_inner.set_valign(Gtk.Align.CENTER)

        # Compliance ring (custom drawn)
        compliance = 0
        if total > 0:
            compliance = round((summary["completed"] + summary["done_early"]) / total * 100)

        ring = Gtk.DrawingArea()
        ring.set_size_request(100, 100)
        ring.set_draw_func(self._draw_compliance_ring, compliance)
        hero_inner.append(ring)

        # Text beside ring
        hero_text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        hero_text.set_valign(Gtk.Align.CENTER)

        hero_label = Gtk.Label(label="COMPLIANCE")
        hero_label.add_css_class("stats-hero-label")
        hero_label.set_halign(Gtk.Align.START)
        hero_text.append(hero_label)

        pct_text = f"{compliance}%"
        hero_value = Gtk.Label(label=pct_text)
        hero_value.add_css_class("stats-hero-value")
        hero_value.set_halign(Gtk.Align.START)
        hero_text.append(hero_value)

        period_label = "today" if self._period == "today" else "last 7 days"
        hero_sub = Gtk.Label(label=f"{total} breaks {period_label}")
        hero_sub.add_css_class("stats-hero-subtitle")
        hero_sub.set_halign(Gtk.Align.START)
        hero_text.append(hero_sub)

        hero_inner.append(hero_text)
        hero_card.append(hero_inner)
        self._content_box.append(hero_card)

        # ── Three metric cards ───────────────────────────
        metrics_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        metrics_box.set_homogeneous(True)
        metrics_box.set_margin_bottom(20)

        metrics_box.append(self._build_metric_card(
            str(summary["completed"]), "COMPLETED", "metric-completed"
        ))
        metrics_box.append(self._build_metric_card(
            str(summary["done_early"]), "DONE EARLY", "metric-early"
        ))
        metrics_box.append(self._build_metric_card(
            str(summary["skipped"]), "SKIPPED", "metric-skipped"
        ))
        self._content_box.append(metrics_box)

        # ── Breakdown by type ────────────────────────────
        if summary["by_type"]:
            section_label = Gtk.Label(label="BREAKDOWN")
            section_label.add_css_class("stats-section-title")
            section_label.set_halign(Gtk.Align.START)
            section_label.set_margin_bottom(10)
            self._content_box.append(section_label)

            breakdown_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

            for break_type in ("walk", "lie_down", "position_switch", "breathing", "eye_rest"):
                if break_type not in summary["by_type"]:
                    continue
                bt = summary["by_type"][break_type]
                meta = _BREAK_META.get(break_type, {"icon": "?", "name": break_type})
                breakdown_box.append(self._build_breakdown_row(
                    meta["icon"], meta["name"], bt
                ))

            self._content_box.append(breakdown_box)
        elif total == 0:
            empty = Gtk.Label(label="No breaks recorded yet. Take your first break!")
            empty.add_css_class("stats-empty")
            empty.set_margin_top(40)
            self._content_box.append(empty)

    def _build_metric_card(self, value: str, label: str, css_variant: str) -> Gtk.Box:
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        card.add_css_class("metric-card")
        card.add_css_class(css_variant)
        card.set_halign(Gtk.Align.FILL)

        val = Gtk.Label(label=value)
        val.add_css_class("metric-value")
        card.append(val)

        lbl = Gtk.Label(label=label)
        lbl.add_css_class("metric-label")
        card.append(lbl)

        return card

    def _build_breakdown_row(self, icon: str, name: str, counts: dict) -> Gtk.Box:
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        row.add_css_class("breakdown-row")

        # Icon
        icon_label = Gtk.Label(label=icon)
        icon_label.add_css_class("breakdown-type-icon")
        icon_label.set_valign(Gtk.Align.CENTER)
        row.append(icon_label)

        # Name
        name_label = Gtk.Label(label=name)
        name_label.add_css_class("breakdown-type-name")
        name_label.set_hexpand(True)
        name_label.set_halign(Gtk.Align.START)
        name_label.set_valign(Gtk.Align.CENTER)
        row.append(name_label)

        # Count cells
        for count_val, count_label, css_class in [
            (counts["completed"], "done", "breakdown-count-completed"),
            (counts["done_early"], "early", "breakdown-count-early"),
            (counts["skipped"], "skip", "breakdown-count-skipped"),
        ]:
            cell = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
            cell.set_valign(Gtk.Align.CENTER)
            cell.set_halign(Gtk.Align.CENTER)
            cell.set_size_request(48, -1)

            cv = Gtk.Label(label=str(count_val))
            cv.add_css_class("breakdown-count")
            cv.add_css_class(css_class)
            cell.append(cv)

            cl = Gtk.Label(label=count_label.upper())
            cl.add_css_class("breakdown-count-label")
            cell.append(cl)

            row.append(cell)

        return row

    @staticmethod
    def _draw_compliance_ring(area, cr, width, height, compliance):
        """Draw a compliance ring with the percentage."""
        cx = width / 2
        cy = height / 2
        radius = min(width, height) / 2 - 6
        line_w = 7

        # Background ring
        cr.set_source_rgba(0.54, 0.61, 0.69, 0.1)
        cr.set_line_width(line_w)
        cr.arc(cx, cy, radius, 0, 2 * math.pi)
        cr.stroke()

        # Progress arc
        if compliance > 0:
            fraction = compliance / 100.0
            if compliance >= 70:
                cr.set_source_rgba(0.27, 0.83, 0.54, 0.85)  # green
            elif compliance >= 40:
                cr.set_source_rgba(0.91, 0.72, 0.29, 0.85)  # amber
            else:
                cr.set_source_rgba(0.91, 0.39, 0.35, 0.85)  # coral
            cr.set_line_width(line_w)
            cr.set_line_cap(1)  # CAIRO_LINE_CAP_ROUND
            cr.arc(cx, cy, radius, -math.pi / 2, -math.pi / 2 + 2 * math.pi * fraction)
            cr.stroke()

        # Center percentage text
        cr.set_source_rgba(0.89, 0.93, 0.96, 1.0)
        cr.select_font_face("Sans", 0, 1)
        cr.set_font_size(22)
        text = f"{compliance}%"
        extents = cr.text_extents(text)
        cr.move_to(cx - extents.width / 2, cy + extents.height / 3)
        cr.show_text(text)
