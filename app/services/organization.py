import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User


class OrganizationAccessDeniedError(Exception):
    """Raised when a user has no membership in an organization."""


def get_user_organizations(
    db: Session,
    user: User,
) -> list[Organization]:
    statement = (
        select(Organization)
        .join(
            Membership,
            Membership.organization_id == Organization.id,
        )
        .where(Membership.user_id == user.id)
        .order_by(Organization.name)
    )

    return list(db.scalars(statement).all())


def get_authorized_organization(
    db: Session,
    user: User,
    organization_id: uuid.UUID,
) -> Organization:
    statement = (
        select(Organization)
        .join(
            Membership,
            Membership.organization_id == Organization.id,
        )
        .where(
            Organization.id == organization_id,
            Membership.user_id == user.id,
        )
    )

    organization = db.scalar(statement)

    if organization is None:
        raise OrganizationAccessDeniedError

    return organization
