"""users.json persistence (atomic writes, mtime-cached reads)."""
import json
import os
import threading

from ..config import DATA, USERS_FILE
from ..models import User

_lock = threading.RLock()
_cache: tuple[float, dict[str, User]] | None = None


def load() -> dict[str, User]:
    global _cache
    with _lock:
        try:
            mtime = USERS_FILE.stat().st_mtime_ns
        except FileNotFoundError:
            return {}
        if _cache and _cache[0] == mtime:
            return _cache[1]
        raw = json.loads(USERS_FILE.read_text())
        users = {n: User.from_dict(n, r) for n, r in raw.get("users", {}).items()}
        _cache = (mtime, users)
        return users


def save(users: dict[str, User]) -> None:
    global _cache
    with _lock:
        DATA.mkdir(parents=True, exist_ok=True)
        os.chmod(DATA, 0o711)  # users traverse /data to reach their home but cannot list it
        tmp = USERS_FILE.with_suffix(".tmp")
        payload = {"users": {n: u.to_dict() for n, u in users.items()}}
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as fh:
            json.dump(payload, fh, indent=2)
        os.replace(tmp, USERS_FILE)
        _cache = None


def get(name: str) -> User | None:
    return load().get(name)


def all_users() -> list[User]:
    return sorted(load().values(), key=lambda u: u.name)


def update(name: str, **changes) -> User:
    with _lock:
        users = dict(load())
        if name not in users:
            raise KeyError(name)
        for key, value in changes.items():
            setattr(users[name], key, value)
        save(users)
        return users[name]


def next_uid(base: int) -> int:
    return max([u.uid for u in load().values()] + [base - 1]) + 1
