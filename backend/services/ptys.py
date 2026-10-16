"""Persistent per-user pseudo-terminals with scrollback and fan-out to subscribers."""
import asyncio
import os
import secrets

from ..config import MAX_TERMINALS, SCROLLBACK_CHARS
from ..models import User
from . import credsync, ptyproc, ptyterm

_terms: dict[str, ptyterm.Term] = {}


def for_user(name: str) -> list[ptyterm.Term]:
    return sorted((t for t in _terms.values() if t.user == name), key=lambda t: t.number)


def get(user: User, term_id: str) -> ptyterm.Term | None:
    term = _terms.get(term_id)
    return term if term and term.user == user.name else None


def create(user: User, cwd: str | None, cols: int, rows: int, run: str | None) -> ptyterm.Term:
    if len(for_user(user.name)) >= MAX_TERMINALS:
        raise ValueError(f"Terminal limit reached ({MAX_TERMINALS}). Close one first.")
    credsync.push(user)
    proc, master = ptyproc.spawn(user, cwd, cols, rows)
    used = {t.number for t in for_user(user.name)}
    number = next(n for n in range(1, MAX_TERMINALS + 2) if n not in used)
    term = ptyterm.Term(secrets.token_hex(6), user.name, number, proc, master)
    _terms[term.id] = term
    asyncio.get_running_loop().add_reader(master, _on_readable, term)
    if run == "claude":
        ptyterm.write(term, "claude\r")
    return term


def _on_readable(term: ptyterm.Term) -> None:
    try:
        data = os.read(term.fd, 65536)
    except OSError:
        data = b""
    if not data:
        return _finish(term)
    text = term.decoder.decode(data)
    term.buf = (term.buf + text)[-SCROLLBACK_CHARS:]
    ptyterm.broadcast(term, ("data", text))


def _finish(term: ptyterm.Term) -> None:
    asyncio.get_running_loop().remove_reader(term.fd)
    os.close(term.fd)
    code = term.proc.poll()
    _terms.pop(term.id, None)
    ptyterm.broadcast(term, ("exit", str(code if code is not None else 0)))


def close(term: ptyterm.Term) -> None:
    term.proc.terminate()
    asyncio.get_running_loop().call_later(2, lambda: term.proc.poll() is None and term.proc.kill())


def kill_all(name: str) -> None:
    for term in for_user(name):
        term.proc.kill()
