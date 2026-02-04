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
        notification.set_body(tips.get_water_tip())
        notification.set_priority(Gio.NotificationPriority.NORMAL)
        self._app.send_notification("water-reminder", notification)

    def show_supplement_reminder(self, morning: bool):
        """Show a supplement reminder notification."""
        title = "Morning Supplements" if morning else "Evening Supplements"
        notification = Gio.Notification.new(title)
        notification.set_body(tips.get_supplement_tip(morning))
        notification.set_priority(Gio.NotificationPriority.HIGH)
        self._app.send_notification("supplement-reminder", notification)
