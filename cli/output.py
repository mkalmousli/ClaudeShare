"""Colour-coded console output for the claudeshare CLI."""
from rich.console import Console

console = Console(highlight=False)
ACCENT = "#d97757"


def ok(text: str) -> None:
    console.print(f"[bold green]✔[/] {text}")


def warn(text: str) -> None:
    console.print(f"[bold yellow]![/] [yellow]{text}[/]")


def fail(text: str) -> None:
    console.print(f"[bold red]✖[/] [red]{text}[/]")


def state_line(label: str, value: str, good: set[str]) -> None:
    color = "green" if value in good else "yellow"
    console.print(f"  [dim]{label:<9}[/] [bold {color}]{value}[/]")
