"""In-container user administration: python -m backend.admin <command> ...

Only ever invoked through the validated root helper (system/ctl.py).
"""
import asyncio

from . import admin_views as view
from .admin_parse import build_parser, parse_amount
from .services import accounts, passwords, planusage, store, usage

def cmd_add(args) -> None:
    key = args.key or passwords.new_key()
    accounts.create(args.name, key)
    view.ok(f'User "{args.name}" created')
    view.credentials(args.name, key)


def cmd_passwd(args) -> None:
    key = args.key or passwords.new_key()
    accounts.set_key(args.name, key)
    view.ok(f'New key for "{args.name}" (old sessions signed out)')
    view.credentials(args.name, key)


def cmd_del(args) -> None:
    accounts.remove(args.name, args.purge)
    view.ok(f'User "{args.name}" removed' + (" and files deleted" if args.purge else " (files kept; use --purge)"))


def cmd_limit(args) -> None:
    if not store.get(args.name):
        raise ValueError(f'No such user "{args.name}".')
    changes = {"share": parse_amount(args.amount)}
    if args.period:
        changes["period"] = args.period
    store.update(args.name, **changes)
    view.ok(f'Limit for "{args.name}" updated')


async def _rows() -> list[dict]:
    rows = []
    await planusage.plan_usage()
    for user in store.all_users():
        await usage.refresh(user)
        snap = usage.snapshot(user)
        live = any(s["live"] for s in snap["sessions"])
        rows.append({"name": user.name, "last_login": user.last_login[:16].replace("T", " "), "live": live, **snap})
    return rows


def cmd_status(_args) -> None:
    view.users_table(asyncio.run(_rows()))


def cmd_sessions(args) -> None:
    user = store.get(args.name)
    if not user:
        raise ValueError(f'No such user "{args.name}".')
    asyncio.run(planusage.plan_usage())
    asyncio.run(usage.refresh(user))
    view.sessions_table(usage.snapshot(user)["sessions"])


def main() -> None:
    commands = {"add": cmd_add, "passwd": cmd_passwd, "del": cmd_del, "limit": cmd_limit,
                "sessions": cmd_sessions, "status": cmd_status}
    args = build_parser(commands).parse_args()
    try:
        accounts.sync_all()
        args.fn(args)
    except ValueError as exc:
        view.fail(str(exc))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
