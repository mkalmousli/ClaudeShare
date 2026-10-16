"""Strict grammar for the admin commands the root helper will forward. Standard library only."""
import re
import sys

NAME = re.compile(r"^[a-z][a-z0-9_-]{1,23}$")
KEY = re.compile(r"^[A-Za-z0-9_-]{8,128}$")
AMOUNT = re.compile(r"^(default|\d{1,3}(\.\d+)?%?)$")
PERIOD = re.compile(r"^(day|week|month)$")
SIZE = re.compile(r"^(default|\d+(\.\d+)?[kKmMgGtT]?[bB]?)$")
NUMBER = re.compile(r"^(default|\d+(\.\d+)?)$")
# command -> flags it accepts (None = no value) ; command -> positional count
FLAGS = {"add": {"--key": KEY}, "passwd": {"--key": KEY}, "del": {"--purge": None}, "limit": {"--period": PERIOD},
         "resources": {"--mem": SIZE, "--cpu": NUMBER, "--procs": NUMBER, "--disk": SIZE}}
SHAPE = {"add": 1, "passwd": 1, "del": 1, "limit": 2, "resources": 1, "sessions": 1, "status": 0, "list": 0}


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
    if cmd not in SHAPE:
        fail("Unknown admin command.")
    allowed, positional, out, idx = FLAGS.get(cmd, {}), [], [cmd], 0
    while idx < len(rest):
        item = rest[idx]
        if item in allowed:
            out.append(item)
            if allowed[item] is not None:
                idx += 1
                out.append(pick(rest[idx] if idx < len(rest) else "", allowed[item], item))
        else:
            positional.append(item)
        idx += 1
    if len(positional) != SHAPE[cmd]:
        fail("Wrong number of arguments.")
    if positional:
        out.insert(1, pick(positional[0], NAME, "user name"))
    if cmd == "limit":
        out.insert(2, pick(positional[1], AMOUNT, "amount"))
    return out
