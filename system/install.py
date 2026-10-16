"""One-time root install: systemd unit, `claudeshare` group, sudoers rule, root helper.

Usage (run via sudo by `uv run install`, `claudeshare setup` and `claudeshare uninstall`):  python -m system.install --user NAME --project DIR
       python -m system.install --remove
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

GROUP = "claudeshare"
HELPER_DIR = Path("/usr/libexec/claudeshare")
HELPER = HELPER_DIR / "ctl.py"
CONF_DIR = Path("/etc/claudeshare")
UNIT_PATH = Path("/etc/systemd/system/claudeshare.service")
SUDOERS = Path("/etc/sudoers.d/claudeshare")

UNIT = """[Unit]
Description=ClaudeShare (isolated Claude CLI desktops)
Requires=docker.service
After=docker.service network-online.target

[Service]
WorkingDirectory={project}
ExecStart={docker} compose up --remove-orphans
ExecStop={docker} compose down
Restart=on-failure
RestartSec=5
TimeoutStopSec=60

[Install]
WantedBy=multi-user.target
"""

SUDOERS_RULE = f"%{GROUP} ALL=(root) NOPASSWD: {HELPER}\n"


def run(*cmd: str, check: bool = True) -> None:
    subprocess.run(cmd, check=check, capture_output=True)


def write(path: Path, text: str, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    os.chmod(path, mode)


def install(user: str, project: Path, start: bool = True) -> None:
    docker = shutil.which("docker")
    if not docker:
        sys.exit("Docker is not installed.")
    run("groupadd", "-f", GROUP)
    run("usermod", "-aG", GROUP, user)
    HELPER_DIR.mkdir(parents=True, exist_ok=True)
    for name in ("ctl.py", "ctl_args.py"):
        shutil.copy(Path(__file__).with_name(name), HELPER_DIR / name)
        os.chown(HELPER_DIR / name, 0, 0)
        os.chmod(HELPER_DIR / name, 0o755 if name == "ctl.py" else 0o644)
    write(CONF_DIR / "project", str(project), 0o644)
    write(UNIT_PATH, UNIT.format(project=project, docker=docker), 0o644)
    write(SUDOERS, SUDOERS_RULE, 0o440)
    if subprocess.run(["visudo", "-cf", str(SUDOERS)], capture_output=True).returncode:
        SUDOERS.unlink()
        sys.exit("Generated sudoers rule failed validation; nothing was enabled.")
    run("systemctl", "daemon-reload")
    run("systemctl", "enable", UNIT_PATH.name)
    if start:  # a fresh install stays off until `claudeshare setup` has configured it
        run("systemctl", "restart", UNIT_PATH.name)  # also picks up a changed .env on re-runs


def remove() -> None:
    run("systemctl", "disable", "--now", UNIT_PATH.name, check=False)
    for path in (UNIT_PATH, SUDOERS):
        path.unlink(missing_ok=True)
    shutil.rmtree(HELPER_DIR, ignore_errors=True)
    shutil.rmtree(CONF_DIR, ignore_errors=True)
    run("systemctl", "daemon-reload", check=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--user")
    parser.add_argument("--project")
    parser.add_argument("--remove", action="store_true")
    parser.add_argument("--no-start", action="store_true")
    args = parser.parse_args()
    if os.geteuid() != 0:
        sys.exit("This step must run as root (setup calls it through sudo).")
    if args.remove:
        remove()
    elif args.user and args.project:
        install(args.user, Path(args.project).resolve(), start=not args.no_start)
    else:
        parser.error("--user and --project are required")


if __name__ == "__main__":
    main()
