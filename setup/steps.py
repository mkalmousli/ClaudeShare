"""The configuration steps; each returns the .env values it is responsible for."""
from . import steps_cloudflare as cf
from . import ui

MODES = [("Cloudflare Tunnel — automatic", "I enter an API token; the tunnel and DNS are created for me"),
         ("Cloudflare Tunnel — existing", "I already created a tunnel and have its token"),
         ("Local only", "No tunnel: listen on a port (put your own reverse proxy in front)")]
PERIODS = [("day", ""), ("week", ""), ("month", "")]


def access() -> dict[str, str]:
    mode = ui.choose("How will people reach ClaudeShare?", MODES)
    if mode == 2:
        bind = "0.0.0.0" if ui.yes("Listen on all network interfaces? (No = this machine only)", False) else "127.0.0.1"
        port = ui.ask_int("Port", 3000)
        scheme = "https" if ui.yes("Will it be served over HTTPS by your proxy?", False) else "http"
        host = ui.ask("Address people will use", f"localhost:{port}")
        return {"BIND": bind, "PORT": str(port), "PUBLIC_URL": f"{scheme}://{host}", "COOKIE_SECURE": "true" if scheme == "https" else "false"}
    hostname = cf.ask_hostname()
    secrets = cf.automatic(hostname) if mode == 0 else cf.manual()
    return {"PUBLIC_URL": f"https://{hostname}", "COOKIE_SECURE": "true", "BIND": "127.0.0.1", "PORT": "3000",
            "COMPOSE_PROFILES": "cloudflare", **secrets}


def usage() -> dict[str, str]:
    ui.console.print("Claude's own plan limit is shared by everyone. Give each person a weekly (or daily/monthly) slice;\n"
                     "when they use it up, their [bold]claude[/] stops until the period resets.")
    period = PERIODS[ui.choose("Usage period", PERIODS, default=2)][0]
    plan = ui.ask_int("Total weighted tokens your plan allows per period (millions)", 100)
    share = ui.ask_int("Default share per person (percent of the plan)", 20)
    reset = ui.ask_int("Weekly reset day (0 = Monday … 6 = Sunday)", 0)
    return {"USAGE_PERIOD": period, "USAGE_PLAN_TOKENS": str(plan * 1_000_000),
            "USAGE_BUDGET": str(int(plan * 1_000_000 * share / 100)), "USAGE_RESET_DAY": str(reset)}


def resources() -> dict[str, str]:
    return {"MEM_LIMIT": ui.ask("Memory limit for the whole container", "4g"), "CPU_LIMIT": ui.ask("CPU limit (cores)", "2")}
