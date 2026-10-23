from app.core.security import hash_password

import pytest

import jwt

from app.core.security import verify_password
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.auth import UserRegisterRequest
from app.services.auth import (
    EmailAlreadyRegisteredError,
    InactiveUserError,
    InvalidCredentialsError,
    authenticate_user,
    register_user,
)


def test_register_user() -> None:
    db = SessionLocal()

    data = UserRegisterRequest(
        email="registration@example.com",
        full_name="Registration User",
        password="SecurePassword123!",
    )

    try:
        user = register_user(db, data)

        assert user.id is not None
        assert user.email == "registration@example.com"
        assert user.full_name == "Registration User"
        assert user.password_hash != data.password
        assert verify_password(data.password, user.password_hash) is True
    finally:
        db.rollback()

        db.query(User).filter(User.email == "registration@example.com").delete()

        db.commit()
        db.close()


def test_register_user_normalizes_email() -> None:
    db = SessionLocal()

    data = UserRegisterRequest(
        email="Registration.Email@Example.COM",
        full_name="Normalized User",
        password="SecurePassword123!",
    )

    try:
        user = register_user(db, data)

        assert user.email == "registration.email@example.com"
    finally:
        db.rollback()

        db.query(User).filter(User.email == "registration.email@example.com").delete()

        db.commit()
        db.close()


def test_register_duplicate_email_is_rejected() -> None:
    db = SessionLocal()

    first_data = UserRegisterRequest(
        email="duplicate-registration@example.com",
        full_name="First User",
        password="SecurePassword123!",
    )

    second_data = UserRegisterRequest(
        email="duplicate-registration@example.com",
        full_name="Second User",
        password="AnotherPassword123!",
    )

    try:
        register_user(db, first_data)

        with pytest.raises(EmailAlreadyRegisteredError):
            register_user(db, second_data)
    finally:
        db.rollback()

        db.query(User).filter(User.email == "duplicate-registration@example.com").delete()

        db.commit()
        db.close()


def test_authenticate_user_returns_access_token() -> None:
    db = SessionLocal()

    user = User(
        email="login@example.com",
        full_name="Login User",
        password_hash=hash_password("SecurePassword123!"),
    )

    try:
        db.add(user)
        db.commit()

        token = authenticate_user(
            db,
            "login@example.com",
            "SecurePassword123!",
        )

        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        assert payload["sub"] == str(user.id)
    finally:
        db.rollback()
        db.query(User).filter(User.email == "login@example.com").delete()
        db.commit()
        db.close()
