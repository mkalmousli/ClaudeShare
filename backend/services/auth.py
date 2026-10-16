"""Cookie handling and request checks shared by HTTP routes and GraphQL."""
from starlette.requests import HTTPConnection
from starlette.responses import Response

from ..config import COOKIE_NAME, COOKIE_SECURE, SESSION_DAYS
from ..models import User
from . import sessions


def same_origin(conn: HTTPConnection) -> bool:
    origin = conn.headers.get("origin")
    if not origin:
        return True
    return origin.split("://", 1)[-1] == conn.headers.get("host")


def user_from(conn: HTTPConnection) -> User | None:
    return sessions.parse(conn.cookies.get(COOKIE_NAME)) if same_origin(conn) else None


def _secure(conn: HTTPConnection) -> bool:
    if COOKIE_SECURE != "auto":
        return COOKIE_SECURE == "true"
    return conn.headers.get("x-forwarded-proto") == "https" or conn.url.scheme == "https"


def set_cookie(conn: HTTPConnection, response: Response, user: User) -> None:
    response.set_cookie(COOKIE_NAME, sessions.issue(user), max_age=SESSION_DAYS * 86400, httponly=True,
                        samesite="strict", secure=_secure(conn), path="/")


def clear_cookie(response: Response) -> None:
    response.delete_cookie(COOKIE_NAME, path="/")


def client_ip(conn: HTTPConnection) -> str:
    return conn.headers.get("cf-connecting-ip") or (conn.client.host if conn.client else "?")
