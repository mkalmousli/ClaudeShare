"""Keep every user's Claude login in step with the single source login."""
import asyncio
import json
import os
import time

import httpx

from ..config import (CREDSYNC_SECONDS, OAUTH_CLIENT_ID, OAUTH_TOKEN_URL, REFRESH_MARGIN_MS, SOURCE_HOME)
from ..models import User
from . import store

SOURCE_FILE = SOURCE_HOME / ".claude" / ".credentials.json"


def read_source() -> dict | None:
    try:
        return json.loads(SOURCE_FILE.read_text())
    except (OSError, ValueError):
        return None


def _write_private(path, data: str, uid: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as fh:
        fh.write(data)
    if uid is not None:
        os.chown(path, uid, uid)
        os.chown(path.parent, uid, uid)


def seed_onboarding(user: User) -> None:
    """Mark first-run onboarding done so the shared login works without any prompts."""
    path = user.home / ".claude.json"
    try:
        config = json.loads(path.read_text())
    except (OSError, ValueError):
        config = {}
    if not config.get("hasCompletedOnboarding"):
        _write_private(path, json.dumps({**config, "hasCompletedOnboarding": True}), user.uid)


def push(user: User) -> bool:
    """Copy the login into the user's home. Their copy has no refresh token, so only the
    server ever refreshes it (a shared, rotating refresh token would break everyone)."""
    source = read_source()
    if not source or "claudeAiOauth" not in source:
        return False
    seed_onboarding(user)
    copy = {"claudeAiOauth": {**source["claudeAiOauth"], "refreshToken": ""}}
    target = user.home / ".claude" / ".credentials.json"
    text = json.dumps(copy)
    if not target.exists() or target.read_text() != text:
        _write_private(target, text, user.uid)
    return True


async def refresh_source() -> bool:
    source = read_source()
    oauth = (source or {}).get("claudeAiOauth", {})
    if not oauth.get("refreshToken") or oauth.get("expiresAt", 0) - time.time() * 1000 > REFRESH_MARGIN_MS:
        return False
    body = {"grant_type": "refresh_token", "refresh_token": oauth["refreshToken"], "client_id": OAUTH_CLIENT_ID}
    async with httpx.AsyncClient(timeout=15) as client:
        reply = await client.post(OAUTH_TOKEN_URL, json=body)
    reply.raise_for_status()
    data = reply.json()
    oauth.update(accessToken=data["access_token"], refreshToken=data.get("refresh_token", oauth["refreshToken"]),
                 expiresAt=int(time.time() * 1000) + int(data["expires_in"]) * 1000)
    _write_private(SOURCE_FILE, json.dumps(source))
    return True


async def loop() -> None:
    while True:
        try:
            await refresh_source()
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            print(f"[credsync] refresh failed: {exc}", flush=True)
        for user in store.all_users():
            try:
                push(user)
            except OSError as exc:
                print(f"[credsync] {user.name}: {exc}", flush=True)
        await asyncio.sleep(CREDSYNC_SECONDS)
