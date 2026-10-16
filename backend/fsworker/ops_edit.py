import os

from .paths import OpError, check_name, exists, resolve, to_rel, unique

TEXT_LIMIT = 2 * 1024 * 1024


def mkdir(path: str, parents: bool = False) -> dict:
    resolve(path).mkdir(parents=parents, exist_ok=parents)
    return {}


def touch(path: str) -> dict:
    with open(resolve(path), "x"):
        pass
    return {}


def rename(path: str, to: str) -> dict:
    src = resolve(path)
    dst = src.parent / check_name(to)
    if exists(dst):
        raise OpError(f'"{to}" already exists')
    src.rename(dst)
    return {"path": to_rel(dst)}


def chmod(path: str, mode: str) -> dict:
    if not (mode.isdigit() and 3 <= len(mode) <= 4 and set(mode) <= set("01234567")):
        raise OpError("Mode must be octal, e.g. 644")
    os.chmod(resolve(path), int(mode, 8))
    return {}


def read(path: str) -> dict:
    target = resolve(path)
    if target.is_dir():
        raise OpError("Is a folder")
    size = target.stat().st_size
    if size > TEXT_LIMIT:
        return {"binary": True, "size": size, "content": ""}
    raw = target.read_bytes()
    if b"\0" in raw:
        return {"binary": True, "size": size, "content": ""}
    return {"binary": False, "size": size, "content": raw.decode("utf-8", "replace")}


def write(path: str, content: str) -> dict:
    resolve(path).write_text(content)
    return {}


def unique_path(path: str, overwrite: bool = False) -> dict:
    target = resolve(path)
    if overwrite:
        return {"path": to_rel(target)}
    return {"path": to_rel(target.parent / unique(target.parent, target.name, "num"))}


OPS = {"mkdir": mkdir, "touch": touch, "rename": rename, "chmod": chmod,
       "read": read, "write": write, "unique": unique_path}
