import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.authorization import require_organization_role
from app.api.dependencies.organization import get_current_organization
from app.core.roles import OrganizationRole
from app.db.session import get_db
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User
from app.schemas.invitation import (
    InvitationCreateRequest,
    InvitationResponse,
)
from app.schemas.membership import (
    MembershipResponse,
    MembershipRoleUpdateRequest,
)
from app.schemas.organization import (
    OrganizationCreateRequest,
    OrganizationResponse,
    OrganizationUpdateRequest,
)
from app.services.invitation import (
    InvitationAlreadyExistsError,
    InvitationRoleNotAllowedError,
    UserAlreadyMemberError,
    create_invitation,
)
from app.services.membership import (
    MembershipNotFoundError,
    list_organization_members,
    update_membership_role,
)
from app.services.organization import (
    OrganizationNotFoundError,
    OrganizationSlugAlreadyExistsError,
    create_organization,
    delete_organization,
    get_user_organizations,
    update_organization,
)

router = APIRouter(
    prefix="/organizations",
    tags=["organizations"],
)


@router.get(
    "",
    response_model=list[OrganizationResponse],
)
def list_organizations(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[OrganizationResponse]:
    organizations = get_user_organizations(
        db,
        current_user,
    )

    return [OrganizationResponse.model_validate(organization) for organization in organizations]


@router.get(
    "/{organization_id}",
    response_model=OrganizationResponse,
)
def get_organization(
    organization: Annotated[
        Organization,
        Depends(get_current_organization),
    ],
) -> OrganizationResponse:
    return OrganizationResponse.model_validate(organization)


@router.get(
    "/{organization_id}/members",
    response_model=list[MembershipResponse],
)
def list_members(
    organization_id: uuid.UUID,
    membership: Annotated[
        Membership,
        Depends(
            require_organization_role(
                OrganizationRole.ADMIN,
            )
        ),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> list[MembershipResponse]:
    memberships = list_organization_members(
        db,
        organization_id,
    )

    return [MembershipResponse.model_validate(item) for item in memberships]


@router.patch(
    "/{organization_id}/members/{membership_id}",
    response_model=MembershipResponse,
)
def update_member_role(
    organization_id: uuid.UUID,
    membership_id: uuid.UUID,
    payload: MembershipRoleUpdateRequest,
    owner_membership: Annotated[
        Membership,
        Depends(
            require_organization_role(
                OrganizationRole.OWNER,
            )
        ),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> MembershipResponse:
    try:
        updated_membership = update_membership_role(
            db,
            organization_id,
            membership_id,
            payload.role,
        )
    except MembershipNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Membership not found",
        ) from exc

    return MembershipResponse.model_validate(updated_membership)


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_organization_endpoint(
    payload: OrganizationCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> OrganizationResponse:
    try:
        organization = create_organization(
            db,
            current_user,
            payload.name,
            payload.slug,
        )
    except OrganizationSlugAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organization slug already exists",
        ) from exc

    return OrganizationResponse.model_validate(organization)


@router.patch(
    "/{organization_id}",
    response_model=OrganizationResponse,
)
def update_organization_endpoint(
    organization_id: uuid.UUID,
    payload: OrganizationUpdateRequest,
    membership: Annotated[
        Membership,
        Depends(require_organization_role(OrganizationRole.ADMIN)),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> OrganizationResponse:
    try:
        organization = update_organization(
            db,
            organization_id,
            name=payload.name,
            slug=payload.slug,
        )
    except OrganizationSlugAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organization slug already exists",
        ) from exc
    except OrganizationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        ) from exc

    return OrganizationResponse.model_validate(organization)


@router.delete(
    "/{organization_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_organization_endpoint(
    organization_id: uuid.UUID,
    owner_membership: Annotated[
        Membership,
        Depends(require_organization_role(OrganizationRole.OWNER)),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    try:
        delete_organization(
            db,
            organization_id,
        )
    except OrganizationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found",
        ) from exc


@router.post(
    "/{organization_id}/invitations",
    response_model=InvitationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_organization_invitation(
    organization_id: uuid.UUID,
    payload: InvitationCreateRequest,
    inviter_membership: Annotated[
        Membership,
        Depends(require_organization_role(OrganizationRole.ADMIN)),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> InvitationResponse:
    try:
        invitation = create_invitation(
            db,
            organization_id,
            inviter_membership,
            payload.email,
            payload.role,
        )
    except InvitationRoleNotAllowedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invitation role not allowed",
        ) from exc
    except UserAlreadyMemberError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already an organization member",
        ) from exc
    except InvitationAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Active invitation already exists",
        ) from exc

    return InvitationResponse.model_validate(invitation)
