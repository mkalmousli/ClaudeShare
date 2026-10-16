"""Enforcement loop: refresh usage, publish the block flag, stop `claude` over budget."""
import asyncio

from ..config import BLOCKED_DIR, WATCH_SECONDS
from ..models import User
from . import procs, store, usage


def _flag(user: User):
    return BLOCKED_DIR / user.name


def apply(user: User, snap: dict) -> None:
    if snap["blocked"]:
        _flag(user).write_text(str(int(snap["resets_at"])))
        procs.stop_claude(user.uid)
    else:
        _flag(user).unlink(missing_ok=True)


async def tick() -> None:
    for user in store.all_users():
        try:
            await usage.refresh(user)
            apply(user, usage.snapshot(user))
        except Exception as exc:  # one broken account must not stop the loop
            print(f"[watcher] {user.name}: {exc}", flush=True)
    live = {u.name for u in store.all_users()}
    for flag in BLOCKED_DIR.iterdir():
        if flag.name not in live:
            flag.unlink(missing_ok=True)


async def loop() -> None:
    BLOCKED_DIR.mkdir(parents=True, exist_ok=True)
    BLOCKED_DIR.chmod(0o755)
    while True:
        await tick()
        await asyncio.sleep(WATCH_SECONDS)
