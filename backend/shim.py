#!/usr/local/bin/python3
"""Installed as `claude` for users: refuses to start once their usage limit is reached."""
import os
import sys
import time

BLOCKED = "/run/claudeshare/blocked"
REAL = "/opt/claude-real"

flag = os.path.join(BLOCKED, os.environ.get("USER", ""))
if os.path.isfile(flag):
    try:
        resets = time.strftime("%a %d %b %H:%M UTC", time.gmtime(int(open(flag).read())))
    except (OSError, ValueError):
        resets = "the next period"
    sys.stderr.write(f"\x1b[1;31mUsage limit reached.\x1b[0m Claude is paused until {resets}.\n")
    sys.exit(1)
os.execv(REAL, ["claude", *sys.argv[1:]])
