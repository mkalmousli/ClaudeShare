"""Plain data models shared across the backend."""
from dataclasses import dataclass, asdict, fields
from pathlib import Path

from .config import HOMES


@dataclass
class User:
    name: str
    uid: int
    hash: str
    tv: int = 1  # token version: bumping it signs everyone out
    created: str = ""
    last_login: str = ""
    budget: float | None = None  # weighted tokens; None = server default
    period: str | None = None  # day | week | month; None = server default

    @property
    def home(self) -> Path:
        return HOMES / self.name

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, name: str, raw: dict) -> "User":
        known = {f.name for f in fields(cls)}
        return cls(name=name, **{k: v for k, v in raw.items() if k in known and k != "name"})
