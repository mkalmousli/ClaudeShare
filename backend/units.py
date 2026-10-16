"""Parse human sizes like 512m / 2g / 1.5t into megabytes. Standard library only."""
import re

_UNITS = {"": 1, "k": 1 / 1024, "m": 1, "g": 1024, "t": 1024 * 1024}


def parse_size_mb(text: str) -> float:
    match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*([kmgt]?)b?", text.strip().lower())
    if not match or float(match[1]) <= 0:
        raise ValueError("Give a size such as 512m, 2g or 1.5t.")
    return float(match[1]) * _UNITS[match[2]]


def format_mb(megabytes: float) -> str:
    if megabytes >= 1024 * 1024:
        return f"{megabytes / 1024 / 1024:.1f}T"
    return f"{megabytes / 1024:.1f}G" if megabytes >= 1024 else f"{megabytes:.0f}M"
