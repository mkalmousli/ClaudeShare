"""Rich output for the in-container admin commands."""
from datetime import datetime, timezone

from rich.console import Console
from rich.table import Table

from .config import PUBLIC_URL
from .units import format_mb

console = Console(highlight=False)


def when(epoch: float) -> str:
    return datetime.fromtimestamp(epoch, timezone.utc).strftime("%a %d %b %H:%M")


def ok(text: str) -> None:
    console.print(f"\n[bold green]✔[/] {text}")


def fail(text: str) -> None:
    console.print(f"\n[bold red]✖ {text}[/]\n")


def credentials(name: str, key: str) -> None:
    console.print(f"\n  [cyan]URL [/]  {PUBLIC_URL}\n  [cyan]User[/]  [bold green]{name}[/]\n  [cyan]Key [/]  [bold yellow]{key}[/]")
    console.print("\n  [dim]Share these two. The key is shown only once.[/]\n")


def users_table(rows: list[dict]) -> None:
    table = Table(header_style="bold cyan", box=None, padding=(0, 2))
    for col in ("USER", "LAST LOGIN", "USED", "RESETS", "CLAUDE"):
        table.add_column(col)
    for row in rows:
        pct = row["percent"]
        color = "red" if pct >= 100 else "yellow" if pct >= 80 else "green"
        table.add_row(f"[green]{row['name']}[/]", row["last_login"] or "[dim]never[/]",
                      f"[{color}]{pct:5.1f}%[/] [dim]of a {row['share']:g}% share / {row['period']}[/]",
                      when(row["resets_at"]), "[bold green]running[/]" if row["live"] else "[dim]idle[/]")
    console.print()
    console.print(table)
    console.print()


def resources_table(name: str, lim: dict) -> None:
    console.print(f"\n  [bold]{name}[/]  [dim]resource limits[/]")
    console.print(f"  [cyan]RAM  [/] {format_mb(lim['mem_mb'])}\n  [cyan]CPU  [/] {lim['cpu']:g} core(s)\n"
                  f"  [cyan]Procs[/] {lim['procs']:.0f}\n  [cyan]Disk [/] {format_mb(lim['disk_mb'])}\n")


def sessions_table(sessions: list[dict]) -> None:
    table = Table(header_style="bold cyan", box=None, padding=(0, 2))
    for col in ("SESSION", "PROJECT", "LAST ACTIVE", "MSGS", "TOKENS", ""):
        table.add_column(col)
    for row in sessions:
        table.add_row(row["id"][:8], row["project"], when(row["last"]), str(row["messages"]),
                      f"{row['tokens']:,.0f}", "[bold green]live[/]" if row["live"] else "")
    console.print()
    console.print(table if sessions else "[yellow]No Claude sessions in this period.[/]")
    console.print()
