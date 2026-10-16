"""Strict grammar for the admin commands the root helper will forward. Standard library only."""
import re
import sys

NAME = re.compile(r"^[a-z][a-z0-9_-]{1,23}$")
KEY = re.compile(r"^[A-Za-z0-9_-]{8,128}$")
AMOUNT = re.compile(r"^(default|\d{1,3}(\.\d+)?%?)$")
PERIOD = re.compile(r"^(day|week|month)$")


def fail(message: str) -> None:
    sys.stderr.write(message + "\n")
    sys.exit(2)


def pick(value: str, pattern: re.Pattern, what: str) -> str:
    if not pattern.match(value):
        fail(f"Invalid {what}.")
    return value


def admin_args(args: list[str]) -> list[str]:
    """Validate a backend.admin command line against a strict grammar."""
    cmd, rest = (args or [""])[0], args[1:]
    flags = {"add": {"--key"}, "passwd": {"--key"}, "del": {"--purge"}, "limit": {"--period"}}
    shape = {"add": 1, "passwd": 1, "del": 1, "limit": 2, "sessions": 1, "status": 0, "list": 0}
    if cmd not in shape:
        fail("Unknown admin command.")
    positional = []
    out = [cmd]
    idx = 0
    while idx < len(rest):
        item = rest[idx]
        if item in flags.get(cmd, set()):
            if item == "--purge":
                out.append(item)
            else:
                idx += 1
                value = rest[idx] if idx < len(rest) else ""
                out += [item, pick(value, KEY if item == "--key" else PERIOD, item)]
        else:
            positional.append(item)
        idx += 1
    if len(positional) != shape[cmd]:
        fail("Wrong number of arguments.")
    if positional:
        out.insert(1, pick(positional[0], NAME, "user name"))
    if cmd == "limit":
        out.insert(2, pick(positional[1], AMOUNT, "amount"))
    return out
