"""Linux accounts backing each ClaudeShare user."""
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from ..config import HOMES, NAME_PATTERN, RESERVED_NAMES, UID_BASE
from ..models import User
from . import passwords, store

SKEL_BASHRC = Path(__file__).resolve().parent.parent / "skel_bashrc"


def valid_name(name: str) -> bool:
    return bool(re.match(NAME_PATTERN, name)) and name not in RESERVED_NAMES


def _run(*cmd: str) -> bool:
    return subprocess.run(cmd, capture_output=True).returncode == 0


def _setup_home(user: User) -> None:
    fresh = not user.home.exists()
    HOMES.mkdir(parents=True, exist_ok=True)
    os.chmod(HOMES, 0o711)
    if fresh:
        user.home.mkdir()
        shutil.copy(SKEL_BASHRC, user.home / ".bashrc")
        (user.home / ".bash_profile").write_text("[ -f ~/.bashrc ] && . ~/.bashrc\n")
        subprocess.run(["chown", "-R", f"{user.uid}:{user.uid}", str(user.home)], check=True)
    os.chmod(user.home, 0o700)
    os.chown(user.home, user.uid, user.uid)


def ensure_system_user(user: User) -> None:
    """Idempotent: /etc/passwd vanishes with the container, users.json does not."""
    if not _run("id", "-u", user.name):
        _run("groupadd", "-g", str(user.uid), user.name)
        if not _run("useradd", "-M", "-d", str(user.home), "-s", "/bin/bash",
                    "-u", str(user.uid), "-g", str(user.uid), user.name):
            raise RuntimeError(f"could not create system account for {user.name}")
    _setup_home(user)


def sync_all() -> None:
    for user in store.all_users():
        try:
            ensure_system_user(user)
        except Exception as exc:  # keep booting even if one account is broken
            print(f"[accounts] {user.name}: {exc}", flush=True)


def create(name: str, key: str) -> User:
    if not valid_name(name):
        raise ValueError("Name must be 2-24 chars: a-z, 0-9, '-' or '_', starting with a letter.")
    if store.get(name):
        raise ValueError(f'User "{name}" already exists.')
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    user = User(name, store.next_uid(UID_BASE), passwords.hash_key(key), created=stamp)
    ensure_system_user(user)
    users = dict(store.load())
    users[name] = user
    store.save(users)
    return user


def set_key(name: str, key: str) -> None:
    user = store.get(name)
    if not user:
        raise ValueError(f'No such user "{name}".')
    store.update(name, hash=passwords.hash_key(key), tv=user.tv + 1)


def remove(name: str, purge: bool) -> None:
    users = dict(store.load())
    if name not in users:
        raise ValueError(f'No such user "{name}".')
    user = users.pop(name)
    store.save(users)
    _run("pkill", "-KILL", "-u", name)
    _run("userdel", name)
    if purge:
        shutil.rmtree(user.home, ignore_errors=True)
