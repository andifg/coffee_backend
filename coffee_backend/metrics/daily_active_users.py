import logging
from datetime import datetime

from prometheus_client import Gauge


class DailyActiveUsersMetric:
    """Class to keep track of the daily active users."""

    def __init__(self) -> None:
        """Initialize the daily active users prometheus metric."""
        self.counter = Gauge("unique_daily_users", "Unique daily users counter")
        self.users: set[str] = set()
        self.day = datetime.now().date()

    def add_user(self, user_id: str) -> None:
        """Add a user to the daily active users if not already present."""
        self.users.add(user_id)
        logging.info("Current unique users: %s ", self.users)
        self.counter.set(len(self.users))

    def check_day(self) -> None:
        """Check if the day has changed and reset the users and counter."""
        if self.day != datetime.now().date():
            logging.debug("Resetting daily active users")
            self.users.clear()
            self.day = datetime.now().date()
            self.counter.set(0)
