"""Desktop notifications for SpineGuard."""

from gi.repository import Gio, GLib

from . import tips


class NotificationManager:
    """Manages desktop notifications for water and supplement reminders."""

    def __init__(self, application: Gio.Application):
        self._app = application

    def show_water_reminder(self):
        """Show a water reminder notification."""
        notification = Gio.Notification.new("Water Reminder")
        notification.set_body(tips.get_tip("water"))
        notification.set_priority(Gio.NotificationPriority.NORMAL)
        notification.add_button("Snooze 10 min", "app.snooze-water")
        self._app.send_notification("water-reminder", notification)

    def show_supplement_reminder(self, morning: bool):
        """Show a supplement reminder notification."""
        title = "Morning Supplements" if morning else "Evening Supplements"
        notification = Gio.Notification.new(title)
        notification.set_body(tips.get_supplement_tip(morning))
        notification.set_priority(Gio.NotificationPriority.HIGH)
        notification.add_button("Snooze 10 min", "app.snooze-supplement-morning" if morning else "app.snooze-supplement-evening")
        self._app.send_notification("supplement-reminder", notification)

    def show_pre_break_warning(self, break_type: str, seconds: int):
        """Show a pre-break warning notification."""
        minutes = seconds // 60
        break_name = "Walk" if break_type == "walk" else "Lie Down"
        notification = Gio.Notification.new(f"Break in {minutes} min")
        notification.set_body(f"{break_name} break coming up in {minutes} minutes. Wrap up your current task.")
        notification.set_priority(Gio.NotificationPriority.NORMAL)
        self._app.send_notification("pre-break-warning", notification)
