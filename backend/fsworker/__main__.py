"""Entry point: `python -m backend.fsworker` reads {"op","args"} on stdin, prints JSON.

Always started by the server with the target user's uid/gid, never as root.
"""
import json
import sys

from . import ops_archive, ops_edit, ops_list, ops_move, ops_usage
from .paths import OpError

OPS = {**ops_list.OPS, **ops_edit.OPS, **ops_move.OPS, **ops_archive.OPS, **ops_usage.OPS}

ERRORS = {FileNotFoundError: "No such file or folder", PermissionError: "Permission denied",
          FileExistsError: "Already exists", IsADirectoryError: "Is a folder",
          NotADirectoryError: "Not a folder"}


def main() -> None:
    request = json.load(sys.stdin)
    try:
        result = OPS[request["op"]](**request.get("args", {}))
        print(json.dumps({"ok": True, "data": result}))
    except OpError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
    except tuple(ERRORS) as exc:
        message = next(msg for typ, msg in ERRORS.items() if isinstance(exc, typ))
        print(json.dumps({"ok": False, "error": message}))
    except Exception as exc:  # noqa: BLE001 - report instead of dumping a traceback to users
        print(json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"}))


main()
