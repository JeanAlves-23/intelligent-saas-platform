import pytest

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User
from app.services.organization import (
    OrganizationNotFoundError,
    delete_organization,
)


def test_delete_organization_removes_memberships() -> None:
    db = SessionLocal()

    user = User(
        email="organization-delete-service@example.com",
        full_name="Organization Delete Service",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization = Organization(
        name="Organization To Delete",
        slug="organization-delete-service",
    )

    try:
        db.add_all([user, organization])
        db.commit()

        membership = Membership(
            user_id=user.id,
            organization_id=organization.id,
            role="owner",
        )

        db.add(membership)
        db.commit()

        organization_id = organization.id
        membership_id = membership.id

        delete_organization(
            db,
            organization_id,
        )

        db.expire_all()

        assert db.get(Organization, organization_id) is None
        assert db.get(Membership, membership_id) is None

    finally:
        db.rollback()

        db.query(Membership).filter(Membership.user_id == user.id).delete()

        db.query(Organization).filter(Organization.slug == "organization-delete-service").delete()

        db.query(User).filter(User.email == "organization-delete-service@example.com").delete()

        db.commit()
        db.close()


def test_delete_nonexistent_organization_raises_error() -> None:
    db = SessionLocal()

    try:
        import uuid

        with pytest.raises(OrganizationNotFoundError):
            delete_organization(
                db,
                uuid.uuid4(),
            )

    finally:
        db.close()
