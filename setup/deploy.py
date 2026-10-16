"""Build, install the service, wait for it, sign in the source Claude, create the first user."""
import getpass
import subprocess
import sys
import time
import urllib.request

from . import ui
from .envfile import PROJECT

HELPER = "/usr/libexec/claudeshare/ctl.py"


def run(*cmd: str, **kwargs) -> int:
    return subprocess.run(cmd, cwd=PROJECT, **kwargs).returncode


def build() -> None:
    ui.info("Building the image (first time takes a few minutes)…")
    if run("docker", "compose", "build"):
        ui.fail("Image build failed.")
        raise SystemExit(1)
    ui.ok("Image built")


def install_service() -> None:
    ui.info("Installing the system service (this is the only step that needs root)…")
    user = getpass.getuser()
    cmd = ["sudo", sys.executable, "-m", "system.install", "--user", user, "--project", str(PROJECT)]
    if run(*cmd):
        ui.fail("Service install failed.")
        raise SystemExit(1)
    ui.ok("Service installed and started; you can now manage it without root")


def wait_healthy(port: str, seconds: int = 90) -> bool:
    for _ in range(seconds):
        try:
            if urllib.request.urlopen(f"http://127.0.0.1:{port}/healthz", timeout=2).status == 200:
                return True
        except OSError:
            time.sleep(1)
    return False


def source_login() -> None:
    ui.console.print("\nNow sign the [bold]source[/] Claude in. Everyone shares this login.\n"
                     "Run [bold]/login[/] inside Claude, finish in your browser, then exit with [bold]/exit[/].")
    input("Press Enter to open Claude… ")
    run("sudo", "-n", HELPER, "login")


def first_user() -> None:
    if ui.yes("Create the first user now?"):
        name = ui.ask("User name", "alice")
        run("sudo", "-n", HELPER, "admin", "add", name)
