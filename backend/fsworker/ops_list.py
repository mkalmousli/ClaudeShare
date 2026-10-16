import os

from .paths import OpError, resolve, to_rel


def _entry(path, name: str) -> dict | None:
    full = path / name
    try:
        low = os.lstat(full)
        stat, broken = low, False
        if os.path.islink(full):
            try:
                stat = os.stat(full)
            except OSError:
                broken = True
        is_dir = not broken and os.path.isdir(full)
        return {"name": name, "isDir": is_dir, "size": stat.st_size, "mtime": stat.st_mtime,
                "mode": stat.st_mode & 0o7777, "isLink": os.path.islink(full)}
    except OSError:
        return None


def list_dir(path: str = "/") -> dict:
    target = resolve(path)
    if not target.is_dir():
        raise OpError("Not a folder")
    entries = [e for e in (_entry(target, n) for n in os.listdir(target)) if e]
    return {"path": to_rel(target), "entries": entries}


def stat(path: str = "/") -> dict:
    st = os.stat(resolve(path))
    return {"isDir": os.path.isdir(resolve(path)), "size": st.st_size,
            "mtime": st.st_mtime, "mode": st.st_mode & 0o7777}


OPS = {"list": list_dir, "stat": stat}
