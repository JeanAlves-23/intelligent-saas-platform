import pytest

from app.core.roles import OrganizationRole
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User
from app.services.organization import (
    OrganizationSlugAlreadyExistsError,
    create_organization,
)


def test_create_organization_creates_owner_membership() -> None:
    db = SessionLocal()

    user = User(
        email="organization-creator@example.com",
        full_name="Organization Creator",
        password_hash=hash_password("SecurePassword123!"),
    )

    try:
        db.add(user)
        db.commit()

        organization = create_organization(
            db,
            user,
            "Created Organization",
            "created-organization",
        )

        membership = (
            db.query(Membership)
            .filter(
                Membership.user_id == user.id,
                Membership.organization_id == organization.id,
            )
            .one()
        )

        assert organization.name == "Created Organization"
        assert organization.slug == "created-organization"
        assert membership.role == OrganizationRole.OWNER.value

    finally:
        db.rollback()
        db.query(Membership).filter(Membership.user_id == user.id).delete()
        db.query(Organization).filter(Organization.slug == "created-organization").delete()
        db.query(User).filter(User.email == "organization-creator@example.com").delete()
        db.commit()
        db.close()


def test_create_organization_duplicate_slug_is_rejected() -> None:
    db = SessionLocal()

    user = User(
        email="organization-duplicate@example.com",
        full_name="Organization Duplicate",
        password_hash=hash_password("SecurePassword123!"),
    )

    existing = Organization(
        name="Existing Organization",
        slug="duplicate-organization",
    )

    try:
        db.add_all([user, existing])
        db.commit()

        with pytest.raises(OrganizationSlugAlreadyExistsError):
            create_organization(
                db,
                user,
                "Another Organization",
                "duplicate-organization",
            )

    finally:
        db.rollback()
        db.query(Membership).filter(Membership.user_id == user.id).delete()
        db.query(Organization).filter(Organization.slug == "duplicate-organization").delete()
        db.query(User).filter(User.email == "organization-duplicate@example.com").delete()
        db.commit()
        db.close()
