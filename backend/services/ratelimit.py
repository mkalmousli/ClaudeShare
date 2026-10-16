"""Tiny in-memory failure counter for brute-force protection."""
import time

WINDOW_SECONDS = 600
_hits: dict[str, list[float]] = {}


def _recent(key: str) -> list[float]:
    cutoff = time.time() - WINDOW_SECONDS
    _hits[key] = [t for t in _hits.get(key, []) if t > cutoff]
    return _hits[key]


def blocked(key: str, limit: int) -> bool:
    return len(_recent(key)) >= limit


def record(key: str) -> None:
    _recent(key).append(time.time())
