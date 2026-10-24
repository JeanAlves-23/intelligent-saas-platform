import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.roles import OrganizationRole


class MembershipUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str
    is_active: bool


class MembershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    role: OrganizationRole
    status: str
    created_at: datetime
    updated_at: datetime
    user: MembershipUserResponse


class MembershipRoleUpdateRequest(BaseModel):
    role: OrganizationRole
