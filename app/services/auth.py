from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.auth import UserRegisterRequest

from app.core.security import create_access_token, verify_password


class EmailAlreadyRegisteredError(Exception):
    """Raised when attempting to register an existing email."""


class InvalidCredentialsError(Exception):
    """Raised when login credentials are invalid."""


class InactiveUserError(Exception):
    """Raised when an inactive user attempts to authenticate."""


def register_user(
    db: Session,
    data: UserRegisterRequest,
) -> User:
    normalized_email = str(data.email).lower()

    existing_user = db.scalar(select(User).where(User.email == normalized_email))

    if existing_user is not None:
        raise EmailAlreadyRegisteredError

    user = User(
        email=normalized_email,
        full_name=data.full_name,
        password_hash=hash_password(data.password),
    )

    db.add(user)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise EmailAlreadyRegisteredError from exc

    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> str:
    normalized_email = email.lower()

    user = db.scalar(select(User).where(User.email == normalized_email))

    if user is None:
        raise InvalidCredentialsError

    if not verify_password(password, user.password_hash):
        raise InvalidCredentialsError

    if not user.is_active:
        raise InactiveUserError

    return create_access_token(str(user.id))
