import pytest
from sqlalchemy.exc import IntegrityError

from app.db.session import SessionLocal
from app.models.organization import Organization


def test_create_organization() -> None:
    db = SessionLocal()

    organization = Organization(
        name="Acme Corporation",
        slug="acme-corporation",
    )

    try:
        db.add(organization)
        db.commit()
        db.refresh(organization)

        saved = db.get(Organization, organization.id)

        assert saved is not None
        assert saved.name == "Acme Corporation"
        assert saved.slug == "acme-corporation"
        assert saved.created_at is not None
        assert saved.updated_at is not None
    finally:
        db.delete(organization)
        db.commit()
        db.close()


def test_duplicate_organization_slug_is_rejected() -> None:
    db = SessionLocal()

    first = Organization(
        name="First Organization",
        slug="duplicate-slug",
    )

    second = Organization(
        name="Second Organization",
        slug="duplicate-slug",
    )

    try:
        db.add(first)
        db.commit()

        db.add(second)

        with pytest.raises(IntegrityError):
            db.commit()

        db.rollback()
    finally:
        existing = db.query(Organization).filter(Organization.slug == "duplicate-slug").all()

        for organization in existing:
            db.delete(organization)

        db.commit()
        db.close()
