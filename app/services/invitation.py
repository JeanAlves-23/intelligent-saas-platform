import secrets
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.roles import OrganizationRole
from app.models.invitation import Invitation
from app.models.membership import Membership
from app.models.user import User


class InvitationAlreadyExistsError(Exception):
    """Raised when an active invitation already exists."""


class UserAlreadyMemberError(Exception):
    """Raised when the invited user is already an organization member."""


class InvitationRoleNotAllowedError(Exception):
    """Raised when the inviter cannot assign the requested role."""


class InvitationNotFoundError(Exception):
    """Raised when an invitation cannot be found."""


class InvitationExpiredError(Exception):
    """Raised when an invitation has expired."""


class InvitationAlreadyAcceptedError(Exception):
    """Raised when an invitation has already been accepted."""


class InvitationEmailMismatchError(Exception):
    """Raised when the authenticated user does not match the invited email."""


def create_invitation(
    db: Session,
    organization_id: uuid.UUID,
    inviter_membership: Membership,
    email: str,
    role: OrganizationRole,
) -> Invitation:
    normalized_email = email.lower()

    if role == OrganizationRole.OWNER:
        raise InvitationRoleNotAllowedError

    if inviter_membership.role == OrganizationRole.ADMIN.value and role != OrganizationRole.MEMBER:
        raise InvitationRoleNotAllowedError

    existing_user = db.scalar(select(User).where(User.email == normalized_email))

    if existing_user is not None:
        existing_membership = db.scalar(
            select(Membership).where(
                Membership.user_id == existing_user.id,
                Membership.organization_id == organization_id,
            )
        )

        if existing_membership is not None:
            raise UserAlreadyMemberError

    now = datetime.now(UTC)

    existing_invitation = db.scalar(
        select(Invitation).where(
            Invitation.organization_id == organization_id,
            Invitation.email == normalized_email,
            Invitation.accepted_at.is_(None),
            Invitation.expires_at > now,
        )
    )

    if existing_invitation is not None:
        raise InvitationAlreadyExistsError

    invitation = Invitation(
        organization_id=organization_id,
        email=normalized_email,
        role=role.value,
        token=secrets.token_urlsafe(32),
        expires_at=now + timedelta(days=7),
    )

    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    return invitation


def accept_invitation(
    db: Session,
    token: str,
    user: User,
) -> Membership:
    invitation = db.scalar(
        select(Invitation).where(
            Invitation.token == token,
        )
    )

    if invitation is None:
        raise InvitationNotFoundError

    if invitation.accepted_at is not None:
        raise InvitationAlreadyAcceptedError

    now = datetime.now(UTC)

    if invitation.expires_at <= now:
        raise InvitationExpiredError

    if invitation.email.lower() != user.email.lower():
        raise InvitationEmailMismatchError

    existing_membership = db.scalar(
        select(Membership).where(
            Membership.user_id == user.id,
            Membership.organization_id == invitation.organization_id,
        )
    )

    if existing_membership is not None:
        raise UserAlreadyMemberError

    membership = Membership(
        user_id=user.id,
        organization_id=invitation.organization_id,
        role=invitation.role,
    )

    invitation.accepted_at = now

    db.add(membership)

    db.commit()
    db.refresh(membership)

    return membership
