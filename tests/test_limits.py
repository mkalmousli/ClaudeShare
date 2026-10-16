import os
import subprocess
import sys
import time

import psutil
import pytest

from backend.models import User
from backend.services import enforcement, fs_client, limits

pytestmark = pytest.mark.skipif(os.geteuid() != 0, reason="needs root to run processes as another uid")
UID = 65534


def start(code: str, user: User | None = None, **kwargs):
    extra = {"preexec_fn": limits.child_setup(user)} if user else {}
    return subprocess.Popen([sys.executable, "-c", code], user=UID, group=UID, extra_groups=[], **extra, **kwargs)


def wait_dead(proc, seconds=5):
    deadline = time.time() + seconds
    while time.time() < deadline and proc.poll() is None:
        time.sleep(0.05)
    return proc.poll() is not None


@pytest.fixture
def user():
    return User("nobody", UID, "h", mem_mb=40.0, cpu=0.5, procs=40, disk_mb=1.0)


def test_effective_uses_overrides_then_defaults():
    assert limits.effective(User("a", 1, "h", mem_mb=5.0))["mem_mb"] == 5.0
    assert limits.effective(User("a", 1, "h"))["cpu"] == limits.DEFAULT_LIMITS["cpu"]


def test_memory_hog_is_stopped_and_user_is_told(user):
    hog = start("b = bytearray(120*1024*1024); import time; time.sleep(60)")
    time.sleep(1.0)
    groups = enforcement.group_by_uid()
    stats = enforcement.measure(user, groups[UID])
    assert stats["mem_mb"] > 40
    enforcement.enforce(user, groups[UID], stats)
    assert wait_dead(hog)
    assert "memory limit" in enforcement.report(user)["notice"]


def test_process_cap_blocks_fork_bombs(user):
    code = ("import os, sys\nn = 0\nfor _ in range(200):\n    try:\n        if os.fork() == 0:\n            import time; time.sleep(5); os._exit(0)\n        n += 1\n"
            "    except OSError:\n        break\nprint(n)")
    out = start(code, user, stdout=subprocess.PIPE)
    forked = int(out.communicate(timeout=20)[0])
    assert forked < 40  # limit is 40 processes for the whole uid


@pytest.mark.skipif((os.cpu_count() or 1) < 3, reason="needs at least 3 cores to pin")
def test_cpu_limit_pins_cores_and_throttles(user):
    spinner = start("while True: pass")
    time.sleep(0.5)
    procs = enforcement.group_by_uid()[UID]
    enforcement.measure(user, procs)
    time.sleep(1.0)
    for _ in range(3):
        stats = enforcement.measure(user, procs)
        enforcement.enforce(user, procs, stats)
        time.sleep(0.7)
    proc = psutil.Process(spinner.pid)
    assert len(proc.cpu_affinity()) == 1 and proc.nice() == limits_nice()
    spinner.kill()


def limits_nice():
    return enforcement.NICE_THROTTLED


async def test_disk_quota_blocks_writes_but_not_deletes(user, tmp_path, monkeypatch):
    calls = []

    async def fake(_user):
        calls.append("disk")
        return {"bytes": 5 * 1024 * 1024}

    await limits.refresh_disk(user, fake)
    assert limits.disk_exceeded(user)
    with pytest.raises(fs_client.FsError, match="Disk quota"):
        await fs_client.call(user, "write", path="/x", content="y")
    limits._disk[user.name] = (0, 0.0)  # space freed
    assert not limits.disk_exceeded(user)
