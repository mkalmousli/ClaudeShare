import re
import shutil
import subprocess

from .paths import OpError, check_name, resolve, to_rel, unique

ARCHIVE_EXT = re.compile(r"\.(zip|tar\.gz|tgz|tar\.bz2|tbz2|tar\.xz|txz|tar)$", re.I)


def _run(cmd: list[str], cwd) -> None:
    done = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if done.returncode:
        raise OpError((done.stderr.strip().splitlines() or ["Archive command failed"])[-1])


def compress(paths: list[str], dest: str, name: str) -> dict:
    folder = resolve(dest)
    out = unique(folder, check_name(name), "num")
    members = [resolve(p).relative_to(folder).as_posix() for p in paths]
    if out.lower().endswith(".zip"):
        _run(["zip", "-r", "-q", "-y", out, "--", *members], folder)
    else:
        _run(["tar", "-czf", out, "--", *members], folder)
    return {"name": out}


def extract(path: str) -> dict:
    src = resolve(path)
    if not ARCHIVE_EXT.search(src.name):
        raise OpError("Unsupported archive type")
    out = src.parent / unique(src.parent, ARCHIVE_EXT.sub("", src.name) or "extracted", "num")
    out.mkdir()
    try:
        if src.name.lower().endswith(".zip"):
            _run(["unzip", "-q", str(src), "-d", str(out)], src.parent)
        else:
            _run(["tar", "-xf", str(src), "-C", str(out)], src.parent)
    except OpError:
        shutil.rmtree(out, ignore_errors=True)
        raise
    return {"path": to_rel(out)}


OPS = {"compress": compress, "extract": extract}
