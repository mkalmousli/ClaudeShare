"""Read and write the project's .env (mode 600)."""
import os
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT / ".env"


def read(path: Path = ENV_PATH) -> dict[str, str]:
    values: dict[str, str] = {}
    if path.exists():
        for line in path.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                key, _, value = line.partition("=")
                values[key.strip()] = value.strip()
    return values


def write(values: dict[str, str], path: Path = ENV_PATH) -> None:
    body = "# Written by `claudeshare setup`. Contains secrets: keep private.\n"
    body += "".join(f"{key}={value}\n" for key, value in values.items() if value != "")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as fh:
        fh.write(body)
    os.chmod(path, 0o600)
