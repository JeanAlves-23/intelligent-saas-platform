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


def test_list_organizations_returns_only_user_memberships() -> None:
    db = SessionLocal()

    user = User(
        email="organization-api@example.com",
        full_name="Organization API User",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization_a = Organization(
        name="Organization API A",
        slug="organization-api-a",
    )

    organization_b = Organization(
        name="Organization API B",
        slug="organization-api-b",
    )

    organization_without_membership = Organization(
        name="Organization API C",
        slug="organization-api-c",
    )

    try:
        db.add_all(
            [
                user,
                organization_a,
                organization_b,
                organization_without_membership,
            ]
        )
        db.commit()

        db.add_all(
            [
                Membership(
                    user_id=user.id,
                    organization_id=organization_a.id,
                ),
                Membership(
                    user_id=user.id,
                    organization_id=organization_b.id,
                ),
            ]
        )
        db.commit()

        token = create_access_token(str(user.id))

        response = client.get(
            "/organizations",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert response.status_code == 200

        body = response.json()

        returned_slugs = {item["slug"] for item in body}

        assert "organization-api-a" in returned_slugs
        assert "organization-api-b" in returned_slugs
        assert "organization-api-c" not in returned_slugs
        assert len(body) == 2

    finally:
        db.rollback()

        db.query(Membership).filter(Membership.user_id == user.id).delete()

        db.query(User).filter(User.email == "organization-api@example.com").delete()

        db.query(Organization).filter(
            Organization.slug.in_(
                [
                    "organization-api-a",
                    "organization-api-b",
                    "organization-api-c",
                ]
            )
        ).delete(synchronize_session=False)

        db.commit()
        db.close()


def test_list_organizations_without_memberships_returns_empty_list() -> None:
    db = SessionLocal()

    user = User(
        email="organization-api-empty@example.com",
        full_name="Organization API Empty User",
        password_hash=hash_password("SecurePassword123!"),
    )

    try:
        db.add(user)
        db.commit()

        token = create_access_token(str(user.id))

        response = client.get(
            "/organizations",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert response.status_code == 200
        assert response.json() == []

    finally:
        db.rollback()

        db.query(User).filter(User.email == "organization-api-empty@example.com").delete()

        db.commit()
        db.close()


def test_list_organizations_without_token_returns_unauthorized() -> None:
    response = client.get("/organizations")

    assert response.status_code == 401


def test_get_organization_returns_authorized_organization() -> None:
    db = SessionLocal()

    user = User(
        email="organization-detail@example.com",
        full_name="Organization Detail User",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization = Organization(
        name="Organization Detail",
        slug="organization-detail",
    )

    try:
        db.add_all([user, organization])
        db.commit()

        membership = Membership(
            user_id=user.id,
            organization_id=organization.id,
        )

        db.add(membership)
        db.commit()

        token = create_access_token(str(user.id))

        response = client.get(
            f"/organizations/{organization.id}",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["id"] == str(organization.id)
        assert body["name"] == "Organization Detail"
        assert body["slug"] == "organization-detail"

    finally:
        db.rollback()

        db.query(Membership).filter(Membership.user_id == user.id).delete()

        db.query(User).filter(User.email == "organization-detail@example.com").delete()

        db.query(Organization).filter(Organization.slug == "organization-detail").delete()

        db.commit()
        db.close()


def test_get_organization_without_membership_returns_forbidden() -> None:
    db = SessionLocal()

    user = User(
        email="organization-forbidden@example.com",
        full_name="Organization Forbidden User",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization = Organization(
        name="Organization Forbidden",
        slug="organization-forbidden",
    )

    try:
        db.add_all([user, organization])
        db.commit()

        token = create_access_token(str(user.id))

        response = client.get(
            f"/organizations/{organization.id}",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        assert response.status_code == 403
        assert response.json() == {
            "detail": "Organization access denied",
        }

    finally:
        db.rollback()

        db.query(User).filter(User.email == "organization-forbidden@example.com").delete()

        db.query(Organization).filter(Organization.slug == "organization-forbidden").delete()

        db.commit()
        db.close()


def test_get_organization_with_invalid_id_returns_validation_error() -> None:
    token = create_access_token("00000000-0000-0000-0000-000000000000")

    response = client.get(
        "/organizations/not-a-valid-uuid",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code in {401, 422}


def test_owner_can_access_admin_check() -> None:
    db = SessionLocal()

    user = User(
        email="owner-rbac@example.com",
        full_name="Owner RBAC User",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization = Organization(
        name="Owner RBAC Organization",
        slug="owner-rbac-organization",
    )

    try:
        db.add_all([user, organization])
        db.commit()

        membership = Membership(
            user_id=user.id,
            organization_id=organization.id,
            role="owner",
        )

        db.add(membership)
        db.commit()

        token = create_access_token(str(user.id))

        response = client.get(
            f"/organizations/{organization.id}/admin-check",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "status": "ok",
            "role": "owner",
        }

    finally:
        db.rollback()
        db.query(Membership).filter(Membership.user_id == user.id).delete()
        db.query(User).filter(User.email == "owner-rbac@example.com").delete()
        db.query(Organization).filter(Organization.slug == "owner-rbac-organization").delete()
        db.commit()
        db.close()


def test_admin_can_access_admin_check() -> None:
    db = SessionLocal()

    user = User(
        email="admin-rbac@example.com",
        full_name="Admin RBAC User",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization = Organization(
        name="Admin RBAC Organization",
        slug="admin-rbac-organization",
    )

    try:
        db.add_all([user, organization])
        db.commit()

        membership = Membership(
            user_id=user.id,
            organization_id=organization.id,
            role="admin",
        )

        db.add(membership)
        db.commit()

        token = create_access_token(str(user.id))

        response = client.get(
            f"/organizations/{organization.id}/admin-check",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "status": "ok",
            "role": "admin",
        }

    finally:
        db.rollback()
        db.query(Membership).filter(Membership.user_id == user.id).delete()
        db.query(User).filter(User.email == "admin-rbac@example.com").delete()
        db.query(Organization).filter(Organization.slug == "admin-rbac-organization").delete()
        db.commit()
        db.close()


def test_member_cannot_access_admin_check() -> None:
    db = SessionLocal()

    user = User(
        email="member-rbac@example.com",
        full_name="Member RBAC User",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization = Organization(
        name="Member RBAC Organization",
        slug="member-rbac-organization",
    )

    try:
        db.add_all([user, organization])
        db.commit()

        membership = Membership(
            user_id=user.id,
            organization_id=organization.id,
            role="member",
        )

        db.add(membership)
        db.commit()

        token = create_access_token(str(user.id))

        response = client.get(
            f"/organizations/{organization.id}/admin-check",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        assert response.json() == {
            "detail": "Insufficient organization role",
        }

    finally:
        db.rollback()
        db.query(Membership).filter(Membership.user_id == user.id).delete()
        db.query(User).filter(User.email == "member-rbac@example.com").delete()
        db.query(Organization).filter(Organization.slug == "member-rbac-organization").delete()
        db.commit()
        db.close()


def test_user_without_membership_cannot_access_admin_check() -> None:
    db = SessionLocal()

    user = User(
        email="no-membership-rbac@example.com",
        full_name="No Membership RBAC User",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization = Organization(
        name="No Membership RBAC Organization",
        slug="no-membership-rbac-organization",
    )

    try:
        db.add_all([user, organization])
        db.commit()

        token = create_access_token(str(user.id))

        response = client.get(
            f"/organizations/{organization.id}/admin-check",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        assert response.json() == {
            "detail": "Organization access denied",
        }

    finally:
        db.rollback()
        db.query(User).filter(User.email == "no-membership-rbac@example.com").delete()
        db.query(Organization).filter(
            Organization.slug == "no-membership-rbac-organization"
        ).delete()
        db.commit()
        db.close()


def test_admin_can_list_organization_members() -> None:
    db = SessionLocal()

    admin = User(
        email="members-admin@example.com",
        full_name="Members Admin",
        password_hash=hash_password("SecurePassword123!"),
    )
    member_user = User(
        email="members-user@example.com",
        full_name="Members User",
        password_hash=hash_password("SecurePassword123!"),
    )
    organization = Organization(
        name="Members Organization",
        slug="members-organization",
    )

    try:
        db.add_all([admin, member_user, organization])
        db.commit()

        admin_membership = Membership(
            user_id=admin.id,
            organization_id=organization.id,
            role="admin",
        )
        member_membership = Membership(
            user_id=member_user.id,
            organization_id=organization.id,
            role="member",
        )

        db.add_all([admin_membership, member_membership])
        db.commit()

        token = create_access_token(str(admin.id))

        response = client.get(
            f"/organizations/{organization.id}/members",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert len(response.json()) == 2

    finally:
        db.rollback()
        db.query(Membership).filter(Membership.organization_id == organization.id).delete()
        db.query(User).filter(
            User.email.in_(
                [
                    "members-admin@example.com",
                    "members-user@example.com",
                ]
            )
        ).delete(synchronize_session=False)
        db.query(Organization).filter(Organization.slug == "members-organization").delete()
        db.commit()
        db.close()


def test_member_cannot_list_organization_members() -> None:
    db = SessionLocal()

    user = User(
        email="members-denied@example.com",
        full_name="Members Denied",
        password_hash=hash_password("SecurePassword123!"),
    )
    organization = Organization(
        name="Members Denied Organization",
        slug="members-denied-organization",
    )

    try:
        db.add_all([user, organization])
        db.commit()

        membership = Membership(
            user_id=user.id,
            organization_id=organization.id,
            role="member",
        )

        db.add(membership)
        db.commit()

        token = create_access_token(str(user.id))

        response = client.get(
            f"/organizations/{organization.id}/members",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        assert response.json() == {
            "detail": "Insufficient organization role",
        }

    finally:
        db.rollback()
        db.query(Membership).filter(Membership.user_id == user.id).delete()
        db.query(User).filter(User.email == "members-denied@example.com").delete()
        db.query(Organization).filter(Organization.slug == "members-denied-organization").delete()
        db.commit()
        db.close()


def test_owner_can_update_member_role() -> None:
    db = SessionLocal()

    owner = User(
        email="role-owner@example.com",
        full_name="Role Owner",
        password_hash=hash_password("SecurePassword123!"),
    )
    target = User(
        email="role-target@example.com",
        full_name="Role Target",
        password_hash=hash_password("SecurePassword123!"),
    )
    organization = Organization(
        name="Role Management Organization",
        slug="role-management-organization",
    )

    try:
        db.add_all([owner, target, organization])
        db.commit()

        owner_membership = Membership(
            user_id=owner.id,
            organization_id=organization.id,
            role="owner",
        )
        target_membership = Membership(
            user_id=target.id,
            organization_id=organization.id,
            role="member",
        )

        db.add_all([owner_membership, target_membership])
        db.commit()

        token = create_access_token(str(owner.id))

        response = client.patch(
            f"/organizations/{organization.id}/members/{target_membership.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"role": "admin"},
        )

        assert response.status_code == 200
        assert response.json()["role"] == "admin"

    finally:
        db.rollback()
        db.query(Membership).filter(Membership.organization_id == organization.id).delete()
        db.query(User).filter(
            User.email.in_(
                [
                    "role-owner@example.com",
                    "role-target@example.com",
                ]
            )
        ).delete(synchronize_session=False)
        db.query(Organization).filter(Organization.slug == "role-management-organization").delete()
        db.commit()
        db.close()


def test_admin_cannot_update_member_role() -> None:
    db = SessionLocal()

    admin = User(
        email="role-admin@example.com",
        full_name="Role Admin",
        password_hash=hash_password("SecurePassword123!"),
    )
    target = User(
        email="role-admin-target@example.com",
        full_name="Role Admin Target",
        password_hash=hash_password("SecurePassword123!"),
    )
    organization = Organization(
        name="Role Admin Organization",
        slug="role-admin-organization",
    )

    try:
        db.add_all([admin, target, organization])
        db.commit()

        admin_membership = Membership(
            user_id=admin.id,
            organization_id=organization.id,
            role="admin",
        )
        target_membership = Membership(
            user_id=target.id,
            organization_id=organization.id,
            role="member",
        )

        db.add_all([admin_membership, target_membership])
        db.commit()

        token = create_access_token(str(admin.id))

        response = client.patch(
            f"/organizations/{organization.id}/members/{target_membership.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"role": "admin"},
        )

        assert response.status_code == 403
        assert response.json() == {
            "detail": "Insufficient organization role",
        }

    finally:
        db.rollback()
        db.query(Membership).filter(Membership.organization_id == organization.id).delete()
        db.query(User).filter(
            User.email.in_(
                [
                    "role-admin@example.com",
                    "role-admin-target@example.com",
                ]
            )
        ).delete(synchronize_session=False)
        db.query(Organization).filter(Organization.slug == "role-admin-organization").delete()
        db.commit()
        db.close()


def test_create_organization_returns_created_organization() -> None:
    db = SessionLocal()

    user = User(
        email="organization-create-api@example.com",
        full_name="Organization Create API User",
        password_hash=hash_password("SecurePassword123!"),
    )

    try:
        db.add(user)
        db.commit()

        token = create_access_token(str(user.id))

        response = client.post(
            "/organizations",
            headers={
                "Authorization": f"Bearer {token}",
            },
            json={
                "name": "API Created Organization",
                "slug": "api-created-organization",
            },
        )

        assert response.status_code == 201

        body = response.json()

        assert body["name"] == "API Created Organization"
        assert body["slug"] == "api-created-organization"

        membership = (
            db.query(Membership)
            .filter(
                Membership.user_id == user.id,
                Membership.organization_id == body["id"],
            )
            .one()
        )

        assert membership.role == "owner"

    finally:
        db.rollback()

        db.query(Membership).filter(Membership.user_id == user.id).delete()

        db.query(Organization).filter(Organization.slug == "api-created-organization").delete()

        db.query(User).filter(User.email == "organization-create-api@example.com").delete()

        db.commit()
        db.close()


def test_create_organization_duplicate_slug_returns_conflict() -> None:
    db = SessionLocal()

    user = User(
        email="organization-create-duplicate@example.com",
        full_name="Organization Create Duplicate User",
        password_hash=hash_password("SecurePassword123!"),
    )

    existing = Organization(
        name="Existing API Organization",
        slug="api-duplicate-organization",
    )

    try:
        db.add_all([user, existing])
        db.commit()

        token = create_access_token(str(user.id))

        response = client.post(
            "/organizations",
            headers={
                "Authorization": f"Bearer {token}",
            },
            json={
                "name": "Another Organization",
                "slug": "api-duplicate-organization",
            },
        )

        assert response.status_code == 409
        assert response.json() == {
            "detail": "Organization slug already exists",
        }

    finally:
        db.rollback()

        db.query(Membership).filter(Membership.user_id == user.id).delete()

        db.query(Organization).filter(Organization.slug == "api-duplicate-organization").delete()

        db.query(User).filter(User.email == "organization-create-duplicate@example.com").delete()

        db.commit()
        db.close()


def test_create_organization_invalid_slug_returns_validation_error() -> None:
    db = SessionLocal()

    user = User(
        email="organization-invalid-slug@example.com",
        full_name="Organization Invalid Slug User",
        password_hash=hash_password("SecurePassword123!"),
    )

    try:
        db.add(user)
        db.commit()

        token = create_access_token(str(user.id))

        response = client.post(
            "/organizations",
            headers={
                "Authorization": f"Bearer {token}",
            },
            json={
                "name": "Invalid Slug Organization",
                "slug": "Invalid Slug!",
            },
        )

        assert response.status_code == 422

    finally:
        db.rollback()

        db.query(User).filter(User.email == "organization-invalid-slug@example.com").delete()

        db.commit()
        db.close()


def test_create_organization_without_token_returns_unauthorized() -> None:
    response = client.post(
        "/organizations",
        json={
            "name": "Unauthorized Organization",
            "slug": "unauthorized-organization-create",
        },
    )

    assert response.status_code == 401


def test_admin_can_update_organization() -> None:
    db = SessionLocal()

    user = User(
        email="organization-update-admin@example.com",
        full_name="Organization Update Admin",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization = Organization(
        name="Original Organization",
        slug="admin-update-organization",
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

        token = create_access_token(str(user.id))

        response = client.patch(
            f"/organizations/{organization.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Updated by Admin"},
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Updated by Admin"

    finally:
        db.rollback()
        db.query(Membership).filter(Membership.user_id == user.id).delete()
        db.query(Organization).filter(Organization.id == organization.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()
        db.close()


def test_member_cannot_update_organization() -> None:
    db = SessionLocal()

    user = User(
        email="organization-update-member@example.com",
        full_name="Organization Update Member",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization = Organization(
        name="Member Organization",
        slug="member-update-organization",
    )

    try:
        db.add_all([user, organization])
        db.commit()

        membership = Membership(
            user_id=user.id,
            organization_id=organization.id,
            role=OrganizationRole.MEMBER.value,
        )

        db.add(membership)
        db.commit()

        token = create_access_token(str(user.id))

        response = client.patch(
            f"/organizations/{organization.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Should Not Update"},
        )

        assert response.status_code == 403

    finally:
        db.rollback()
        db.query(Membership).filter(Membership.user_id == user.id).delete()
        db.query(Organization).filter(Organization.id == organization.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()
        db.close()


def test_update_organization_duplicate_slug_returns_conflict() -> None:
    db = SessionLocal()

    user = User(
        email="organization-update-conflict@example.com",
        full_name="Organization Update Conflict",
        password_hash=hash_password("SecurePassword123!"),
    )

    first = Organization(
        name="First Organization",
        slug="first-api-update-organization",
    )

    second = Organization(
        name="Second Organization",
        slug="second-api-update-organization",
    )

    try:
        db.add_all([user, first, second])
        db.commit()

        membership = Membership(
            user_id=user.id,
            organization_id=second.id,
            role=OrganizationRole.OWNER.value,
        )

        db.add(membership)
        db.commit()

        token = create_access_token(str(user.id))

        response = client.patch(
            f"/organizations/{second.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"slug": "first-api-update-organization"},
        )

        assert response.status_code == 409
        assert response.json() == {"detail": "Organization slug already exists"}

    finally:
        db.rollback()
        db.query(Membership).filter(Membership.user_id == user.id).delete()
        db.query(Organization).filter(Organization.id.in_([first.id, second.id])).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()
        db.close()


def test_update_organization_invalid_slug_returns_validation_error() -> None:
    db = SessionLocal()

    user = User(
        email="organization-update-invalid@example.com",
        full_name="Organization Update Invalid",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization = Organization(
        name="Invalid Slug Organization",
        slug="invalid-slug-update-organization",
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

        token = create_access_token(str(user.id))

        response = client.patch(
            f"/organizations/{organization.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"slug": "Invalid Slug!"},
        )

        assert response.status_code == 422

    finally:
        db.rollback()
        db.query(Membership).filter(Membership.user_id == user.id).delete()
        db.query(Organization).filter(Organization.id == organization.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()
        db.close()


def test_owner_can_delete_organization() -> None:
    db = SessionLocal()

    user = User(
        email="organization-delete-owner@example.com",
        full_name="Organization Delete Owner",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization = Organization(
        name="Organization Delete Owner",
        slug="organization-delete-owner",
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

        organization_id = organization.id
        token = create_access_token(str(user.id))

        response = client.delete(
            f"/organizations/{organization_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 204

        db.expire_all()

        assert db.get(Organization, organization_id) is None

    finally:
        db.rollback()
        db.query(Membership).filter(Membership.user_id == user.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()
        db.close()


def test_admin_cannot_delete_organization() -> None:
    db = SessionLocal()

    user = User(
        email="organization-delete-admin@example.com",
        full_name="Organization Delete Admin",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization = Organization(
        name="Organization Delete Admin",
        slug="organization-delete-admin",
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

        token = create_access_token(str(user.id))

        response = client.delete(
            f"/organizations/{organization.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        assert response.json() == {"detail": "Insufficient organization role"}

    finally:
        db.rollback()
        db.query(Membership).filter(Membership.user_id == user.id).delete()
        db.query(Organization).filter(Organization.id == organization.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()
        db.close()


def test_member_cannot_delete_organization() -> None:
    db = SessionLocal()

    user = User(
        email="organization-delete-member@example.com",
        full_name="Organization Delete Member",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization = Organization(
        name="Organization Delete Member",
        slug="organization-delete-member",
    )

    try:
        db.add_all([user, organization])
        db.commit()

        membership = Membership(
            user_id=user.id,
            organization_id=organization.id,
            role=OrganizationRole.MEMBER.value,
        )

        db.add(membership)
        db.commit()

        token = create_access_token(str(user.id))

        response = client.delete(
            f"/organizations/{organization.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403

    finally:
        db.rollback()
        db.query(Membership).filter(Membership.user_id == user.id).delete()
        db.query(Organization).filter(Organization.id == organization.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()
        db.close()


def test_owner_can_create_member_invitation() -> None:
    db = SessionLocal()

    user = User(
        email="invitation-api-owner-member@example.com",
        full_name="Invitation API Owner Member",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization = Organization(
        name="Invitation API Owner Member",
        slug="invitation-api-owner-member",
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

        token = create_access_token(str(user.id))

        response = client.post(
            f"/organizations/{organization.id}/invitations",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "email": "new-member-api@example.com",
                "role": "member",
            },
        )

        assert response.status_code == 201

        body = response.json()

        assert body["organization_id"] == str(organization.id)
        assert body["email"] == "new-member-api@example.com"
        assert body["role"] == "member"
        assert body["accepted_at"] is None

    finally:
        db.rollback()
        db.query(Invitation).filter(Invitation.organization_id == organization.id).delete()
        db.query(Membership).filter(Membership.organization_id == organization.id).delete()
        db.query(Organization).filter(Organization.id == organization.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()
        db.close()


def test_owner_can_create_admin_invitation() -> None:
    db = SessionLocal()

    user = User(
        email="invitation-api-owner-admin@example.com",
        full_name="Invitation API Owner Admin",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization = Organization(
        name="Invitation API Owner Admin",
        slug="invitation-api-owner-admin",
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

        token = create_access_token(str(user.id))

        response = client.post(
            f"/organizations/{organization.id}/invitations",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "email": "new-admin-api@example.com",
                "role": "admin",
            },
        )

        assert response.status_code == 201
        assert response.json()["role"] == "admin"

    finally:
        db.rollback()
        db.query(Invitation).filter(Invitation.organization_id == organization.id).delete()
        db.query(Membership).filter(Membership.organization_id == organization.id).delete()
        db.query(Organization).filter(Organization.id == organization.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()
        db.close()


def test_admin_can_create_member_invitation() -> None:
    db = SessionLocal()

    user = User(
        email="invitation-api-admin-member@example.com",
        full_name="Invitation API Admin Member",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization = Organization(
        name="Invitation API Admin Member",
        slug="invitation-api-admin-member",
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

        token = create_access_token(str(user.id))

        response = client.post(
            f"/organizations/{organization.id}/invitations",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "email": "admin-created-member@example.com",
                "role": "member",
            },
        )

        assert response.status_code == 201
        assert response.json()["role"] == "member"

    finally:
        db.rollback()
        db.query(Invitation).filter(Invitation.organization_id == organization.id).delete()
        db.query(Membership).filter(Membership.organization_id == organization.id).delete()
        db.query(Organization).filter(Organization.id == organization.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()
        db.close()


def test_admin_cannot_create_admin_invitation() -> None:
    db = SessionLocal()

    user = User(
        email="invitation-api-admin-admin@example.com",
        full_name="Invitation API Admin Admin",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization = Organization(
        name="Invitation API Admin Restriction",
        slug="invitation-api-admin-restriction",
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

        token = create_access_token(str(user.id))

        response = client.post(
            f"/organizations/{organization.id}/invitations",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "email": "forbidden-admin@example.com",
                "role": "admin",
            },
        )

        assert response.status_code == 403
        assert response.json() == {"detail": "Invitation role not allowed"}

    finally:
        db.rollback()
        db.query(Invitation).filter(Invitation.organization_id == organization.id).delete()
        db.query(Membership).filter(Membership.organization_id == organization.id).delete()
        db.query(Organization).filter(Organization.id == organization.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()
        db.close()


def test_member_cannot_create_invitation() -> None:
    db = SessionLocal()

    user = User(
        email="invitation-api-member@example.com",
        full_name="Invitation API Member",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization = Organization(
        name="Invitation API Member",
        slug="invitation-api-member",
    )

    try:
        db.add_all([user, organization])
        db.commit()

        membership = Membership(
            user_id=user.id,
            organization_id=organization.id,
            role=OrganizationRole.MEMBER.value,
        )

        db.add(membership)
        db.commit()

        token = create_access_token(str(user.id))

        response = client.post(
            f"/organizations/{organization.id}/invitations",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "email": "member-invite@example.com",
                "role": "member",
            },
        )

        assert response.status_code == 403
        assert response.json() == {"detail": "Insufficient organization role"}

    finally:
        db.rollback()
        db.query(Invitation).filter(Invitation.organization_id == organization.id).delete()
        db.query(Membership).filter(Membership.organization_id == organization.id).delete()
        db.query(Organization).filter(Organization.id == organization.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()
        db.close()


def test_duplicate_active_invitation_returns_conflict() -> None:
    db = SessionLocal()

    user = User(
        email="invitation-api-duplicate@example.com",
        full_name="Invitation API Duplicate",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization = Organization(
        name="Invitation API Duplicate",
        slug="invitation-api-duplicate",
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

        token = create_access_token(str(user.id))

        payload = {
            "email": "duplicate-api@example.com",
            "role": "member",
        }

        first_response = client.post(
            f"/organizations/{organization.id}/invitations",
            headers={"Authorization": f"Bearer {token}"},
            json=payload,
        )

        second_response = client.post(
            f"/organizations/{organization.id}/invitations",
            headers={"Authorization": f"Bearer {token}"},
            json=payload,
        )

        assert first_response.status_code == 201
        assert second_response.status_code == 409
        assert second_response.json() == {"detail": "Active invitation already exists"}

    finally:
        db.rollback()
        db.query(Invitation).filter(Invitation.organization_id == organization.id).delete()
        db.query(Membership).filter(Membership.organization_id == organization.id).delete()
        db.query(Organization).filter(Organization.id == organization.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()
        db.close()


def test_existing_member_invitation_returns_conflict() -> None:
    db = SessionLocal()

    owner = User(
        email="invitation-api-existing-owner@example.com",
        full_name="Invitation Existing Owner",
        password_hash=hash_password("SecurePassword123!"),
    )

    existing_member = User(
        email="invitation-api-existing-member@example.com",
        full_name="Invitation Existing Member",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization = Organization(
        name="Invitation Existing Member Organization",
        slug="invitation-api-existing-member",
    )

    try:
        db.add_all([owner, existing_member, organization])
        db.commit()

        owner_membership = Membership(
            user_id=owner.id,
            organization_id=organization.id,
            role=OrganizationRole.OWNER.value,
        )

        member_membership = Membership(
            user_id=existing_member.id,
            organization_id=organization.id,
            role=OrganizationRole.MEMBER.value,
        )

        db.add_all([owner_membership, member_membership])
        db.commit()

        token = create_access_token(str(owner.id))

        response = client.post(
            f"/organizations/{organization.id}/invitations",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "email": existing_member.email,
                "role": "member",
            },
        )

        assert response.status_code == 409
        assert response.json() == {"detail": "User is already an organization member"}

    finally:
        db.rollback()
        db.query(Invitation).filter(Invitation.organization_id == organization.id).delete()
        db.query(Membership).filter(Membership.organization_id == organization.id).delete()
        db.query(Organization).filter(Organization.id == organization.id).delete()
        db.query(User).filter(User.id.in_([owner.id, existing_member.id])).delete()
        db.commit()
        db.close()


def test_owner_role_invitation_is_rejected() -> None:
    db = SessionLocal()

    user = User(
        email="invitation-api-owner-role@example.com",
        full_name="Invitation API Owner Role",
        password_hash=hash_password("SecurePassword123!"),
    )

    organization = Organization(
        name="Invitation API Owner Role",
        slug="invitation-api-owner-role",
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

        token = create_access_token(str(user.id))

        response = client.post(
            f"/organizations/{organization.id}/invitations",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "email": "future-owner-api@example.com",
                "role": "owner",
            },
        )

        assert response.status_code == 403
        assert response.json() == {"detail": "Invitation role not allowed"}

    finally:
        db.rollback()
        db.query(Invitation).filter(Invitation.organization_id == organization.id).delete()
        db.query(Membership).filter(Membership.organization_id == organization.id).delete()
        db.query(Organization).filter(Organization.id == organization.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()
        db.close()


def test_create_invitation_without_token_returns_unauthorized() -> None:
    response = client.post(
        "/organizations/00000000-0000-0000-0000-000000000001/invitations",
        json={
            "email": "unauthorized-invitation@example.com",
            "role": "member",
        },
    )

    assert response.status_code == 401
