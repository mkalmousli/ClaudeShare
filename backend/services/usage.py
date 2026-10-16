"""Per-user weighted-token usage, built from the user's own Claude logs."""
import asyncio
import time
from datetime import datetime, timezone

from ..config import DEFAULT_PERIOD, DEFAULT_SHARE, HISTORY_DAYS, WEIGHTS
from ..models import User
from . import capacity, fs_client, planusage, procs
from .periods import bounds

LIVE_WINDOW_SECONDS = 120
_state: dict[str, dict] = {}
_locks: dict[str, asyncio.Lock] = {}


def weigh(tokens: dict) -> float:
    return sum(tokens.get(key, 0) * weight for key, weight in WEIGHTS.items())


async def refresh(user: User) -> None:
    state = _state.setdefault(user.name, {"offsets": {}, "events": {}})
    async with _locks.setdefault(user.name, asyncio.Lock()):
        since = time.time() - HISTORY_DAYS * 86400
        reply = await fs_client.call(user, "usage", offsets=state["offsets"], since=since)
        state["offsets"] = reply["offsets"]
        for event in reply["events"]:
            state["events"][event["id"]] = event  # later duplicate lines win


def _window(period: str, plan: dict | None) -> tuple[datetime, datetime]:
    """Weekly periods follow the plan's own reset time when it is known."""
    return (period == "week" and capacity.plan_week(plan)) or bounds(datetime.now(timezone.utc), period)


def _in_window(events, start: datetime, end: datetime) -> list[dict]:
    return [e for e in events if start.timestamp() <= e["ts"] < end.timestamp()]


def _everyone_used(start: datetime, end: datetime) -> float:
    return sum(weigh(e["tokens"]) for st in _state.values() for e in _in_window(st["events"].values(), start, end))


def _sessions(events: list[dict], live: bool) -> list[dict]:
    grouped: dict[str, dict] = {}
    for event in events:
        row = grouped.setdefault(event["session"], {"id": event["session"], "project": event["project"],
                                                    "started": event["ts"], "last": event["ts"],
                                                    "messages": 0, "tokens": 0.0})
        row["started"], row["last"] = min(row["started"], event["ts"]), max(row["last"], event["ts"])
        row["messages"] += 1
        row["tokens"] += weigh(event["tokens"])
    now = time.time()
    for row in grouped.values():
        row["live"] = live and now - row["last"] < LIVE_WINDOW_SECONDS
    return sorted(grouped.values(), key=lambda r: r["last"], reverse=True)


def snapshot(user: User) -> dict:
    plan, period, share = planusage.cached(), user.period or DEFAULT_PERIOD, user.share or DEFAULT_SHARE
    start, end = _window(period, plan)
    events = _in_window(_state.get(user.name, {"events": {}})["events"].values(), start, end)
    budget = capacity.estimate(plan, _everyone_used(*_window("week", plan)), period) * share / 100
    used = sum(weigh(e["tokens"]) for e in events)
    live = bool(procs.claude_procs(user.uid))
    return {"used": used, "budget": budget, "share": share, "period": period, "percent": 100 * used / budget if budget else 0.0,
            "resets_at": end.timestamp(), "blocked": bool(budget) and used >= budget,
            "sessions": _sessions(events, live)}
