import asyncio
from collections.abc import AsyncGenerator

import strawberry
from strawberry.types import Info

from ..config import WATCH_SECONDS
from ..models import User
from ..services import planusage, usage
from ..types import ClaudeSession, PlanUsage, Usage
from .context import Authed, current


async def build(user: User) -> Usage:
    await usage.refresh(user)
    snap = usage.snapshot(user)
    plan = await planusage.plan_usage()
    return Usage(**{**snap, "sessions": [ClaudeSession(**s) for s in snap["sessions"]],
                    "plan": PlanUsage(**plan) if plan else None})


@strawberry.type
class UsageQuery:
    @strawberry.field(permission_classes=Authed)
    async def usage(self, info: Info) -> Usage:
        return await build(current(info))


@strawberry.type
class UsageSubscription:
    @strawberry.subscription(permission_classes=Authed)
    async def usage_updates(self, info: Info) -> AsyncGenerator[Usage, None]:
        user = current(info)
        while True:
            yield await build(user)
            await asyncio.sleep(WATCH_SECONDS)
