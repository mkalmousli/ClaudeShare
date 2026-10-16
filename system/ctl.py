#!/usr/bin/python3 -I
"""Root helper for ClaudeShare. The `claudeshare` sudoers group may run ONLY this file.

Standard library only. Every argument is validated; nothing is passed through a shell.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from ctl_args import admin_args  # noqa: E402

CONF = "/etc/claudeshare/project"
UNIT = "claudeshare.service"
ADMIN_ENV = ["-e", "FORCE_COLOR=1", "-e", "COLUMNS=110"]


def die(message: str, code: int = 2) -> None:
    sys.stderr.write(message + "\n")
    sys.exit(code)


def project() -> str:
    try:
        return open(CONF).read().strip()
    except OSError:
        die("ClaudeShare is not installed (run `uv run setup` first).")


def systemctl(*args: str) -> None:
    os.execvp("systemctl", ["systemctl", *args])


def compose(*args: str) -> None:
    os.chdir(project())
    os.execvp("docker", ["docker", "compose", *args])


def is_active() -> bool:
    return subprocess.run(["systemctl", "is-active", "--quiet", UNIT]).returncode == 0


def need_running() -> None:
    if not is_active():
        die("ClaudeShare is off. Start it with: claudeshare on", 3)


def main(argv: list[str]) -> None:
    cmd, rest = (argv or [""])[0], argv[1:]
    simple = {"start", "stop", "restart", "enable", "disable"}
    if cmd in simple and not rest:
        systemctl(cmd, UNIT)
    elif cmd == "state" and not rest:
        active = subprocess.run(["systemctl", "is-active", UNIT], capture_output=True, text=True).stdout.strip()
        enabled = subprocess.run(["systemctl", "is-enabled", UNIT], capture_output=True, text=True).stdout.strip()
        print(f"active={active or 'unknown'}\nenabled={enabled or 'unknown'}\nproject={project()}")
    elif cmd == "logs" and rest in ([], ["-f"]):
        compose("logs", "--no-color", "--tail", "200", *rest)
    elif cmd == "update" and not rest:
        subprocess.run(["docker", "compose", "build"], cwd=project(), check=True)
        systemctl("restart", UNIT)
    elif cmd == "login" and not rest:
        need_running()
        compose("exec", "-e", "HOME=/data/source", "app", "claude")
    elif cmd == "admin":
        args = admin_args(rest)  # validate before touching anything
        need_running()
        compose("exec", "-T", *ADMIN_ENV, "app", "python", "-m", "backend.admin", *args)
    else:
        die("usage: ctl.py start|stop|restart|enable|disable|state|logs [-f]|update|login|admin ...")


if __name__ == "__main__":
    main(sys.argv[1:])
