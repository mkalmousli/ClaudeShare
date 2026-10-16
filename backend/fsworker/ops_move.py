import os
import shutil

from .paths import OpError, exists, resolve, unique


def _inside(dest, src) -> bool:
    return dest == src or src in dest.parents


def move(paths: list[str], dest: str) -> dict:
    folder = resolve(dest)
    for rel in paths:
        src = resolve(rel)
        if _inside(folder, src):
            raise OpError("Cannot move a folder into itself")
        target = folder / src.name
        if target == src:
            continue
        if exists(target):
            raise OpError(f'"{src.name}" already exists in the destination')
        shutil.move(str(src), str(target))
    return {}


def copy(paths: list[str], dest: str) -> dict:
    folder = resolve(dest)
    for rel in paths:
        src = resolve(rel)
        if _inside(folder, src):
            raise OpError("Cannot copy a folder into itself")
        target = folder / unique(folder, src.name)
        if src.is_dir() and not src.is_symlink():
            shutil.copytree(src, target, symlinks=True)
        else:
            shutil.copy2(src, target, follow_symlinks=False)
    return {}


def remove(paths: list[str]) -> dict:
    for rel in paths:
        target = resolve(rel)
        if target == resolve("/"):
            raise OpError("Cannot delete your home folder")
        if target.is_dir() and not target.is_symlink():
            shutil.rmtree(target)
        elif exists(target):
            os.unlink(target)
    return {}


OPS = {"move": move, "copy": copy, "remove": remove}
