"""Streaming upload/download (binary does not belong in GraphQL)."""
import asyncio
import mimetypes
import posixpath
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse

from ..models import User
from . import auth, fs_client

router = APIRouter()
INLINE_PREFIXES = ("image/", "audio/", "video/")
INLINE_TYPES = {"application/pdf"}


def _user(request: Request) -> User:
    user = auth.user_from(request)
    if not user:
        raise HTTPException(401, "Not signed in")
    return user


def _abs(user: User, rel: str) -> str:
    return str(user.home / posixpath.normpath("/" + rel).lstrip("/"))


def _run_as(user: User, *cmd: str, stdin=None, stdout=asyncio.subprocess.PIPE):
    return asyncio.create_subprocess_exec(
        *cmd, stdin=stdin, stdout=stdout, stderr=asyncio.subprocess.DEVNULL,
        cwd=str(user.home), user=user.uid, group=user.uid, extra_groups=[],
        env={"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": str(user.home), "LANG": "C.UTF-8"})


async def _pump(proc):
    try:
        while chunk := await proc.stdout.read(65536):
            yield chunk
    finally:
        if proc.returncode is None:
            proc.kill()
        await proc.wait()


@router.get("/download")
async def download(request: Request, path: str = "/", inline: int = 0):
    user = _user(request)
    try:
        info = await fs_client.call(user, "stat", path=path)
    except fs_client.FsError as exc:
        raise HTTPException(404, str(exc))
    full = _abs(user, path)
    name = posixpath.basename(full) or user.name
    mime = mimetypes.guess_type(name)[0] or "application/octet-stream"
    can_inline = inline and (mime.startswith(INLINE_PREFIXES) or mime in INLINE_TYPES)
    headers = {"X-Content-Type-Options": "nosniff", "Content-Security-Policy": "sandbox; default-src 'none'; img-src data:"}
    if info["isDir"]:
        proc = await _run_as(user, "tar", "-czf", "-", "-C", posixpath.dirname(full), "--", posixpath.basename(full))
        name, mime = name + ".tar.gz", "application/gzip"
    else:
        proc = await _run_as(user, "cat", "--", full)
        headers["Content-Length"] = str(info["size"])
    kind = "inline" if can_inline else "attachment"
    headers["Content-Disposition"] = f"{kind}; filename*=UTF-8''{quote(name)}"
    return StreamingResponse(_pump(proc), media_type=mime if can_inline or info["isDir"] else "application/octet-stream", headers=headers)


@router.put("/upload")
async def upload(request: Request, path: str, overwrite: int = 0):
    user = _user(request)
    if not auth.same_origin(request) or posixpath.basename(path) in ("", ".", ".."):
        raise HTTPException(400, "Bad request")
    try:
        await fs_client.call(user, "mkdir", path=posixpath.dirname(path) or "/", parents=True)
        final = (await fs_client.call(user, "unique", path=path, overwrite=bool(overwrite)))["path"]
    except fs_client.FsError as exc:
        raise HTTPException(400, str(exc))
    proc = await _run_as(user, "tee", "--", _abs(user, final),
                         stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.DEVNULL)
    try:
        async for chunk in request.stream():
            proc.stdin.write(chunk)
            await proc.stdin.drain()
        proc.stdin.close()
        await proc.wait()
    except Exception:
        proc.kill()
        await fs_client.call(user, "remove", paths=[final])
        raise HTTPException(500, "Upload failed")
    return JSONResponse({"path": final})
