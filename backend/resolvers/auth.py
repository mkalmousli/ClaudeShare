from datetime import datetime, timezone

import strawberry
from strawberry.types import Info

from ..models import User
from ..services import auth, ratelimit, store
from ..services.passwords import verify_key
from ..types import Me
from .context import Authed, current

IP_LIMIT, USER_LIMIT = 30, 10
BAD_LOGIN = "Wrong username or key"


def _guard(keys: list[tuple[str, int]]) -> None:
    if any(ratelimit.blocked(key, limit) for key, limit in keys):
        raise ValueError("Too many attempts. Try again in a few minutes.")


@strawberry.type
class AuthQuery:
    @strawberry.field(permission_classes=Authed)
    def me(self, info: Info) -> Me:
        return Me(username=current(info).name)


@strawberry.type
class AuthMutation:
    @strawberry.mutation
    def login(self, info: Info, username: str, key: str) -> Me:
        name = username.strip().lower()
        keys = [(f"ip:{auth.client_ip(info.context.conn)}", IP_LIMIT), (f"user:{name}", USER_LIMIT)]
        _guard(keys)
        user: User | None = store.get(name)
        if not verify_key(key, user.hash if user else None):
            for key_name, _ in keys:
                ratelimit.record(key_name)
            raise ValueError(BAD_LOGIN)
        store.update(name, last_login=datetime.now(timezone.utc).isoformat(timespec="seconds"))
        auth.set_cookie(info.context.conn, info.context.response, user)
        return Me(username=name)

    @strawberry.mutation
    def logout(self, info: Info) -> bool:
        auth.clear_cookie(info.context.response)
        return True
