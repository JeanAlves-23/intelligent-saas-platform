import uuid

import pytest

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User
from app.core.roles import OrganizationRole
from app.services.membership import (
    MembershipNotFoundError,
    list_organization_members,
    update_membership_role,
)


def test_list_organization_members_returns_only_target_organization() -> None:
    db = SessionLocal()

    user_a = User(
        email="member-list-a@example.com",
        full_name="Member List A",
        password_hash=hash_password("SecurePassword123!"),
    )

    user_b = User(
        email="member-list-b@example.com",
        full_name="Member List B",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization_a = Organization(
        name="Membership Service A",
        slug="membership-service-a",
    )

    organization_b = Organization(
        name="Membership Service B",
        slug="membership-service-b",
    )

    try:
        db.add_all([user_a, user_b, organization_a, organization_b])
        db.commit()

        membership_a = Membership(
            user_id=user_a.id,
            organization_id=organization_a.id,
            role="admin",
        )

        membership_b = Membership(
            user_id=user_b.id,
            organization_id=organization_b.id,
            role="member",
        )

        db.add_all([membership_a, membership_b])
        db.commit()

        memberships = list_organization_members(
            db,
            organization_a.id,
        )

        assert len(memberships) == 1
        assert memberships[0].user_id == user_a.id
        assert memberships[0].organization_id == organization_a.id

    finally:
        db.rollback()

        db.query(Membership).filter(
            Membership.organization_id.in_([organization_a.id, organization_b.id])
        ).delete(synchronize_session=False)

        db.query(User).filter(
            User.email.in_(
                [
                    "member-list-a@example.com",
                    "member-list-b@example.com",
                ]
            )
        ).delete(synchronize_session=False)

        db.query(Organization).filter(
            Organization.slug.in_(
                [
                    "membership-service-a",
                    "membership-service-b",
                ]
            )
        ).delete(synchronize_session=False)

        db.commit()
        db.close()


def test_update_membership_role() -> None:
    db = SessionLocal()

    user = User(
        email="role-update@example.com",
        full_name="Role Update User",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization = Organization(
        name="Role Update Organization",
        slug="role-update-organization",
    )

    try:
        db.add_all([user, organization])
        db.commit()

        membership = Membership(
            user_id=user.id,
            organization_id=organization.id,
            role="member",
        )

        db.add(membership)
        db.commit()

        updated = update_membership_role(
            db,
            organization.id,
            membership.id,
            OrganizationRole.ADMIN,
        )

        assert updated.role == "admin"

    finally:
        db.rollback()

        db.query(Membership).filter(Membership.user_id == user.id).delete()

        db.query(User).filter(User.email == "role-update@example.com").delete()

        db.query(Organization).filter(Organization.slug == "role-update-organization").delete()

        db.commit()
        db.close()


def test_update_membership_from_another_organization_is_rejected() -> None:
    db = SessionLocal()

    fake_organization_id = uuid.uuid4()
    fake_membership_id = uuid.uuid4()

    try:
        with pytest.raises(MembershipNotFoundError):
            update_membership_role(
                db,
                fake_organization_id,
                fake_membership_id,
                OrganizationRole.ADMIN,
            )
    finally:
        db.close()
