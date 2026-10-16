"""A running terminal: scrollback, subscribers, input, resize, output stream."""
import asyncio
import codecs
import os
import subprocess
from dataclasses import dataclass, field

from . import ptyproc

WRITE_CHUNK = 4096


@dataclass
class Term:
    id: str
    user: str
    number: int
    proc: subprocess.Popen
    fd: int
    buf: str = ""
    subs: set = field(default_factory=set)
    decoder: codecs.IncrementalDecoder = field(default_factory=lambda: codecs.getincrementaldecoder("utf-8")("replace"))


def broadcast(term: Term, event: tuple) -> None:
    for queue in term.subs:
        queue.put_nowait(event)


def write(term: Term, data: str) -> None:
    raw = data.encode()
    for idx in range(0, len(raw), WRITE_CHUNK):
        os.write(term.fd, raw[idx:idx + WRITE_CHUNK])


def resize(term: Term, cols: int, rows: int) -> None:
    if 1 < cols < 1000 and 1 < rows < 500:
        ptyproc.set_size(term.fd, cols, rows)


async def stream(term: Term):
    queue: asyncio.Queue = asyncio.Queue()
    term.subs.add(queue)
    try:
        yield ("replay", term.buf)
        while True:
            event = await queue.get()
            yield event
            if event[0] == "exit":
                return
    finally:
        term.subs.discard(queue)
