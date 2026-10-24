import uuid
from typing import Annotated, Callable

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.core.roles import OrganizationRole
from app.db.session import get_db
from app.models.membership import Membership
from app.models.user import User
from app.services.authorization import (
    InsufficientRoleError,
    require_role,
)


def require_organization_role(
    required_role: OrganizationRole,
) -> Callable[..., Membership]:
    def dependency(
        organization_id: Annotated[uuid.UUID, Path()],
        current_user: Annotated[User, Depends(get_current_user)],
        db: Annotated[Session, Depends(get_db)],
    ) -> Membership:
        membership = db.scalar(
            select(Membership).where(
                Membership.user_id == current_user.id,
                Membership.organization_id == organization_id,
            )
        )

        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Organization access denied",
            )

        try:
            require_role(
                membership.role,
                required_role,
            )
        except InsufficientRoleError as exc:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient organization role",
            ) from exc

        return membership

    return dependency
