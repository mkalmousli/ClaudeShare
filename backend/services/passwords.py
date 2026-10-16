"""Access keys: generation, scrypt hashing, constant-time verification."""
import hashlib
import hmac
import secrets

_N, _R, _P, _LEN = 2**14, 8, 1, 32


def new_key() -> str:
    return secrets.token_urlsafe(18)


def _derive(key: str, salt: bytes) -> bytes:
    return hashlib.scrypt(key.encode(), salt=salt, n=_N, r=_R, p=_P, dklen=_LEN)


def hash_key(key: str) -> str:
    salt = secrets.token_bytes(16)
    return f"scrypt${salt.hex()}${_derive(key, salt).hex()}"


_DUMMY = hash_key("dummy")


def verify_key(key: str, stored: str | None) -> bool:
    """Always burns one scrypt round so unknown users cost the same as wrong keys."""
    _, salt_hex, hash_hex = (stored or _DUMMY).split("$")
    digest = _derive(key, bytes.fromhex(salt_hex))
    return hmac.compare_digest(digest, bytes.fromhex(hash_hex)) and stored is not None
