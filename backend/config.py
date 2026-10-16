"""All runtime settings and named constants for the backend."""
import os
from pathlib import Path

DATA = Path(os.environ.get("DATA_DIR", "/data"))
HOMES = DATA / "home"
SOURCE_HOME = DATA / "source"
USERS_FILE = DATA / "users.json"
SECRET_FILE = DATA / "secret"
RUN_DIR = Path(os.environ.get("RUN_DIR", "/run/claudeshare"))
BLOCKED_DIR = RUN_DIR / "blocked"
STATIC_DIR = Path(__file__).resolve().parent.parent / "frontend"
APP_ROOT = Path(__file__).resolve().parent.parent
CLAUDE_REAL = Path(os.environ.get("CLAUDE_REAL", "/opt/claude-real"))

PORT = int(os.environ.get("PORT", "3000"))
PUBLIC_URL = os.environ.get("PUBLIC_URL", f"http://localhost:{PORT}")
COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "auto")  # true | false | auto
COOKIE_NAME = "cs_session"
SESSION_DAYS = 7
MAX_TERMINALS = int(os.environ.get("MAX_TERMINALS", "8"))
SCROLLBACK_CHARS = 300_000
UID_BASE = 10_000
NAME_PATTERN = r"^[a-z][a-z0-9_-]{1,23}$"
RESERVED_NAMES = {"root", "daemon", "bin", "sys", "nobody", "admin", "claude", "node", "www-data"}

# Usage accounting: weighted tokens per message component.
WEIGHTS = {"input": 1.0, "output": 5.0, "cache_write": 1.25, "cache_read": 0.1}
PERIODS = ("day", "week", "month")
DEFAULT_PERIOD = os.environ.get("USAGE_PERIOD", "week")
# The plan's real size is measured at runtime; this is only the starting guess until enough data exists.
FALLBACK_PLAN_TOKENS = float(os.environ.get("USAGE_PLAN_TOKENS", "100000000"))
MIN_PLAN_PERCENT = 2.0  # below this the plan figure is too small to calibrate from
DEFAULT_SHARE = float(os.environ.get("USAGE_SHARE", "20"))  # percent of the plan per person
PERIOD_WEEKS = {"day": 1 / 7, "week": 1.0, "month": 30 / 7}
RESET_WEEKDAY = int(os.environ.get("USAGE_RESET_DAY", "0"))  # 0 = Monday
RESET_HOUR = int(os.environ.get("USAGE_RESET_HOUR", "0"))  # UTC
HISTORY_DAYS = 32
WATCH_SECONDS = 5
CREDSYNC_SECONDS = 30
PLAN_CACHE_SECONDS = 60

# Shared Claude login (OAuth) handling.
OAUTH_CLIENT_ID = "9d1c250a-e61b-4d11-9a68-8eb3d3e9c2a8"
OAUTH_TOKEN_URL = "https://console.anthropic.com/v1/oauth/token"
OAUTH_USAGE_URL = "https://api.anthropic.com/api/oauth/usage"
REFRESH_MARGIN_MS = 30 * 60 * 1000

# The only variables handed to user shells.
BASE_ENV = {
    "SHELL": "/bin/bash",
    "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
    "TERM": "xterm-256color",
    "COLORTERM": "truecolor",
    "LANG": "C.UTF-8",
    "DISABLE_AUTOUPDATER": "1",
    "CLAUDESHARE": "1",
}


def user_env(name: str, home: Path) -> dict[str, str]:
    return {**BASE_ENV, "HOME": str(home), "USER": name, "LOGNAME": name}
