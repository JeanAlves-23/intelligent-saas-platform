from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.membership import MembershipResponse
from app.services.invitation import (
    InvitationAlreadyAcceptedError,
    InvitationEmailMismatchError,
    InvitationExpiredError,
    InvitationNotFoundError,
    UserAlreadyMemberError,
    accept_invitation,
)

router = APIRouter(
    prefix="/invitations",
    tags=["invitations"],
)


@router.post(
    "/{token}/accept",
    response_model=MembershipResponse,
)
def accept_invitation_endpoint(
    token: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> MembershipResponse:
    try:
        membership = accept_invitation(
            db,
            token,
            current_user,
        )
    except InvitationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found",
        ) from exc
    except InvitationExpiredError as exc:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Invitation expired",
        ) from exc
    except InvitationAlreadyAcceptedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Invitation already accepted",
        ) from exc
    except InvitationEmailMismatchError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invitation email does not match authenticated user",
        ) from exc
    except UserAlreadyMemberError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User is already an organization member",
        ) from exc

    return MembershipResponse.model_validate(membership)
