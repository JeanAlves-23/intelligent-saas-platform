import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db
from app.models.organization import Organization
from app.models.user import User
from app.services.organization import (
    OrganizationAccessDeniedError,
    get_authorized_organization,
)


def get_current_organization(
    organization_id: Annotated[uuid.UUID, Path()],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> Organization:
    try:
        return get_authorized_organization(
            db,
            current_user,
            organization_id,
        )
    except OrganizationAccessDeniedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization access denied",
        ) from exc
