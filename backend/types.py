"""GraphQL object types."""
import strawberry


@strawberry.type
class Me:
    username: str


@strawberry.type
class TerminalInfo:
    id: str
    title: str


@strawberry.type
class TerminalEvent:
    kind: str  # replay | data | exit
    data: str


@strawberry.type
class FileEntry:
    name: str
    is_dir: bool
    size: float
    mtime: float
    mode: int
    is_link: bool


@strawberry.type
class Listing:
    path: str
    entries: list[FileEntry]


@strawberry.type
class FileContent:
    binary: bool
    size: float
    content: str


@strawberry.type
class PathResult:
    path: str


@strawberry.type
class ClaudeSession:
    id: str
    project: str
    started: float
    last: float
    messages: int
    tokens: float
    live: bool


@strawberry.type
class PlanUsage:
    five_hour: float | None
    five_hour_resets: str | None
    seven_day: float | None
    seven_day_resets: str | None


@strawberry.type
class Usage:
    used: float
    budget: float
    percent: float
    period: str
    resets_at: float
    blocked: bool
    sessions: list[ClaudeSession]
    plan: PlanUsage | None
