"""Run the official cloudflared image against ./.cloudflared, handling host/container permissions."""
import os
import subprocess

from .envfile import PROJECT

IMAGE = "cloudflare/cloudflared:latest"
DIR = PROJECT / ".cloudflared"


def rootless() -> bool:
    """Rootless Docker maps container root to *you*, so that is the user that can write the folder."""
    out = subprocess.run(["docker", "info", "--format", "{{.SecurityOptions}}"], capture_output=True, text=True).stdout
    return "rootless" in out


def owner() -> tuple[int, int]:
    """Who should own the credentials on the host (and run the tunnel service)."""
    return (0, 0) if rootless() else (os.getuid(), os.getgid())


def docker(*args: str) -> subprocess.Popen:
    # Root inside the container can always write the folder; ownership is handed back afterwards.
    # ":z" relabels the folder so SELinux hosts (Fedora, RHEL…) allow it.
    cmd = ["docker", "run", "--rm", "--user", "0:0", "-e", "HOME=/home/nonroot",
           "-v", f"{DIR}:/home/nonroot/.cloudflared:z", IMAGE, *args]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def hand_back() -> None:
    """Files written by container-root belong to root on the host; sudo gives them back to you."""
    uid, gid = owner()
    if uid and subprocess.run(["sudo", "chown", "-R", f"{uid}:{gid}", str(DIR)]).returncode:
        raise SystemExit("Could not take ownership of the Cloudflare credentials (sudo failed).")
