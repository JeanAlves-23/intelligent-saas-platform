from fastapi.testclient import TestClient

from app.core.security import (
    hash_password,
    verify_password,
)
from app.db.session import SessionLocal
from app.main import app
from app.models.user import User

client = TestClient(app)


def test_register_user_endpoint() -> None:
    email = "api-registration@example.com"

    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "full_name": "API Registration User",
            "password": "SecurePassword123!",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["email"] == email
    assert body["full_name"] == "API Registration User"
    assert body["is_active"] is True

    assert "password" not in body
    assert "password_hash" not in body

    db = SessionLocal()

    try:
        user = db.query(User).filter(User.email == email).one()

        assert user.password_hash != "SecurePassword123!"
        assert (
            verify_password(
                "SecurePassword123!",
                user.password_hash,
            )
            is True
        )
    finally:
        db.query(User).filter(User.email == email).delete()
        db.commit()
        db.close()


def test_register_duplicate_email_returns_conflict() -> None:
    email = "api-duplicate@example.com"

    payload = {
        "email": email,
        "full_name": "Duplicate API User",
        "password": "SecurePassword123!",
    }

    try:
        first_response = client.post(
            "/auth/register",
            json=payload,
        )

        second_response = client.post(
            "/auth/register",
            json=payload,
        )

        assert first_response.status_code == 201
        assert second_response.status_code == 409
        assert second_response.json() == {
            "detail": "Email already registered",
        }
    finally:
        db = SessionLocal()

        db.query(User).filter(User.email == email).delete()

        db.commit()
        db.close()


def test_register_invalid_email_returns_validation_error() -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": "not-an-email",
            "full_name": "Invalid Email User",
            "password": "SecurePassword123!",
        },
    )

    assert response.status_code == 422


def test_register_short_password_returns_validation_error() -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": "short-password@example.com",
            "full_name": "Short Password User",
            "password": "123",
        },
    )

    assert response.status_code == 422


def test_login_returns_access_token() -> None:
    email = "login-api@example.com"
    password = "SecurePassword123!"

    db = SessionLocal()

    user = User(
        email=email,
        full_name="Login API User",
        password_hash=hash_password(password),
    )

    try:
        db.add(user)
        db.commit()

        response = client.post(
            "/auth/login",
            json={
                "email": email,
                "password": password,
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert "access_token" in body
        assert body["token_type"] == "bearer"
    finally:
        db.rollback()
        db.query(User).filter(User.email == email).delete()
        db.commit()
        db.close()


def test_login_inactive_user_returns_forbidden() -> None:
    email = "inactive-api@example.com"
    password = "SecurePassword123!"

    db = SessionLocal()

    user = User(
        email=email,
        full_name="Inactive API User",
        password_hash=hash_password(password),
        is_active=False,
    )

    try:
        db.add(user)
        db.commit()

        response = client.post(
            "/auth/login",
            json={
                "email": email,
                "password": password,
            },
        )

        assert response.status_code == 403
        assert response.json() == {"detail": "Inactive user"}
    finally:
        db.rollback()
        db.query(User).filter(User.email == email).delete()
        db.commit()
        db.close()


def test_login_with_wrong_password_returns_unauthorized() -> None:
    email = "wrong-password-api@example.com"
    password = "SecurePassword123!"

    db = SessionLocal()

    user = User(
        email=email,
        full_name="Wrong Password API User",
        password_hash=hash_password(password),
    )

    try:
        db.add(user)
        db.commit()

        response = client.post(
            "/auth/login",
            json={
                "email": email,
                "password": "WrongPassword123!",
            },
        )

        assert response.status_code == 401
        assert response.json() == {
            "detail": "Invalid email or password",
        }
    finally:
        db.rollback()
        db.query(User).filter(User.email == email).delete()
        db.commit()
        db.close()


def test_login_with_unknown_email_returns_unauthorized() -> None:
    response = client.post(
        "/auth/login",
        json={
            "email": "unknown-api@example.com",
            "password": "SecurePassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid email or password",
    }
