import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.core.roles import OrganizationRole


class InvitationCreateRequest(BaseModel):
    email: EmailStr
    role: OrganizationRole


class InvitationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    email: EmailStr
    role: OrganizationRole
    expires_at: datetime
    accepted_at: datetime | None
    created_at: datetime
