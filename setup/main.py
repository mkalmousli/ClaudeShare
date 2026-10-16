"""`claudeshare setup`: guided, colour-coded configuration."""
import argparse

from . import deploy, envfile, steps, ui

TOTAL = 5


def collect(existing: dict[str, str]) -> dict[str, str]:
    values = dict(existing)
    ui.step(1, TOTAL, "Access", "How the outside world reaches your ClaudeShare.")
    values.update(steps.access())
    ui.step(2, TOTAL, "Usage limits", "Split your Claude plan between people.")
    values.update(steps.usage())
    ui.step(3, TOTAL, "Resources", "Limits for the whole container and for each person.")
    values.update(steps.resources())
    return values


def summary(values: dict[str, str]) -> None:
    ui.console.print(f"\n[bold green]Ready.[/] People will open [bold cyan]{values['PUBLIC_URL']}[/]")
    ui.console.print("Manage it any time (no root needed):\n  [bold]claudeshare status[/] · [bold]on[/] · [bold]off[/] · [bold]user add NAME[/] · [bold]user limit NAME 25%[/]\n")


def main() -> None:
    parser = argparse.ArgumentParser(prog="setup")
    parser.add_argument("--env-only", action="store_true", help="only write .env (no docker, no sudo)")
    args = parser.parse_args()
    ui.banner()
    values = collect(envfile.read())
    envfile.write(values)
    ui.ok(f"Settings saved to {envfile.ENV_PATH}")
    if args.env_only:
        return
    ui.step(4, TOTAL, "Install", "Build the image and register the service.")
    deploy.build()
    deploy.install_service()
    if not deploy.wait_healthy(values.get("PORT", "3000")):
        ui.warn("The app did not answer in time; check `claudeshare logs`.")
    ui.step(5, TOTAL, "Claude login & first user")
    deploy.source_login()
    deploy.first_user()
    summary(values)


if __name__ == "__main__":
    main()
