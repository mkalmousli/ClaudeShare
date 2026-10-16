"""`claudeshare uninstall`: remove the service and command; optionally delete all data."""
import shutil
import subprocess
import sys
from pathlib import Path

from rich.prompt import Confirm, Prompt

from . import output as out

PROJECT = Path(__file__).resolve().parent.parent
CONFIRM_WORD = "delete"


def sudo(*cmd: str, check: bool = True) -> int:
    code = subprocess.run(["sudo", *cmd], cwd=PROJECT).returncode
    if code and check:
        out.fail(f"Failed: {' '.join(cmd)}")
        raise SystemExit(1)
    return code


def confirmed(purge: bool, assume_yes: bool) -> bool:
    if assume_yes:
        return True
    if purge:
        out.warn("--purge permanently deletes EVERY user's files, keys and settings.")
        return Prompt.ask(f"Type [bold]{CONFIRM_WORD}[/] to continue", console=out.console) == CONFIRM_WORD
    return Confirm.ask("Remove the ClaudeShare service and command? (user data is kept)", console=out.console, default=False)


def purge_data() -> None:
    out.console.print("[dim]Deleting data volume, image, and local settings…[/]")
    sudo("docker", "compose", "--profile", "cloudflare", "--profile", "cloudflare-local", "down", "-v", "--rmi", "local", check=False)
    for name in (".env", ".cloudflared"):
        target = PROJECT / name
        shutil.rmtree(target, ignore_errors=True) if target.is_dir() else target.unlink(missing_ok=True)
        target.exists() and sudo("rm", "-rf", str(target), check=False)


def run(purge: bool, assume_yes: bool) -> int:
    if not confirmed(purge, assume_yes):
        out.warn("Cancelled; nothing was changed.")
        return 1
    sudo(sys.executable, "-m", "system.install", "--remove")
    out.ok("Service stopped and removed")
    purge and purge_data()
    purge and out.ok("All data deleted")
    purge or out.console.print("[dim]Your data volume and .env were kept. Reinstall later and everything is back.[/]")
    out.console.print("[dim]Cloudflare tunnel/DNS records are not touched; remove them in the Cloudflare dashboard if you want.[/]")
    out.ok("Removing the `claudeshare` command… bye")
    subprocess.run(["uv", "tool", "uninstall", "claudeshare"], capture_output=True)
    return 0
