from fastapi.testclient import TestClient

from app.core.security import verify_password
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
