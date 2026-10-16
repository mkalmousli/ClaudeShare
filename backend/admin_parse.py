"""Argument parsing for the in-container admin CLI."""
import argparse
import re

from .config import PERIODS

def parse_amount(text: str) -> float | None:
    """A percentage of the plan: '25' or '25%'. 'default' goes back to the server default."""
    if text == "default":
        return None
    match = re.fullmatch(r"(\d{1,3}(?:\.\d+)?)%?", text)
    if not match or not 0 < float(match[1]) <= 100:
        raise ValueError("Give a percentage between 1 and 100, e.g. 25% (or 'default').")
    return float(match[1])


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
