"""Colour-coded terminal UI helpers for the guided setup."""
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.rule import Rule

console = Console(highlight=False)
ACCENT = "#d97757"


def banner() -> None:
    console.print(Panel.fit(f"[bold {ACCENT}]ClaudeShare[/]  [dim]guided setup[/]\n"
                            "[dim]Isolated Claude CLI desktops for the people you invite.[/]", border_style=ACCENT, padding=(1, 4)))


def step(number: int, total: int, title: str, hint: str = "") -> None:
    console.print()
    console.print(Rule(f"[bold cyan]Step {number}/{total}[/]  [bold]{title}[/]", style="cyan", align="left"))
    if hint:
        console.print(f"[dim]{hint}[/]")


def ok(text: str) -> None:
    console.print(f"[bold green]✔[/] {text}")


def warn(text: str) -> None:
    console.print(f"[bold yellow]![/] [yellow]{text}[/]")


def fail(text: str) -> None:
    console.print(f"[bold red]✖[/] [red]{text}[/]")


def info(text: str) -> None:
    console.print(f"[cyan]›[/] {text}")


def ask(question: str, default: str | None = None, secret: bool = False, check=None) -> str:
    """Prompt until `check(value)` returns None (valid) or an error message."""
    while True:
        value = Prompt.ask(f"[bold]{question}[/]", default=default, password=secret, console=console)
        problem = check(value) if check else None
        if not problem:
            return value
        fail(problem)


def ask_int(question: str, default: int) -> int:
    return IntPrompt.ask(f"[bold]{question}[/]", default=default, console=console)


def yes(question: str, default: bool = True) -> bool:
    return Confirm.ask(f"[bold]{question}[/]", default=default, console=console)


def choose(title: str, options: list[tuple[str, str]], default: int = 1) -> int:
    """Numbered menu; returns the zero-based index chosen."""
    console.print(f"\n[bold]{title}[/]")
    for idx, (name, detail) in enumerate(options, 1):
        console.print(f"  [bold {ACCENT}]{idx}[/]  [bold]{name}[/]  [dim]{detail}[/]")
    return IntPrompt.ask("Choose", choices=[str(n) for n in range(1, len(options) + 1)], default=default, console=console, show_choices=False) - 1
