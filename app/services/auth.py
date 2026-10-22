from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.auth import UserRegisterRequest


class EmailAlreadyRegisteredError(Exception):
    """Raised when attempting to register an existing email."""


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
