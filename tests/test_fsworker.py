import os
import pytest

from backend.fsworker import ops_archive, ops_edit, ops_list, ops_move
from backend.fsworker.paths import OpError, resolve, unique


@pytest.fixture(autouse=True)
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    return tmp_path


def test_parent_traversal_cannot_leave_home(home):
    assert resolve("/../../etc/passwd") == home / "etc/passwd"
    assert resolve("../..") == home


def test_unique_names():
    ops_edit.write("/a.txt", "x")
    assert unique(resolve("/"), "a.txt") == "a copy.txt"
    assert unique(resolve("/"), "a.txt", "num") == "a (1).txt"


def test_list_move_copy_remove(home):
    ops_edit.mkdir("/d")
    ops_edit.write("/d/f.txt", "hi")
    ops_move.copy(["/d"], "/")
    assert {e["name"] for e in ops_list.list_dir("/")["entries"]} == {"d", "d copy"}
    ops_move.move(["/d/f.txt"], "/")
    assert (home / "f.txt").exists()
    with pytest.raises(OpError):
        ops_move.move(["/d"], "/d")  # folder into itself
    ops_move.remove(["/d copy"])
    with pytest.raises(OpError):
        ops_move.remove(["/"])


def test_chmod_validation_and_rename(home):
    ops_edit.write("/f", "x")
    ops_edit.chmod("/f", "600")
    assert os.stat(home / "f").st_mode & 0o777 == 0o600
    for bad in ("999", "rwx", "12"):
        with pytest.raises(OpError):
            ops_edit.chmod("/f", bad)
    with pytest.raises(OpError):
        ops_edit.rename("/f", "../escape")


def test_zip_and_tar_roundtrip(home):
    ops_edit.mkdir("/src")
    ops_edit.write("/src/a.txt", "data")
    for name in ("pack.zip", "pack.tar.gz"):
        made = ops_archive.compress(["/src"], "/", name)["name"]
        out = ops_archive.extract("/" + made)["path"]
        assert (home / out.lstrip("/") / "src" / "a.txt").read_text() == "data"


def test_read_flags_binary(home):
    (home / "b.bin").write_bytes(b"\0\1\2")
    assert ops_edit.read("/b.bin")["binary"] is True
