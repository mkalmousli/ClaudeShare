"""`claudeshare` — a small CLI that needs no root once ClaudeShare is installed."""
import argparse
import sys

from . import commands, lifecycle

HELP = """commands:
  on / off / restart   start or stop the site (data is kept)
  status               service state and every user's usage
  logs [-f]            show server logs
  boot on|off          start automatically at boot (or not)
  login                sign the shared source Claude in again
  update               rebuild after `git pull`, then restart
  user add|list|passwd|del|limit|resources|sessions
  setup                guided configuration (access, limits, Claude login, first user)
  uninstall [--purge]  remove the service and command; --purge also deletes all data"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="claudeshare", epilog=HELP, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True, metavar="command")
    for name in ("on", "off", "restart", "status", "login", "update", "setup"):
        sub.add_parser(name)
    logs = sub.add_parser("logs")
    logs.add_argument("-f", "--follow", action="store_true")
    gone = sub.add_parser("uninstall")
    gone.add_argument("--purge", action="store_true")
    gone.add_argument("-y", "--yes", action="store_true")
    boot = sub.add_parser("boot")
    boot.add_argument("setting", choices=["on", "off"])
    sub.add_parser("user").add_argument("args", nargs=argparse.REMAINDER)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    table = {"on": commands.on, "off": commands.off, "restart": commands.restart, "status": commands.status,
             "login": commands.login, "update": commands.update, "setup": lifecycle.setup,
             "logs": lambda: commands.logs(args.follow), "boot": lambda: commands.boot(args.setting),
             "user": lambda: commands.user(args.args),
             "uninstall": lambda: lifecycle.uninstall(args.purge, args.yes)}
    sys.exit(table[args.cmd]())


if __name__ == "__main__":
    main()
