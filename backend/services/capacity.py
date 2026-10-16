"""How big is the plan, in weighted tokens? Measured from the plan's own utilisation figure."""
from datetime import datetime, timedelta, timezone

from ..config import FALLBACK_PLAN_TOKENS, MIN_PLAN_PERCENT, PERIOD_WEEKS


def plan_week(plan: dict | None) -> tuple[datetime, datetime] | None:
    """The plan's real 7-day window, taken from the reset time Claude reports."""
    stamp = (plan or {}).get("seven_day_resets")
    if not stamp:
        return None
    end = datetime.fromisoformat(stamp.replace("Z", "+00:00")).astimezone(timezone.utc)
    return end - timedelta(days=7), end


def estimate(plan: dict | None, used_by_everyone: float, period: str = "week") -> float:
    """tokens per 100% of the plan = what we saw consumed / the plan's utilisation.

    Usage made outside ClaudeShare is invisible here, so the estimate errs on the cautious side.
    """
    percent = (plan or {}).get("seven_day")
    weekly = used_by_everyone / percent * 100 if percent and percent >= MIN_PLAN_PERCENT and used_by_everyone > 0 else FALLBACK_PLAN_TOKENS
    return weekly * PERIOD_WEEKS[period]
