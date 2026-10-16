"""Implementations of the claudeshare sub-commands."""
import sys
import time
import urllib.request
from pathlib import Path

from . import output as out
from .privileged import helper, state

USER_COMMANDS = {"add", "list", "passwd", "del", "limit", "sessions"}


def _url(info: dict[str, str]) -> str:
    env = Path(info.get("project", ".")) / ".env"
    try:
        lines = dict(line.split("=", 1) for line in env.read_text().splitlines() if "=" in line and not line.startswith("#"))
        return lines.get("PUBLIC_URL", "")
    except OSError:
        return ""


def _wait_up(port: str = "3000", seconds: int = 60) -> bool:
    for _ in range(seconds):
        try:
            if urllib.request.urlopen(f"http://127.0.0.1:{port}/healthz", timeout=2).status == 200:
                return True
        except OSError:
            time.sleep(1)
    return False


def on() -> int:
    code = helper("start").returncode
    if code:
        return code
    out.console.print("[dim]Starting…[/]")
    info = state()
    out.ok(f"ClaudeShare is [bold green]on[/]  {_url(info)}") if _wait_up() else out.warn("Started, but not answering yet. Check `claudeshare logs`.")
    return 0


def off() -> int:
    code = helper("stop").returncode
    code or out.ok("ClaudeShare is [bold yellow]off[/]. Your data is kept; `claudeshare on` brings it back.")
    return code


def restart() -> int:
    code = helper("restart").returncode
    code or out.ok("Restarted")
    return code


def boot(setting: str) -> int:
    code = helper("enable" if setting == "on" else "disable").returncode
    code or out.ok(f"Start at boot: [bold]{setting}[/]")
    return code


def status() -> int:
    info = state()
    out.console.print("\n[bold]ClaudeShare[/]")
    out.state_line("service", info.get("active", "?"), {"active"})
    out.state_line("at boot", info.get("enabled", "?"), {"enabled"})
    out.state_line("address", _url(info) or "(not set)", {"x"})
    if info.get("active") == "active":
        return helper("admin", "status").returncode
    out.console.print()
    return 0


def logs(follow: bool) -> int:
    return helper("logs", *(["-f"] if follow else [])).returncode


def login() -> int:
    return helper("login").returncode


def update() -> int:
    out.console.print("[dim]Rebuilding the image and restarting…[/]")
    return helper("update").returncode


def user(args: list[str]) -> int:
    if not args or args[0] not in USER_COMMANDS:
        out.fail("usage: claudeshare user add|list|passwd|del|limit|sessions …")
        return 2
    return helper("admin", *args).returncode
