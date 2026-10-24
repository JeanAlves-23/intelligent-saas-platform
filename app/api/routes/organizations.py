from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.organization import get_current_organization
from app.db.session import get_db
from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import OrganizationResponse
from app.services.organization import get_user_organizations

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
