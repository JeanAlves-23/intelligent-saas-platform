import pytest

from app.db.session import SessionLocal
from app.models.organization import Organization
from app.services.organization import (
    OrganizationSlugAlreadyExistsError,
    update_organization,
)


def test_update_organization_name() -> None:
    db = SessionLocal()

    organization = Organization(
        name="Original Organization",
        slug="update-name-organization",
    )

    try:
        db.add(organization)
        db.commit()

        updated = update_organization(
            db,
            organization.id,
            name="Updated Organization",
        )

        assert updated.name == "Updated Organization"
        assert updated.slug == "update-name-organization"

    finally:
        db.rollback()
        db.query(Organization).filter(Organization.slug == "update-name-organization").delete()
        db.commit()
        db.close()


def test_update_organization_slug() -> None:
    db = SessionLocal()

    organization = Organization(
        name="Slug Organization",
        slug="old-organization-slug",
    )

    try:
        db.add(organization)
        db.commit()

        updated = update_organization(
            db,
            organization.id,
            slug="new-organization-slug",
        )

        assert updated.slug == "new-organization-slug"

    finally:
        db.rollback()
        db.query(Organization).filter(Organization.id == organization.id).delete()
        db.commit()
        db.close()


def test_update_organization_duplicate_slug_is_rejected() -> None:
    db = SessionLocal()

    first = Organization(
        name="First Organization",
        slug="first-update-organization",
    )

    second = Organization(
        name="Second Organization",
        slug="second-update-organization",
    )

    try:
        db.add_all([first, second])
        db.commit()

        with pytest.raises(OrganizationSlugAlreadyExistsError):
            update_organization(
                db,
                second.id,
                slug="first-update-organization",
            )

    finally:
        db.rollback()
        db.query(Organization).filter(
            Organization.slug.in_(
                [
                    "first-update-organization",
                    "second-update-organization",
                ]
            )
        ).delete()
        db.commit()
        db.close()
