import json

from backend.models import User
from backend.services import credsync


def test_user_copy_has_no_refresh_token(tmp_path, monkeypatch):
    source = tmp_path / "src.json"
    source.write_text(json.dumps({"claudeAiOauth": {"accessToken": "A", "refreshToken": "R", "expiresAt": 1}}))
    monkeypatch.setattr(credsync, "SOURCE_FILE", source)
    user = User("cs1", 0, "h")
    monkeypatch.setattr(User, "home", property(lambda self: tmp_path / "home"))
    (tmp_path / "home").mkdir()
    assert credsync.push(user)
    copy = json.loads((tmp_path / "home/.claude/.credentials.json").read_text())["claudeAiOauth"]
    assert copy["accessToken"] == "A" and copy["refreshToken"] == ""
    assert oct((tmp_path / "home/.claude/.credentials.json").stat().st_mode & 0o777) == "0o600"


def test_push_does_nothing_without_source(tmp_path, monkeypatch):
    monkeypatch.setattr(credsync, "SOURCE_FILE", tmp_path / "missing.json")
    assert credsync.push(User("cs2", 0, "h")) is False


def test_onboarding_is_seeded_once_and_preserves_existing_settings(tmp_path, monkeypatch):
    monkeypatch.setattr(User, "home", property(lambda self: tmp_path))
    user = User("cs3", 0, "h")
    (tmp_path / ".claude.json").write_text(json.dumps({"theme": "dark"}))
    credsync.seed_onboarding(user)
    assert json.loads((tmp_path / ".claude.json").read_text()) == {"theme": "dark", "hasCompletedOnboarding": True}
