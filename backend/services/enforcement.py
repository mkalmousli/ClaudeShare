"""Sampling and enforcement of per-user RAM and CPU limits (called by the watcher every tick)."""
import time

import psutil

from ..config import MB
from ..models import User
from . import limits
from .limits import core_set, effective

CPU_GRACE = 1.15  # tolerate brief bursts above the limit
CPU_STRIKES = 2  # consecutive over-limit ticks before throttling
NICE_THROTTLED = 19
EVENT_TTL_SECONDS = 600
_last: dict[str, dict] = {}
_strikes: dict[str, int] = {}
_events: dict[str, tuple[float, str]] = {}


def group_by_uid() -> dict[int, list[psutil.Process]]:
    groups: dict[int, list[psutil.Process]] = {}
    for proc in psutil.process_iter(["uids"]):
        if proc.info.get("uids"):
            groups.setdefault(proc.info["uids"].real, []).append(proc)
    return groups


def _safe(call, default=0):
    try:
        return call()
    except (psutil.Error, OSError):
        return default


def measure(user: User, procs: list[psutil.Process]) -> dict:
    stats = {"mem_mb": sum(_safe(lambda p=p: p.memory_info().rss) for p in procs) / MB,
             "cpu": sum(_safe(lambda p=p: p.cpu_percent(None)) for p in procs) / 100, "procs": len(procs)}
    _last[user.name] = {**stats, "disk_mb": limits.disk_bytes(user.name) / MB}
    return stats


def _note(name: str, text: str) -> None:
    _events[name] = (time.time(), text)


def _throttle(user: User, procs, stats: dict, lim: dict) -> None:
    _strikes[user.name] = _strikes.get(user.name, 0) + 1 if stats["cpu"] > lim["cpu"] * CPU_GRACE else 0
    slow = _strikes[user.name] >= CPU_STRIKES
    calm = stats["cpu"] < lim["cpu"] * 0.7
    cores = core_set(lim["cpu"], user.uid)
    for proc in procs:
        if slow or calm:
            _safe(lambda p=proc: p.nice(NICE_THROTTLED if slow else 0))
        if cores:
            _safe(lambda p=proc: p.cpu_affinity(cores))
    slow and stats["cpu"] > 0 and _note(user.name, f"CPU is limited to {lim['cpu']:g} core(s); your processes are slowed down.")


def enforce(user: User, procs: list[psutil.Process], stats: dict) -> None:
    lim = effective(user)
    if stats["mem_mb"] > lim["mem_mb"] and procs:
        victim = max(procs, key=lambda p: _safe(lambda: p.memory_info().rss))
        label, size = _safe(victim.name, "process"), _safe(lambda: victim.memory_info().rss) / MB
        _safe(victim.kill)
        _note(user.name, f"Stopped {label} ({size:.0f} MB): memory limit is {lim['mem_mb']:.0f} MB.")
    _throttle(user, procs, stats, lim)


def report(user: User) -> dict:
    lim, now = effective(user), _last.get(user.name, {"mem_mb": 0.0, "cpu": 0.0, "procs": 0, "disk_mb": 0.0})
    when, text = _events.get(user.name, (0, ""))
    return {"mem_used": now["mem_mb"], "mem_limit": lim["mem_mb"], "cpu_used": now["cpu"], "cpu_limit": lim["cpu"],
            "procs_used": now["procs"], "procs_limit": lim["procs"], "disk_used": now["disk_mb"],
            "disk_limit": lim["disk_mb"], "notice": text if time.time() - when < EVENT_TTL_SECONDS else ""}
