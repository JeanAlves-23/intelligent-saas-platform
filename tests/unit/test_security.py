from app.core.security import hash_password, verify_password

import jwt

from app.core.config import settings
from app.core.security import create_access_token


def test_hash_password() -> None:
    password = "SecurePassword123!"

    hashed = hash_password(password)

    assert hashed != password
    assert hashed.startswith("$argon2")


def test_verify_correct_password() -> None:
    password = "SecurePassword123!"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_reject_incorrect_password() -> None:
    hashed = hash_password("CorrectPassword123!")

    assert verify_password("WrongPassword123!", hashed) is False


def test_same_password_generates_different_hashes() -> None:
    password = "SecurePassword123!"

    first = hash_password(password)
    second = hash_password(password)

    assert first != second

    assert verify_password(password, first) is True
    assert verify_password(password, second) is True


def test_create_access_token() -> None:
    token = create_access_token("user-id-123")

    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    assert payload["sub"] == "user-id-123"
    assert "iat" in payload
    assert "exp" in payload


def test_access_token_has_future_expiration() -> None:
    token = create_access_token("user-id-123")

    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    assert payload["exp"] > payload["iat"]
