"""Usage period boundaries (all UTC)."""
from datetime import datetime, timedelta, timezone

from ..config import RESET_HOUR, RESET_WEEKDAY


def _month_start(year: int, month: int, hour: int) -> datetime:
    return datetime(year, month, 1, hour, tzinfo=timezone.utc)


def bounds(now: datetime, period: str, weekday: int = RESET_WEEKDAY, hour: int = RESET_HOUR):
    """Return (start, end) of the period containing `now`."""
    day_start = now.replace(hour=hour, minute=0, second=0, microsecond=0)
    if day_start > now:
        day_start -= timedelta(days=1)
    if period == "day":
        return day_start, day_start + timedelta(days=1)
    if period == "week":
        start = day_start - timedelta(days=(day_start.weekday() - weekday) % 7)
        return start, start + timedelta(days=7)
    start = _month_start(day_start.year, day_start.month, hour)
    if start > now:
        prev = (start - timedelta(days=1))
        start = _month_start(prev.year, prev.month, hour)
    end_ref = start + timedelta(days=32)
    return start, _month_start(end_ref.year, end_ref.month, hour)
