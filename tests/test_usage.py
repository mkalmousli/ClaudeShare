import json
import time
from datetime import datetime, timezone

import pytest

from backend.fsworker import ops_usage
from backend.models import User
from backend.services import usage, watcher


def line(msg_id, session, ts, **tokens):
    stamp = datetime.fromtimestamp(ts, timezone.utc).isoformat().replace("+00:00", "Z")
    return json.dumps({"type": "assistant", "sessionId": session, "timestamp": stamp, "cwd": "/work/app",
                       "message": {"id": msg_id, "usage": tokens}}) + "\n"


@pytest.fixture
def logs(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    folder = tmp_path / ".claude/projects/p1"
    folder.mkdir(parents=True)
    return folder / "s.jsonl"


def test_parser_is_incremental_and_skips_partial_lines(logs):
    now = time.time()
    logs.write_text(line("m1", "s", now, input_tokens=10, output_tokens=2) + '{"partial":')
    first = ops_usage.usage({}, now - 100)
    assert [e["id"] for e in first["events"]] == ["m1"]
    with open(logs, "a") as fh:
        fh.write('"x"}\n' + line("m2", "s", now, output_tokens=1))
    second = ops_usage.usage(first["offsets"], now - 100)
    assert [e["id"] for e in second["events"]] == ["m2"]


def test_weights_and_dedupe():
    assert usage.weigh({"input": 100, "output": 10, "cache_write": 8, "cache_read": 100}) == 100 + 50 + 10 + 10


async def test_budget_exceeded_blocks_and_flags(logs, monkeypatch, tmp_path):
    now = time.time()
    logs.write_text(line("a", "s1", now, output_tokens=1000) + line("a", "s1", now, output_tokens=1000)
                    + line("b", "s2", now, output_tokens=1000))
    user = User("u1", 20001, "h", share=10.0, period="week")

    async def fake_call(_user, op, **args):
        return ops_usage.usage(args["offsets"], args["since"])

    monkeypatch.setattr(usage.fs_client, "call", fake_call)
    monkeypatch.setattr(usage.capacity, "estimate", lambda plan, used, period="week": 100_000.0)  # 10% -> 10,000
    monkeypatch.setattr(watcher, "BLOCKED_DIR", tmp_path / "blocked")
    (tmp_path / "blocked").mkdir()
    killed = []
    monkeypatch.setattr(watcher.procs, "stop_claude", lambda uid: killed.append(uid))
    await usage.refresh(user)
    snap = usage.snapshot(user)
    assert snap["used"] == 10000  # "a" counted once, "b" once
    assert snap["blocked"] and len(snap["sessions"]) == 2
    watcher.apply(user, snap)
    assert (tmp_path / "blocked" / "u1").exists() and killed == [20001]
    user.share = 100.0
    watcher.apply(user, usage.snapshot(user))
    assert not (tmp_path / "blocked" / "u1").exists()


def test_capacity_is_calibrated_from_plan_figure_and_window_from_reset():
    from backend.services import capacity
    plan = {"seven_day": 10.0, "seven_day_resets": "2026-10-19T00:00:00+00:00"}
    assert capacity.estimate(plan, 5_000_000) == 50_000_000  # 5M used = 10% of the plan
    assert capacity.estimate(plan, 5_000_000, "day") == pytest_approx(50_000_000 / 7)
    assert capacity.estimate({"seven_day": 0.5}, 1_000_000) == 100_000_000  # too little data: fallback
    start, end = capacity.plan_week(plan)
    assert (end - start).days == 7 and end.day == 19


def pytest_approx(value):
    import pytest
    return pytest.approx(value)
