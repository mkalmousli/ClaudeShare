"""Run filesystem helpers as the target user (the kernel enforces isolation)."""
import asyncio
import json
import sys

from ..config import APP_ROOT, user_env
from ..models import User
from . import limits


class FsError(Exception):
    pass


async def call(user: User, op: str, **args) -> dict:
    if op in limits.WRITE_OPS and limits.disk_exceeded(user):
        raise FsError("Disk quota reached. Delete some files to free space.")
    env = {**user_env(user.name, user.home), "PYTHONPATH": str(APP_ROOT), "PYTHONDONTWRITEBYTECODE": "1"}
    proc = await asyncio.create_subprocess_exec(
        sys.executable, "-s", "-m", "backend.fsworker",
        stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        env=env, cwd=str(user.home), user=user.uid, group=user.uid, extra_groups=[],
    )
    out, err = await proc.communicate(json.dumps({"op": op, "args": args}).encode())
    try:
        reply = json.loads(out)
    except ValueError:
        raise FsError(err.decode().strip().splitlines()[-1] if err.strip() else "File service failed")
    if not reply["ok"]:
        raise FsError(reply["error"])
    return reply["data"]
