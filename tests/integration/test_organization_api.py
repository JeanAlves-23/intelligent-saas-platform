from fastapi.testclient import TestClient

from app.core.security import create_access_token, hash_password
from app.db.session import SessionLocal
from app.main import app
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
