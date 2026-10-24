import pytest

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User
from app.services.organization import (
    OrganizationAccessDeniedError,
    get_authorized_organization,
    get_user_organizations,
)


def test_get_user_organizations_returns_only_membership_organizations() -> None:
    db = SessionLocal()

    user = User(
        email="organization-list@example.com",
        full_name="Organization List User",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization_a = Organization(
        name="Organization A",
        slug="organization-a-service-test",
    )

    organization_b = Organization(
        name="Organization B",
        slug="organization-b-service-test",
    )

    organization_without_membership = Organization(
        name="Organization C",
        slug="organization-c-service-test",
    )

    try:
        db.add_all(
            [
                user,
                organization_a,
                organization_b,
                organization_without_membership,
            ]
        )
        db.commit()

        membership_a = Membership(
            user_id=user.id,
            organization_id=organization_a.id,
        )

        membership_b = Membership(
            user_id=user.id,
            organization_id=organization_b.id,
        )

        db.add_all([membership_a, membership_b])
        db.commit()

        organizations = get_user_organizations(db, user)

        organization_ids = {organization.id for organization in organizations}

        assert organization_a.id in organization_ids
        assert organization_b.id in organization_ids
        assert organization_without_membership.id not in organization_ids
        assert len(organizations) == 2

    finally:
        db.rollback()

        db.query(Membership).filter(Membership.user_id == user.id).delete()

        db.query(User).filter(User.email == "organization-list@example.com").delete()

        db.query(Organization).filter(
            Organization.slug.in_(
                [
                    "organization-a-service-test",
                    "organization-b-service-test",
                    "organization-c-service-test",
                ]
            )
        ).delete(synchronize_session=False)

        db.commit()
        db.close()


def test_get_authorized_organization_returns_organization() -> None:
    db = SessionLocal()

    user = User(
        email="authorized-organization@example.com",
        full_name="Authorized Organization User",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization = Organization(
        name="Authorized Organization",
        slug="authorized-organization-service-test",
    )

    try:
        db.add_all([user, organization])
        db.commit()

        membership = Membership(
            user_id=user.id,
            organization_id=organization.id,
        )

        db.add(membership)
        db.commit()

        authorized_organization = get_authorized_organization(
            db,
            user,
            organization.id,
        )

        assert authorized_organization.id == organization.id
        assert authorized_organization.name == "Authorized Organization"
        assert authorized_organization.slug == ("authorized-organization-service-test")

    finally:
        db.rollback()

        db.query(Membership).filter(Membership.user_id == user.id).delete()

        db.query(User).filter(User.email == "authorized-organization@example.com").delete()

        db.query(Organization).filter(
            Organization.slug == "authorized-organization-service-test"
        ).delete()

        db.commit()
        db.close()


def test_get_authorized_organization_without_membership_is_rejected() -> None:
    db = SessionLocal()

    user = User(
        email="unauthorized-organization@example.com",
        full_name="Unauthorized Organization User",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization = Organization(
        name="Unauthorized Organization",
        slug="unauthorized-organization-service-test",
    )

    try:
        db.add_all([user, organization])
        db.commit()

        with pytest.raises(OrganizationAccessDeniedError):
            get_authorized_organization(
                db,
                user,
                organization.id,
            )

    finally:
        db.rollback()

        db.query(Membership).filter(Membership.user_id == user.id).delete()

        db.query(User).filter(User.email == "unauthorized-organization@example.com").delete()

        db.query(Organization).filter(
            Organization.slug == "unauthorized-organization-service-test"
        ).delete()

        db.commit()
        db.close()
