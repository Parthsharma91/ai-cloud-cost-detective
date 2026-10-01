from datetime import date
from unittest.mock import patch

from backend.app.core.date_utils import get_current_and_previous_month_periods


def test_get_current_and_previous_month_periods():
    fake_today = date(2026, 9, 29)

    with patch(
        "backend.app.core.date_utils.date"
    ) as mock_date:
        mock_date.today.return_value = fake_today

        result = get_current_and_previous_month_periods()

    assert result == {
        "current_start": "2026-09-01",
        "current_end": "2026-09-30",
        "previous_start": "2026-08-01",
        "previous_end": "2026-09-01",
    }


def test_get_current_and_previous_month_periods_january():
    fake_today = date(2027, 1, 15)

    with patch(
        "backend.app.core.date_utils.date"
    ) as mock_date:
        mock_date.today.return_value = fake_today

        result = get_current_and_previous_month_periods()

    assert result == {
        "current_start": "2027-01-01",
        "current_end": "2027-01-16",
        "previous_start": "2026-12-01",
        "previous_end": "2027-01-01",
    }