"""Spawn a login shell on a pty, running as the target user."""
import fcntl
import os
import pty
import struct
import subprocess
import termios

from ..config import user_env
from ..models import User
from . import limits


def set_size(fd: int, cols: int, rows: int) -> None:
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))


def _take_tty() -> None:
    fcntl.ioctl(0, termios.TIOCSCTTY, 0)


def safe_cwd(user: User, rel: str | None) -> str:
    target = os.path.normpath(os.path.join(user.home, (rel or "").lstrip("/")))
    inside = target == str(user.home) or target.startswith(f"{user.home}{os.sep}")
    return target if inside and os.path.isdir(target) else str(user.home)


def spawn(user: User, cwd: str | None, cols: int, rows: int) -> tuple[subprocess.Popen, int]:
    master, slave = pty.openpty()
    os.fchown(slave, user.uid, user.uid)
    set_size(master, max(cols, 2), max(rows, 2))
    setup = limits.child_setup(user)
    proc = subprocess.Popen(
        ["/bin/bash", "--login"], stdin=slave, stdout=slave, stderr=slave, cwd=safe_cwd(user, cwd),
        env=user_env(user.name, user.home), user=user.uid, group=user.uid, extra_groups=[],
        start_new_session=True, preexec_fn=lambda: (_take_tty(), setup()), close_fds=True)
    os.close(slave)
    return proc, master
