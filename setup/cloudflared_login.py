"""Sign in to Cloudflare through the browser (no token to copy), then create the tunnel.

Uses the official cloudflared image: `tunnel login` prints a Cloudflare page where you pick
your domain; the rest (tunnel, DNS record, config) is done for you.
"""
import json
import os
import re
import subprocess
import webbrowser
from pathlib import Path

from . import ui
from .envfile import PROJECT

IMAGE = "cloudflare/cloudflared:latest"
DIR = PROJECT / ".cloudflared"
URL_RE = re.compile(r"https://dash\.cloudflare\.com/\S+")
UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
CONFIG = """tunnel: {tunnel}
credentials-file: /etc/cloudflared/{tunnel}.json
ingress:
  - hostname: {hostname}
    service: http://app:3000
  - service: http_status:404
"""


def docker(*args: str) -> subprocess.Popen:
    cmd = ["docker", "run", "--rm", "--user", f"{os.getuid()}:{os.getgid()}", "-e", "HOME=/home/nonroot",
           "-v", f"{DIR}:/home/nonroot/.cloudflared", IMAGE, *args]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)


def run(*args: str, echo: bool = False) -> tuple[int, str]:
    proc = docker(*args)
    lines = []
    for line in proc.stdout:
        lines.append(line)
        if echo:
            ui.console.print(line.rstrip(), markup=False)
            link = URL_RE.search(line)
            if link:
                webbrowser.open(link.group(0))  # silently does nothing on a server without a browser
    return proc.wait(), "".join(lines)


def login() -> None:
    DIR.mkdir(mode=0o700, exist_ok=True)
    if (DIR / "cert.pem").exists() and ui.yes("Already signed in to Cloudflare here. Reuse it?"):
        return
    ui.console.print("\n[bold]Open the Cloudflare page below[/], choose your domain and click [bold]Authorize[/].\n"
                     "[dim](It opens automatically if this machine has a browser.)[/]")
    if run("tunnel", "login", echo=True)[0] or not (DIR / "cert.pem").exists():
        raise SystemExit("Cloudflare sign-in did not finish.")
    ui.ok("Signed in to Cloudflare")


def tunnel_id(name: str) -> str:
    code, out = run("tunnel", "create", name)
    found = UUID_RE.search(out)
    if code == 0 and found:
        return found.group(0)
    code, out = run("tunnel", "list", "--name", name, "--output", "json")
    listed = json.loads(out[out.index("["):]) if "[" in out else []
    if listed and (DIR / f"{listed[0]['id']}.json").exists():
        return listed[0]["id"]
    raise SystemExit(f"Could not create the tunnel: {out.strip().splitlines()[-1] if out.strip() else 'unknown error'}")


def setup_tunnel(hostname: str) -> dict[str, str]:
    login()
    tunnel = tunnel_id(f"claudeshare-{hostname}")
    ui.ok(f"Tunnel ready ({tunnel[:8]}…)")
    code, out = run("tunnel", "route", "dns", "--overwrite-dns", tunnel, hostname)
    if code:
        raise SystemExit(f"Could not create the DNS record: {out.strip().splitlines()[-1]}")
    ui.ok(f"{hostname} now points at your tunnel")
    (DIR / "config.yml").write_text(CONFIG.format(tunnel=tunnel, hostname=hostname))
    return {"COMPOSE_PROFILES": "cloudflare-local", "CF_UID": str(os.getuid()), "CF_GID": str(os.getgid())}
