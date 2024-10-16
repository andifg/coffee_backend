import logging


class HealthCheckFilter(logging.Filter):
    """Filter to exclude health check logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("/health") == -1
