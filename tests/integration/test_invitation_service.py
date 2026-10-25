import pytest

from app.core.roles import OrganizationRole
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.invitation import Invitation
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User
from app.services.invitation import (
    InvitationAlreadyExistsError,
    InvitationRoleNotAllowedError,
    UserAlreadyMemberError,
    create_invitation,
)


def test_owner_can_create_member_invitation() -> None:
    db = SessionLocal()

    user = User(
        email="invitation-owner@example.com",
        full_name="Invitation Owner",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization = Organization(
        name="Invitation Organization",
        slug="invitation-owner-member",
    )

    try:
        db.add_all([user, organization])
        db.commit()

        membership = Membership(
            user_id=user.id,
            organization_id=organization.id,
            role=OrganizationRole.OWNER.value,
        )

        db.add(membership)
        db.commit()

        invitation = create_invitation(
            db,
            organization.id,
            membership,
            "new.member@example.com",
            OrganizationRole.MEMBER,
        )

        assert invitation.email == "new.member@example.com"
        assert invitation.role == OrganizationRole.MEMBER.value
        assert invitation.token
        assert invitation.accepted_at is None

    finally:
        db.rollback()
        db.query(Invitation).filter(Invitation.organization_id == organization.id).delete()
        db.query(Membership).filter(Membership.user_id == user.id).delete()
        db.query(Organization).filter(Organization.id == organization.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()
        db.close()


def test_owner_can_create_admin_invitation() -> None:
    db = SessionLocal()

    user = User(
        email="invitation-owner-admin@example.com",
        full_name="Invitation Owner Admin",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization = Organization(
        name="Invitation Admin Organization",
        slug="invitation-owner-admin",
    )

    try:
        db.add_all([user, organization])
        db.commit()

        membership = Membership(
            user_id=user.id,
            organization_id=organization.id,
            role=OrganizationRole.OWNER.value,
        )

        db.add(membership)
        db.commit()

        invitation = create_invitation(
            db,
            organization.id,
            membership,
            "new.admin@example.com",
            OrganizationRole.ADMIN,
        )

        assert invitation.role == OrganizationRole.ADMIN.value

    finally:
        db.rollback()
        db.query(Invitation).filter(Invitation.organization_id == organization.id).delete()
        db.query(Membership).filter(Membership.user_id == user.id).delete()
        db.query(Organization).filter(Organization.id == organization.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()
        db.close()


def test_admin_cannot_create_admin_invitation() -> None:
    db = SessionLocal()

    organization = Organization(
        name="Admin Restriction Organization",
        slug="admin-invitation-restriction",
    )

    user = User(
        email="invitation-admin@example.com",
        full_name="Invitation Admin",
        password_hash=hash_password("SecurePassword123!"),
    )

    try:
        db.add_all([user, organization])
        db.commit()

        membership = Membership(
            user_id=user.id,
            organization_id=organization.id,
            role=OrganizationRole.ADMIN.value,
        )

        db.add(membership)
        db.commit()

        with pytest.raises(InvitationRoleNotAllowedError):
            create_invitation(
                db,
                organization.id,
                membership,
                "another.admin@example.com",
                OrganizationRole.ADMIN,
            )

    finally:
        db.rollback()
        db.query(Membership).filter(Membership.user_id == user.id).delete()
        db.query(Organization).filter(Organization.id == organization.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()
        db.close()


def test_owner_role_cannot_be_invited() -> None:
    db = SessionLocal()

    organization = Organization(
        name="Owner Role Organization",
        slug="owner-role-invitation",
    )

    user = User(
        email="owner-role-user@example.com",
        full_name="Owner Role User",
        password_hash=hash_password("SecurePassword123!"),
    )

    try:
        db.add_all([user, organization])
        db.commit()

        membership = Membership(
            user_id=user.id,
            organization_id=organization.id,
            role=OrganizationRole.OWNER.value,
        )

        db.add(membership)
        db.commit()

        with pytest.raises(InvitationRoleNotAllowedError):
            create_invitation(
                db,
                organization.id,
                membership,
                "future.owner@example.com",
                OrganizationRole.OWNER,
            )

    finally:
        db.rollback()
        db.query(Membership).filter(Membership.user_id == user.id).delete()
        db.query(Organization).filter(Organization.id == organization.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()
        db.close()


def test_existing_member_cannot_be_invited() -> None:
    db = SessionLocal()

    organization = Organization(
        name="Existing Member Organization",
        slug="existing-member-invitation",
    )

    owner = User(
        email="existing-owner@example.com",
        full_name="Existing Owner",
        password_hash=hash_password("SecurePassword123!"),
    )

    existing_user = User(
        email="existing-member@example.com",
        full_name="Existing Member",
        password_hash=hash_password("SecurePassword123!"),
    )

    try:
        db.add_all([organization, owner, existing_user])
        db.commit()

        owner_membership = Membership(
            user_id=owner.id,
            organization_id=organization.id,
            role=OrganizationRole.OWNER.value,
        )

        existing_membership = Membership(
            user_id=existing_user.id,
            organization_id=organization.id,
            role=OrganizationRole.MEMBER.value,
        )

        db.add_all([owner_membership, existing_membership])
        db.commit()

        with pytest.raises(UserAlreadyMemberError):
            create_invitation(
                db,
                organization.id,
                owner_membership,
                existing_user.email,
                OrganizationRole.MEMBER,
            )

    finally:
        db.rollback()
        db.query(Invitation).filter(Invitation.organization_id == organization.id).delete()
        db.query(Membership).filter(Membership.organization_id == organization.id).delete()
        db.query(Organization).filter(Organization.id == organization.id).delete()
        db.query(User).filter(User.id.in_([owner.id, existing_user.id])).delete()
        db.commit()
        db.close()


def test_duplicate_active_invitation_is_rejected() -> None:
    db = SessionLocal()

    organization = Organization(
        name="Duplicate Invitation Organization",
        slug="duplicate-active-invitation",
    )

    owner = User(
        email="duplicate-invitation-owner@example.com",
        full_name="Duplicate Invitation Owner",
        password_hash=hash_password("SecurePassword123!"),
    )

    try:
        db.add_all([organization, owner])
        db.commit()

        membership = Membership(
            user_id=owner.id,
            organization_id=organization.id,
            role=OrganizationRole.OWNER.value,
        )

        db.add(membership)
        db.commit()

        create_invitation(
            db,
            organization.id,
            membership,
            "duplicate@example.com",
            OrganizationRole.MEMBER,
        )

        with pytest.raises(InvitationAlreadyExistsError):
            create_invitation(
                db,
                organization.id,
                membership,
                "duplicate@example.com",
                OrganizationRole.MEMBER,
            )

    finally:
        db.rollback()
        db.query(Invitation).filter(Invitation.organization_id == organization.id).delete()
        db.query(Membership).filter(Membership.organization_id == organization.id).delete()
        db.query(Organization).filter(Organization.id == organization.id).delete()
        db.query(User).filter(User.id == owner.id).delete()
        db.commit()
        db.close()
