"""Calls into the root helper through sudo (passwordless for the `claudeshare` group only)."""
import subprocess
import sys

from .output import fail

HELPER = "/usr/libexec/claudeshare/ctl.py"


def allowed() -> bool:
    return subprocess.run(["sudo", "-n", "-l", HELPER], capture_output=True).returncode == 0


def helper(*args: str, capture: bool = False) -> subprocess.CompletedProcess:
    """Run the helper; stdin/stdout stay attached to the terminal unless `capture` is set."""
    if not allowed():
        fail("You are not set up to control ClaudeShare yet. Run `uv run setup` once, then log out and in again.")
        sys.exit(1)
    return subprocess.run(["sudo", "-n", HELPER, *args], capture_output=capture, text=capture)


def state() -> dict[str, str]:
    out = helper("state", capture=True)
    return dict(line.split("=", 1) for line in out.stdout.splitlines() if "=" in line)
