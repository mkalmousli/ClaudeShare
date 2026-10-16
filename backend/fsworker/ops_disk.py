"""Disk used by the user's home (allocated blocks, symlinks not followed)."""
import os

from .paths import home


def disk() -> dict:
    total, stack = 0, [str(home())]
    while stack:
        try:
            with os.scandir(stack.pop()) as entries:
                for entry in entries:
                    info = entry.stat(follow_symlinks=False)
                    total += info.st_blocks * 512
                    if entry.is_dir(follow_symlinks=False):
                        stack.append(entry.path)
        except OSError:
            continue
    return {"bytes": total}


OPS = {"disk": disk}
