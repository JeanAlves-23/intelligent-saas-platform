import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.roles import OrganizationRole
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User


class OrganizationAccessDeniedError(Exception):
    """Raised when a user has no membership in an organization."""


class OrganizationSlugAlreadyExistsError(Exception):
    """Raised when attempting to create an organization with an existing slug."""


class OrganizationNotFoundError(Exception):
    """Raised when an organization cannot be found."""


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


def create_organization(
    db: Session,
    user: User,
    name: str,
    slug: str,
) -> Organization:
    normalized_slug = slug.lower()

    existing = db.scalar(
        select(Organization).where(
            Organization.slug == normalized_slug,
        )
    )

    if existing is not None:
        raise OrganizationSlugAlreadyExistsError

    organization = Organization(
        name=name,
        slug=normalized_slug,
    )

    db.add(organization)

    try:
        db.flush()

        membership = Membership(
            user_id=user.id,
            organization_id=organization.id,
            role=OrganizationRole.OWNER.value,
        )

        db.add(membership)
        db.commit()

    except IntegrityError as exc:
        db.rollback()
        raise OrganizationSlugAlreadyExistsError from exc

    db.refresh(organization)

    return organization


def update_organization(
    db: Session,
    organization_id: uuid.UUID,
    *,
    name: str | None = None,
    slug: str | None = None,
) -> Organization:
    organization = db.get(Organization, organization_id)

    if organization is None:
        raise OrganizationNotFoundError

    if name is not None:
        organization.name = name

    if slug is not None:
        normalized_slug = slug.lower()

        existing = db.scalar(
            select(Organization).where(
                Organization.slug == normalized_slug,
                Organization.id != organization_id,
            )
        )

        if existing is not None:
            raise OrganizationSlugAlreadyExistsError

        organization.slug = normalized_slug

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise OrganizationSlugAlreadyExistsError from exc

    db.refresh(organization)

    return organization
