"""Stateless signed session tokens."""
import base64
import hashlib
import hmac
import json
import secrets
import time

from ..config import DATA, SECRET_FILE, SESSION_DAYS
from ..models import User
from . import store


def _secret() -> bytes:
    if not SECRET_FILE.exists():
        DATA.mkdir(parents=True, exist_ok=True)
        SECRET_FILE.write_text(secrets.token_hex(48))
        SECRET_FILE.chmod(0o600)
    return SECRET_FILE.read_text().strip().encode()


def _sign(payload: str) -> str:
    mac = hmac.new(_secret(), payload.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(mac).decode().rstrip("=")


def issue(user: User) -> str:
    body = {"u": user.name, "tv": user.tv, "exp": time.time() + SESSION_DAYS * 86400}
    payload = base64.urlsafe_b64encode(json.dumps(body).encode()).decode().rstrip("=")
    return f"{payload}.{_sign(payload)}"


def parse(token: str | None) -> User | None:
    try:
        payload, sig = (token or "").split(".")
        if not hmac.compare_digest(sig, _sign(payload)):
            return None
        body = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
        user = store.get(body["u"])
        return user if user and user.tv == body["tv"] and body["exp"] > time.time() else None
    except (ValueError, KeyError, TypeError):
        return None
