import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Any

from fastapi import HTTPException, status

JWT_SECRET = os.getenv("JWT_SECRET", "agrisense-development-secret-change-me")
TOKEN_TTL_SECONDS = 60 * 60 * 24 * 7


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 210_000)
    return f"pbkdf2_sha256$210000${_b64(salt)}${_b64(digest)}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, rounds, salt_value, digest_value = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), _unb64(salt_value), int(rounds))
        return hmac.compare_digest(digest, _unb64(digest_value))
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: int, email: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": str(user_id), "email": email, "exp": int(time.time()) + TOKEN_TTL_SECONDS}
    encoded_header = _json_b64(header)
    encoded_payload = _json_b64(payload)
    signature = _sign(f"{encoded_header}.{encoded_payload}")
    return f"{encoded_header}.{encoded_payload}.{signature}"


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        encoded_header, encoded_payload, signature = token.split(".", 2)
        message = f"{encoded_header}.{encoded_payload}"
        if not hmac.compare_digest(signature, _sign(message)):
            raise ValueError("invalid signature")
        payload = json.loads(_unb64(encoded_payload))
        if int(payload.get("exp", 0)) < int(time.time()):
            raise ValueError("expired token")
        return payload
    except (ValueError, TypeError, json.JSONDecodeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired login token")


def _sign(message: str) -> str:
    return _b64(hmac.new(JWT_SECRET.encode(), message.encode(), hashlib.sha256).digest())


def _json_b64(value: dict[str, Any]) -> str:
    return _b64(json.dumps(value, separators=(",", ":")).encode())


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
