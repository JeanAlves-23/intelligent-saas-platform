from app.core.roles import OrganizationRole


class InsufficientRoleError(Exception):
    """Raised when a membership role is insufficient for an operation."""


ROLE_LEVELS = {
    OrganizationRole.MEMBER: 1,
    OrganizationRole.ADMIN: 2,
    OrganizationRole.OWNER: 3,
}


def has_required_role(
    current_role: str,
    required_role: OrganizationRole,
) -> bool:
    try:
        role = OrganizationRole(current_role)
    except ValueError:
        return False

    return ROLE_LEVELS[role] >= ROLE_LEVELS[required_role]


def require_role(
    current_role: str,
    required_role: OrganizationRole,
) -> None:
    if not has_required_role(current_role, required_role):
        raise InsufficientRoleError
