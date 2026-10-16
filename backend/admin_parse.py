"""Argument parsing for the in-container admin CLI."""
import argparse
import re

from .config import PERIODS, PLAN_TOKENS

UNITS = {"k": 1e3, "m": 1e6, "b": 1e9}


def parse_amount(text: str) -> float | None:
    """'25%' is a share of the whole plan; '5m' / '800k' / '12345' are weighted tokens."""
    if text == "default":
        return None
    match = re.fullmatch(r"(\d+(?:\.\d+)?)(%|[kmb])?", text.lower())
    if not match:
        raise ValueError("Amount looks like 25%, 5m, 800k or 12345 (or 'default').")
    number, unit = float(match[1]), match[2]
    return number / 100 * PLAN_TOKENS if unit == "%" else number * UNITS.get(unit, 1)


def build_parser(cmds: dict) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="admin")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name, extra in (("add", "key"), ("passwd", "key"), ("del", "purge"), ("limit", "amount"), ("sessions", None), ("status", None)):
        item = sub.add_parser(name)
        item.set_defaults(fn=cmds[name])
        if name != "status":
            item.add_argument("name")
        if extra == "key":
            item.add_argument("--key")
        if extra == "purge":
            item.add_argument("--purge", action="store_true")
        if extra == "amount":
            item.add_argument("amount")
            item.add_argument("--period", choices=PERIODS)
    sub.add_parser("list").set_defaults(fn=cmds["status"])
    return parser
