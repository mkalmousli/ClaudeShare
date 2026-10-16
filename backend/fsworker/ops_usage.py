"""Incrementally parse Claude's own session logs (~/.claude/projects/**/*.jsonl)."""
import json
import os
from datetime import datetime

from .paths import home

KEYS = {"input": "input_tokens", "output": "output_tokens",
        "cache_write": "cache_creation_input_tokens", "cache_read": "cache_read_input_tokens"}


def _epoch(stamp: str) -> float:
    return datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp()


def _event(line: dict, project: str) -> dict | None:
    msg = line.get("message")
    if line.get("type") != "assistant" or not isinstance(msg, dict) or not msg.get("usage"):
        return None
    usage = msg["usage"]
    try:
        return {"id": msg.get("id") or line.get("uuid"), "ts": _epoch(line["timestamp"]),
                "session": line.get("sessionId", ""), "project": line.get("cwd") or project,
                "tokens": {k: int(usage.get(v) or 0) for k, v in KEYS.items()}}
    except (KeyError, ValueError):
        return None


def _read_new(path: str, offset: int, project: str, since: float):
    events, size = [], os.path.getsize(path)
    if size < offset:
        offset = 0  # file was truncated or replaced
    with open(path, "rb") as fh:
        fh.seek(offset)
        for raw in fh:
            if not raw.endswith(b"\n"):
                break  # partially written line: pick it up next time
            offset += len(raw)
            try:
                event = _event(json.loads(raw), os.path.basename(os.path.dirname(path)))
            except ValueError:
                continue
            if event and event["ts"] >= since:
                events.append(event)
    return events, offset


def usage(offsets: dict[str, int], since: float) -> dict:
    root = home() / ".claude" / "projects"
    events, new_offsets = [], {}
    for base, _dirs, files in os.walk(root):
        for name in files:
            if name.endswith(".jsonl"):
                path = os.path.join(base, name)
                found, new_offsets[path] = _read_new(path, offsets.get(path, 0), base, since)
                events += found
    return {"events": events, "offsets": new_offsets}


OPS = {"usage": usage}
