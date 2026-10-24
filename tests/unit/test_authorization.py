import pytest

from app.core.roles import OrganizationRole
from app.services.authorization import (
    InsufficientRoleError,
    has_required_role,
    require_role,
)


def test_owner_has_owner_access() -> None:
    assert has_required_role(
        OrganizationRole.OWNER.value,
        OrganizationRole.OWNER,
    )


def test_owner_has_admin_access() -> None:
    assert has_required_role(
        OrganizationRole.OWNER.value,
        OrganizationRole.ADMIN,
    )


def test_admin_has_member_access() -> None:
    assert has_required_role(
        OrganizationRole.ADMIN.value,
        OrganizationRole.MEMBER,
    )


def test_member_does_not_have_admin_access() -> None:
    assert not has_required_role(
        OrganizationRole.MEMBER.value,
        OrganizationRole.ADMIN,
    )


def test_unknown_role_is_rejected() -> None:
    assert not has_required_role(
        "unknown",
        OrganizationRole.MEMBER,
    )


def test_require_role_raises_for_insufficient_role() -> None:
    with pytest.raises(InsufficientRoleError):
        require_role(
            OrganizationRole.MEMBER.value,
            OrganizationRole.ADMIN,
        )
