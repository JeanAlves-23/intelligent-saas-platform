import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.roles import OrganizationRole
from app.models.membership import Membership


class MembershipNotFoundError(Exception):
    """Raised when a membership cannot be found in the organization."""


def list_organization_members(
    db: Session,
    organization_id: uuid.UUID,
) -> list[Membership]:
    statement = (
        select(Membership)
        .options(joinedload(Membership.user))
        .where(Membership.organization_id == organization_id)
        .order_by(Membership.created_at)
    )

    return list(db.scalars(statement).all())


def update_membership_role(
    db: Session,
    organization_id: uuid.UUID,
    membership_id: uuid.UUID,
    role: OrganizationRole,
) -> Membership:
    statement = (
        select(Membership)
        .options(joinedload(Membership.user))
        .where(
            Membership.id == membership_id,
            Membership.organization_id == organization_id,
        )
    )

    membership = db.scalar(statement)

    if membership is None:
        raise MembershipNotFoundError

    membership.role = role.value

    db.commit()
    db.refresh(membership)

    return membership
