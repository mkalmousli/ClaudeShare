"""Per-user RAM / CPU / process / disk limits, sampled and enforced by the watcher."""
import math
import os
import resource
import time

from ..config import DEFAULT_LIMITS, DISK_REFRESH_OVER_SECONDS, DISK_REFRESH_SECONDS, MB
from ..models import User

WRITE_OPS = {"mkdir", "touch", "write", "copy", "compress", "extract", "unique"}
_disk: dict[str, tuple[float, float]] = {}  # name -> (checked at, bytes)


def effective(user: User) -> dict[str, float]:
    return {key: (getattr(user, key) if getattr(user, key) is not None else default) for key, default in DEFAULT_LIMITS.items()}


def core_set(cpu: float, uid: int) -> list[int] | None:
    """Which cores a user may run on: ceil(limit) of them, spread across users by uid."""
    total, wanted = os.cpu_count() or 1, max(1, math.ceil(cpu))
    return None if wanted >= total else sorted((uid + step) % total for step in range(wanted))


def child_setup(user: User):
    """Run in the shell right after fork: caps the process count and pins CPU cores."""
    lim = effective(user)
    cores, nproc = core_set(lim["cpu"], user.uid), int(lim["procs"])

    def setup() -> None:
        resource.setrlimit(resource.RLIMIT_NPROC, (nproc, nproc))
        if cores:
            os.sched_setaffinity(0, cores)
    return setup


async def refresh_disk(user: User, measure_disk) -> None:
    checked, _size = _disk.get(user.name, (0.0, 0.0))
    ttl = DISK_REFRESH_OVER_SECONDS if disk_exceeded(user) else DISK_REFRESH_SECONDS
    if time.time() - checked >= ttl:
        _disk[user.name] = (time.time(), (await measure_disk(user))["bytes"])


def disk_exceeded(user: User) -> bool:
    return disk_bytes(user.name) / MB >= effective(user)["disk_mb"]


def disk_bytes(name: str) -> float:
    return _disk.get(name, (0, 0.0))[1]
