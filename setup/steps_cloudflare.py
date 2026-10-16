"""Step: Cloudflare Tunnel, either fully automatic or with an existing tunnel token."""
import re

from . import cloudflared_login, ui
from .cloudflare import Cloudflare, CloudflareError

HOST_RE = re.compile(r"^(?=.{4,253}$)([a-z0-9-]+\.)+[a-z]{2,}$")
TOKEN_HELP = ("Create an API token at [cyan]dash.cloudflare.com/profile/api-tokens[/] with:\n"
              "  • Account → Cloudflare Tunnel → [bold]Edit[/]\n  • Zone → DNS → [bold]Edit[/]\n  • Zone → Zone → [bold]Read[/]")


def ask_hostname() -> str:
    check = lambda v: None if HOST_RE.match(v.strip().lower()) else "Enter a full hostname such as claude.example.com"
    return ui.ask("Public hostname", "claude.example.com", check=check).strip().lower()


def automatic(hostname: str) -> dict[str, str]:
    ui.console.print(TOKEN_HELP)
    while True:
        cf = Cloudflare(ui.ask("Cloudflare API token", secret=True))
        try:
            cf.verify()
            ui.ok("Token is valid")
            zone = cf.find_zone(hostname)
            ui.ok(f"Zone [bold]{zone['name']}[/] found")
            tunnel = cf.tunnel(zone["account"], f"claudeshare-{hostname}")
            cf.route(zone["account"], tunnel, hostname, "http://app:3000")
            ui.ok("Tunnel routes to the app")
            ui.ok(f"DNS record {cf.dns(zone['id'], hostname, tunnel)}")
            return {"TUNNEL_TOKEN": cf.tunnel_token(zone["account"], tunnel)}
        except CloudflareError as exc:
            ui.fail(str(exc))
            if not ui.yes("Try a different token?"):
                raise SystemExit(1)


def manual() -> dict[str, str]:
    ui.info("In Cloudflare Zero Trust create a tunnel, copy its token, and add a public hostname pointing to [bold]http://app:3000[/].")
    return {"TUNNEL_TOKEN": ui.ask("Tunnel token", secret=True, check=lambda v: None if len(v) > 40 else "That looks too short.")}


def browser(hostname: str) -> dict[str, str]:
    return cloudflared_login.setup_tunnel(hostname)
