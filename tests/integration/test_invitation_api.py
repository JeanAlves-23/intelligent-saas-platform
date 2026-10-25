from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.core.roles import OrganizationRole
from app.core.security import create_access_token, hash_password
from app.db.session import SessionLocal
from app.main import app
from app.models.invitation import Invitation
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User

client = TestClient(app)


def test_accept_valid_invitation_returns_membership() -> None:
    db = SessionLocal()

    organization = Organization(
        name="Invitation API Accept",
        slug="invitation-api-accept",
    )

    user = User(
        email="invitation-api-accept@example.com",
        full_name="Invitation API Accept User",
        password_hash=hash_password("SecurePassword123!"),
    )

    try:
        db.add_all([organization, user])
        db.commit()

        invitation = Invitation(
            organization_id=organization.id,
            email=user.email,
            role=OrganizationRole.MEMBER.value,
            token="api-valid-invitation-token",
            expires_at=datetime.now(UTC) + timedelta(days=1),
        )

        db.add(invitation)
        db.commit()

        token = create_access_token(str(user.id))

        response = client.post(
            f"/invitations/{invitation.token}/accept",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200

        body = response.json()

        assert body["organization_id"] == str(organization.id)
        assert body["role"] == "member"
        assert body["user"]["email"] == user.email

        db.refresh(invitation)

        assert invitation.accepted_at is not None

    finally:
        db.rollback()
        db.query(Membership).filter(Membership.organization_id == organization.id).delete()
        db.query(Invitation).filter(Invitation.organization_id == organization.id).delete()
        db.query(Organization).filter(Organization.id == organization.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()
        db.close()


def test_accept_invitation_with_different_email_returns_forbidden() -> None:
    db = SessionLocal()

    organization = Organization(
        name="Invitation API Email Mismatch",
        slug="invitation-api-email-mismatch",
    )

    invited_user = User(
        email="invited-api@example.com",
        full_name="Invited API User",
        password_hash=hash_password("SecurePassword123!"),
    )

    authenticated_user = User(
        email="different-api@example.com",
        full_name="Different API User",
        password_hash=hash_password("SecurePassword123!"),
    )

    try:
        db.add_all([organization, invited_user, authenticated_user])
        db.commit()

        invitation = Invitation(
            organization_id=organization.id,
            email=invited_user.email,
            role=OrganizationRole.MEMBER.value,
            token="api-email-mismatch-token",
            expires_at=datetime.now(UTC) + timedelta(days=1),
        )

        db.add(invitation)
        db.commit()

        token = create_access_token(str(authenticated_user.id))

        response = client.post(
            f"/invitations/{invitation.token}/accept",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        assert response.json() == {"detail": "Invitation email does not match authenticated user"}

    finally:
        db.rollback()
        db.query(Membership).filter(Membership.organization_id == organization.id).delete()
        db.query(Invitation).filter(Invitation.organization_id == organization.id).delete()
        db.query(Organization).filter(Organization.id == organization.id).delete()
        db.query(User).filter(User.id.in_([invited_user.id, authenticated_user.id])).delete()
        db.commit()
        db.close()


def test_accept_expired_invitation_returns_gone() -> None:
    db = SessionLocal()

    organization = Organization(
        name="Invitation API Expired",
        slug="invitation-api-expired",
    )

    user = User(
        email="invitation-api-expired@example.com",
        full_name="Invitation API Expired User",
        password_hash=hash_password("SecurePassword123!"),
    )

    try:
        db.add_all([organization, user])
        db.commit()

        invitation = Invitation(
            organization_id=organization.id,
            email=user.email,
            role=OrganizationRole.MEMBER.value,
            token="api-expired-token",
            expires_at=datetime.now(UTC) - timedelta(minutes=1),
        )

        db.add(invitation)
        db.commit()

        token = create_access_token(str(user.id))

        response = client.post(
            f"/invitations/{invitation.token}/accept",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 410
        assert response.json() == {"detail": "Invitation expired"}

    finally:
        db.rollback()
        db.query(Membership).filter(Membership.organization_id == organization.id).delete()
        db.query(Invitation).filter(Invitation.organization_id == organization.id).delete()
        db.query(Organization).filter(Organization.id == organization.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()
        db.close()


def test_accept_already_accepted_invitation_returns_conflict() -> None:
    db = SessionLocal()

    organization = Organization(
        name="Invitation API Accepted",
        slug="invitation-api-accepted",
    )

    user = User(
        email="invitation-api-accepted@example.com",
        full_name="Invitation API Accepted User",
        password_hash=hash_password("SecurePassword123!"),
    )

    try:
        db.add_all([organization, user])
        db.commit()

        invitation = Invitation(
            organization_id=organization.id,
            email=user.email,
            role=OrganizationRole.MEMBER.value,
            token="api-already-accepted-token",
            expires_at=datetime.now(UTC) + timedelta(days=1),
            accepted_at=datetime.now(UTC),
        )

        db.add(invitation)
        db.commit()

        token = create_access_token(str(user.id))

        response = client.post(
            f"/invitations/{invitation.token}/accept",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 409
        assert response.json() == {"detail": "Invitation already accepted"}

    finally:
        db.rollback()
        db.query(Membership).filter(Membership.organization_id == organization.id).delete()
        db.query(Invitation).filter(Invitation.organization_id == organization.id).delete()
        db.query(Organization).filter(Organization.id == organization.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()
        db.close()


def test_accept_nonexistent_invitation_returns_not_found() -> None:
    db = SessionLocal()

    user = User(
        email="invitation-api-missing@example.com",
        full_name="Invitation API Missing",
        password_hash=hash_password("SecurePassword123!"),
    )

    try:
        db.add(user)
        db.commit()

        token = create_access_token(str(user.id))

        response = client.post(
            "/invitations/nonexistent-token/accept",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "Invitation not found"}

    finally:
        db.rollback()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()
        db.close()


def test_existing_member_cannot_accept_invitation() -> None:
    db = SessionLocal()

    organization = Organization(
        name="Invitation API Existing Member",
        slug="invitation-api-existing-member-accept",
    )

    user = User(
        email="invitation-api-existing-accept@example.com",
        full_name="Invitation API Existing Member",
        password_hash=hash_password("SecurePassword123!"),
    )

    try:
        db.add_all([organization, user])
        db.commit()

        membership = Membership(
            user_id=user.id,
            organization_id=organization.id,
            role=OrganizationRole.MEMBER.value,
        )

        invitation = Invitation(
            organization_id=organization.id,
            email=user.email,
            role=OrganizationRole.MEMBER.value,
            token="api-existing-member-token",
            expires_at=datetime.now(UTC) + timedelta(days=1),
        )

        db.add_all([membership, invitation])
        db.commit()

        token = create_access_token(str(user.id))

        response = client.post(
            f"/invitations/{invitation.token}/accept",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 409
        assert response.json() == {"detail": "User is already an organization member"}

    finally:
        db.rollback()
        db.query(Membership).filter(Membership.organization_id == organization.id).delete()
        db.query(Invitation).filter(Invitation.organization_id == organization.id).delete()
        db.query(Organization).filter(Organization.id == organization.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()
        db.close()


def test_accept_invitation_without_authentication_returns_unauthorized() -> None:
    response = client.post(
        "/invitations/some-token/accept",
    )

    assert response.status_code == 401
