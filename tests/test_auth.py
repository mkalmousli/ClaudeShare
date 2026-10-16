import time

from backend.models import User
from backend.services import passwords, ratelimit, sessions, store


def test_key_hash_roundtrip_and_dummy():
    key = passwords.new_key()
    stored = passwords.hash_key(key)
    assert passwords.verify_key(key, stored)
    assert not passwords.verify_key(key + "x", stored)
    assert not passwords.verify_key(key, None)  # unknown user never validates


def test_session_token_rejects_tampering_and_version_bump():
    store.save({"zed": User("zed", 10099, "h", tv=1)})
    token = sessions.issue(store.get("zed"))
    assert sessions.parse(token).name == "zed"
    assert sessions.parse(token[:-2] + "xx") is None
    assert sessions.parse("garbage") is None
    store.update("zed", tv=2)  # changing a key bumps the version
    assert sessions.parse(token) is None


def test_rate_limit_blocks_after_limit():
    key = f"t:{time.time()}"
    assert not ratelimit.blocked(key, 3)
    for _ in range(3):
        ratelimit.record(key)
    assert ratelimit.blocked(key, 3)
