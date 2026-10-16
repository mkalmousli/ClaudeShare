"""Whole-plan usage (5h / weekly %) read with the shared source login. Best effort."""
import time

import httpx

from ..config import OAUTH_USAGE_URL, PLAN_CACHE_SECONDS
from . import credsync

_cache: tuple[float, dict | None] = (0.0, None)


def _pick(raw: dict, key: str) -> tuple[float | None, str | None]:
    part = raw.get(key) or {}
    return part.get("utilization"), part.get("resets_at")


async def plan_usage() -> dict | None:
    global _cache
    if time.time() - _cache[0] < PLAN_CACHE_SECONDS:
        return _cache[1]
    result = None
    token = (credsync.read_source() or {}).get("claudeAiOauth", {}).get("accessToken")
    if token:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                reply = await client.get(OAUTH_USAGE_URL, headers={
                    "Authorization": f"Bearer {token}", "anthropic-beta": "oauth-2025-04-20"})
            if reply.status_code == 200:
                raw = reply.json()
                five, five_reset = _pick(raw, "five_hour")
                week, week_reset = _pick(raw, "seven_day")
                result = {"five_hour": five, "five_hour_resets": five_reset,
                          "seven_day": week, "seven_day_resets": week_reset}
        except (httpx.HTTPError, ValueError):
            result = None
    _cache = (time.time(), result)
    return result
