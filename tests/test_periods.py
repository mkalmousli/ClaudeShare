from datetime import datetime, timezone

from backend.services.periods import bounds


def at(*parts):
    return datetime(*parts, tzinfo=timezone.utc)


def test_week_starts_on_configured_weekday():
    start, end = bounds(at(2026, 10, 16, 12), "week", weekday=0, hour=0)  # a Friday
    assert start == at(2026, 10, 12) and end == at(2026, 10, 19)


def test_day_respects_reset_hour():
    start, _ = bounds(at(2026, 10, 16, 3), "day", hour=6)
    assert start == at(2026, 10, 15, 6)


def test_month_rolls_over_year():
    start, end = bounds(at(2026, 12, 20), "month", hour=0)
    assert start == at(2026, 12, 1) and end == at(2027, 1, 1)
