"""Find (and stop) the `claude` processes that belong to a user."""
import os

import psutil

from ..config import CLAUDE_REAL

_REAL = os.path.realpath(CLAUDE_REAL)


def _is_claude(proc: psutil.Process) -> bool:
    try:
        if proc.name() == "claude":
            return True
        return any(os.path.realpath(arg) == _REAL for arg in proc.cmdline()[:2] if arg.startswith("/"))
    except (psutil.Error, OSError):
        return False


def claude_procs(uid: int) -> list[psutil.Process]:
    found = []
    for proc in psutil.process_iter(["uids"]):
        uids = proc.info.get("uids")
        if uids and uids.real == uid and _is_claude(proc):
            found.append(proc)
    return found


def stop_claude(uid: int) -> int:
    procs = claude_procs(uid)
    for proc in procs:
        try:
            proc.kill()
        except psutil.Error:
            pass
    return len(procs)
