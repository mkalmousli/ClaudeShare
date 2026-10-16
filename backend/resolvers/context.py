"""Per-request GraphQL context and the authentication guard."""
import strawberry
from starlette.requests import HTTPConnection
from strawberry.fastapi import BaseContext
from strawberry.permission import BasePermission
from strawberry.types import Info

from ..models import User
from ..services import auth


class Ctx(BaseContext):
    def __init__(self, conn: HTTPConnection):
        super().__init__()
        self.conn = conn
        self.user: User | None = auth.user_from(conn)


async def get_context(conn: HTTPConnection) -> Ctx:
    return Ctx(conn)


class IsAuthenticated(BasePermission):
    message = "Not signed in"

    def has_permission(self, source, info: Info, **kwargs) -> bool:
        return info.context.user is not None


def current(info: Info) -> User:
    return info.context.user


Authed = [IsAuthenticated]
