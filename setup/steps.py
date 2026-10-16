"""The configuration steps; each returns the .env values it is responsible for."""
from . import steps_cloudflare as cf
from . import ui

MODES = [("Cloudflare Tunnel — sign in with browser", "recommended: one click on Cloudflare's page, everything else is automatic"),
         ("Cloudflare Tunnel — API token", "I paste an API token; the tunnel and DNS are created for me"),
         ("Cloudflare Tunnel — existing", "I already created a tunnel and have its token"),
         ("Local only", "No tunnel: listen on a port (put your own reverse proxy in front)")]


def access() -> dict[str, str]:
    mode = ui.choose("How will people reach ClaudeShare?", MODES)
    if mode == 3:
        bind = "0.0.0.0" if ui.yes("Listen on all network interfaces? (No = this machine only)", False) else "127.0.0.1"
        port = ui.ask_int("Port", 3000)
        scheme = "https" if ui.yes("Will it be served over HTTPS by your proxy?", False) else "http"
        host = ui.ask("Address people will use", f"localhost:{port}")
        return {"BIND": bind, "PORT": str(port), "PUBLIC_URL": f"{scheme}://{host}", "COOKIE_SECURE": "true" if scheme == "https" else "false"}
    hostname = cf.ask_hostname()
    secrets = {0: cf.browser, 1: cf.automatic}.get(mode, lambda _h: cf.manual())(hostname)
    return {"PUBLIC_URL": f"https://{hostname}", "COOKIE_SECURE": "true", "BIND": "127.0.0.1", "PORT": "3000",
            "COMPOSE_PROFILES": "cloudflare", **secrets}


def usage() -> dict[str, str]:
    ui.console.print("Claude's plan limit is shared by everyone. Give each person a percentage of it; the plan's size and weekly\n"
                     "reset are detected automatically, and when someone uses their slice their [bold]claude[/] pauses until the reset.")
    share = ui.ask_int("Default share per person (percent of the plan)", 20)
    return {"USAGE_SHARE": str(share)}


def resources() -> dict[str, str]:
    return {"MEM_LIMIT": ui.ask("Memory limit for the whole container", "4g"), "CPU_LIMIT": ui.ask("CPU limit (cores)", "2")}
