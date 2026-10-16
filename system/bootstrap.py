"""`uv run install`: put ClaudeShare on this machine. Configuration happens later, in `claudeshare setup`."""
import argparse
import getpass
import shutil
import subprocess
import sys
from pathlib import Path

from rich.console import Console

console = Console(highlight=False)
PROJECT = Path(__file__).resolve().parent.parent


def step(text: str) -> None:
    console.print(f"[bold cyan]›[/] {text}")


def need(tool: str, hint: str) -> str:
    path = shutil.which(tool)
    if not path:
        console.print(f"[bold red]✖[/] {tool} not found. {hint}")
        raise SystemExit(1)
    return path


def run(*cmd: str) -> None:
    if subprocess.run(cmd, cwd=PROJECT).returncode:
        console.print(f"[bold red]✖[/] Failed: {' '.join(cmd)}")
        raise SystemExit(1)


def main() -> None:
    argparse.ArgumentParser(prog="install", description="Install ClaudeShare: command, system service, image.").parse_args()
    console.print("[bold #d97757]ClaudeShare[/]  [dim]install[/]\n")
    need("docker", "Install Docker first: https://docs.docker.com/engine/install/")
    uv = need("uv", "Install uv first: https://docs.astral.sh/uv/")
    step("Installing the `claudeshare` command (editable, so `git pull` updates it)…")
    run(uv, "tool", "install", "--editable", "--force", str(PROJECT))
    subprocess.run([uv, "tool", "update-shell"], capture_output=True)
    step("Registering the system service (uses sudo once)…")
    run("sudo", sys.executable, "-m", "system.install", "--user", getpass.getuser(), "--project", str(PROJECT), "--no-start")
    step("Building the image (the first time takes a few minutes)…")
    run("docker", "compose", "build")
    console.print("\n[bold green]✔ Installed.[/] Open a new shell if `claudeshare` is not found, then run:\n\n"
                  "    [bold]claudeshare setup[/]\n\n[dim]Remove everything later with `claudeshare uninstall`.[/]\n")


if __name__ == "__main__":
    main()
