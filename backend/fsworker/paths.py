"""Path mapping inside the worker, which runs as the user's own uid."""
import os
import posixpath
from pathlib import Path


class OpError(Exception):
    """A user-facing failure (shown verbatim in the UI)."""


def home() -> Path:
    return Path(os.environ["HOME"])


def resolve(rel: str | None) -> Path:
    """Virtual '/' is the home folder; '..' can never climb above it."""
    clean = posixpath.normpath("/" + (rel or ""))
    return home() / clean.lstrip("/")


def to_rel(path: Path) -> str:
    rel = os.path.relpath(path, home())
    return "/" if rel == "." else "/" + rel.replace(os.sep, "/")


def exists(path: Path) -> bool:
    return os.path.lexists(path)


def unique(folder: Path, name: str, style: str = "copy") -> str:
    """'a copy.txt' / 'a copy 2.txt' (style copy), or 'a (1).txt' (style num)."""
    if not exists(folder / name):
        return name
    stem, ext = os.path.splitext(name) if os.path.splitext(name)[0] else (name, "")
    for idx in range(1, 10_000):
        mid = f" ({idx})" if style == "num" else (" copy" if idx == 1 else f" copy {idx}")
        if not exists(folder / f"{stem}{mid}{ext}"):
            return f"{stem}{mid}{ext}"
    raise OpError("Too many name collisions")


def check_name(name: str | None) -> str:
    if not name or "/" in name or name in (".", ".."):
        raise OpError("Invalid name")
    return name
