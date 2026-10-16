import strawberry
from strawberry.types import Info

from ..services import fs_client
from ..types import FileContent, FileEntry, Listing, PathResult
from .context import Authed, current


async def _fs(info: Info, op: str, **args) -> dict:
    try:
        return await fs_client.call(current(info), op, **args)
    except fs_client.FsError as exc:
        raise ValueError(str(exc)) from None


async def _ok(info: Info, op: str, **args) -> bool:
    await _fs(info, op, **args)
    return True


async def _path(info: Info, op: str, **args) -> PathResult:
    reply = await _fs(info, op, **args)
    return PathResult(path=reply.get("path") or reply.get("name") or "")


def _entry(raw: dict) -> FileEntry:
    return FileEntry(name=raw["name"], is_dir=raw["isDir"], size=raw["size"], mtime=raw["mtime"],
                     mode=raw["mode"], is_link=raw["isLink"])


@strawberry.type
class FileQuery:
    @strawberry.field(permission_classes=Authed)
    async def files(self, info: Info, path: str = "/") -> Listing:
        reply = await _fs(info, "list", path=path)
        return Listing(path=reply["path"], entries=[_entry(e) for e in reply["entries"]])

    @strawberry.field(permission_classes=Authed)
    async def read_file(self, info: Info, path: str) -> FileContent:
        return FileContent(**await _fs(info, "read", path=path))


@strawberry.type
class FileMutation:
    @strawberry.mutation(permission_classes=Authed)
    async def make_dir(self, info: Info, path: str) -> bool:
        return await _ok(info, "mkdir", path=path)

    @strawberry.mutation(permission_classes=Authed)
    async def make_file(self, info: Info, path: str) -> bool:
        return await _ok(info, "touch", path=path)

    @strawberry.mutation(permission_classes=Authed)
    async def write_file(self, info: Info, path: str, content: str) -> bool:
        return await _ok(info, "write", path=path, content=content)

    @strawberry.mutation(permission_classes=Authed)
    async def rename_entry(self, info: Info, path: str, to: str) -> PathResult:
        return await _path(info, "rename", path=path, to=to)

    @strawberry.mutation(permission_classes=Authed)
    async def move_entries(self, info: Info, paths: list[str], dest: str) -> bool:
        return await _ok(info, "move", paths=paths, dest=dest)

    @strawberry.mutation(permission_classes=Authed)
    async def copy_entries(self, info: Info, paths: list[str], dest: str) -> bool:
        return await _ok(info, "copy", paths=paths, dest=dest)

    @strawberry.mutation(permission_classes=Authed)
    async def delete_entries(self, info: Info, paths: list[str]) -> bool:
        return await _ok(info, "remove", paths=paths)

    @strawberry.mutation(permission_classes=Authed)
    async def chmod_entry(self, info: Info, path: str, mode: str) -> bool:
        return await _ok(info, "chmod", path=path, mode=mode)

    @strawberry.mutation(permission_classes=Authed)
    async def compress(self, info: Info, paths: list[str], dest: str, name: str) -> PathResult:
        return await _path(info, "compress", paths=paths, dest=dest, name=name)

    @strawberry.mutation(permission_classes=Authed)
    async def extract(self, info: Info, path: str) -> PathResult:
        return await _path(info, "extract", path=path)
