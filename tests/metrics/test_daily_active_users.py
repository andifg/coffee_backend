from unittest.mock import MagicMock, patch

import pytest

from coffee_backend.metrics.daily_active_users import DailyActiveUsersMetric


# pylint: disable=protected-access
@patch("coffee_backend.metrics.daily_active_users.Gauge")
def test_daily_active_users_metrics_add_multiple_users(
    gauge_mock: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test adding multiple users to the daily active users metric."""

    gauge_instance = MagicMock()

    gauge_mock.return_value = gauge_instance

    daily_active_users_metric = DailyActiveUsersMetric()

    daily_active_users_metric.add_user(user_id="test")

    gauge_mock.assert_called_once_with(
        "unique_daily_users", "Unique daily users counter"
    )

    gauge_instance.set.assert_called_once_with(1)

    daily_active_users_metric.add_user(user_id="test2")

    gauge_instance.set.assert_called_with(2)

    assert daily_active_users_metric.users == {"test", "test2"}

    assert "Current unique users: {'test'}" in caplog.text


@patch("coffee_backend.metrics.daily_active_users.Gauge")
@patch("coffee_backend.metrics.daily_active_users.datetime")
def test_daily_active_users_metrics_reset_on_date_change(
    mock_datetime: MagicMock,
    gauge_mock: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test resetting the daily active users metric on date change."""

    gauge_instance = MagicMock()

    gauge_mock.return_value = gauge_instance

    mock_datetime.now.return_value.date.return_value = 1

    daily_active_users_metric = DailyActiveUsersMetric()

    daily_active_users_metric.add_user(user_id="test")

    gauge_instance.set.assert_called_once_with(1)

    mock_datetime.now.return_value.date.return_value = 2

    daily_active_users_metric.check_day()

    gauge_instance.set.assert_called_with(0)


# pylint: enable=protected-access
