from collections.abc import AsyncGenerator

import strawberry
from strawberry.types import Info

from ..services import ptys, ptyterm
from ..types import TerminalEvent, TerminalInfo
from .context import Authed, current


def _info(term: ptyterm.Term) -> TerminalInfo:
    return TerminalInfo(id=term.id, title=f"Terminal {term.number}")


def _owned(info: Info, term_id: str) -> ptyterm.Term:
    term = ptys.get(current(info), term_id)
    if not term:
        raise ValueError("No such terminal")
    return term


@strawberry.type
class TerminalQuery:
    @strawberry.field(permission_classes=Authed)
    def terminals(self, info: Info) -> list[TerminalInfo]:
        return [_info(t) for t in ptys.for_user(current(info).name)]


@strawberry.type
class TerminalMutation:
    @strawberry.mutation(permission_classes=Authed)
    def create_terminal(self, info: Info, cwd: str | None = None, run: str | None = None,
                        cols: int = 100, rows: int = 30) -> TerminalInfo:
        return _info(ptys.create(current(info), cwd, cols, rows, run))

    @strawberry.mutation(permission_classes=Authed)
    def close_terminal(self, info: Info, id: str) -> bool:
        ptys.close(_owned(info, id))
        return True

    @strawberry.mutation(permission_classes=Authed)
    def terminal_input(self, info: Info, id: str, data: str) -> bool:
        ptyterm.write(_owned(info, id), data)
        return True

    @strawberry.mutation(permission_classes=Authed)
    def terminal_resize(self, info: Info, id: str, cols: int, rows: int) -> bool:
        ptyterm.resize(_owned(info, id), cols, rows)
        return True


@strawberry.type
class TerminalSubscription:
    @strawberry.subscription(permission_classes=Authed)
    async def terminal_output(self, info: Info, id: str) -> AsyncGenerator[TerminalEvent, None]:
        async for kind, data in ptyterm.stream(_owned(info, id)):
            yield TerminalEvent(kind=kind, data=data)
