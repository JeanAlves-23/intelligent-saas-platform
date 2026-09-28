import pytest
from sqlalchemy.exc import IntegrityError

from app.db.session import SessionLocal
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User


def test_create_user() -> None:
    db = SessionLocal()

    user = User(
        email="user@example.com",
        full_name="Test User",
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)

        saved = db.get(User, user.id)

        assert saved is not None
        assert saved.email == "user@example.com"
        assert saved.full_name == "Test User"
        assert saved.is_active is True
        assert saved.created_at is not None
        assert saved.updated_at is not None
    finally:
        db.rollback()

        existing = db.query(User).filter(User.email == "user@example.com").all()

        for item in existing:
            db.delete(item)

        db.commit()
        db.close()


def test_create_membership() -> None:
    db = SessionLocal()

    user = User(
        email="member@example.com",
        full_name="Member User",
    )

    organization = Organization(
        name="Membership Test Organization",
        slug="membership-test-organization",
    )

    try:
        db.add_all([user, organization])
        db.commit()

        membership = Membership(
            user_id=user.id,
            organization_id=organization.id,
            role="admin",
            status="active",
        )

        db.add(membership)
        db.commit()
        db.refresh(membership)

        saved = db.get(Membership, membership.id)

        assert saved is not None
        assert saved.user_id == user.id
        assert saved.organization_id == organization.id
        assert saved.role == "admin"
        assert saved.status == "active"
        assert saved.created_at is not None
        assert saved.updated_at is not None
    finally:
        db.rollback()

        db.query(Membership).filter(Membership.user_id == user.id).delete()

        db.query(User).filter(User.email == "member@example.com").delete()

        db.query(Organization).filter(Organization.slug == "membership-test-organization").delete()

        db.commit()
        db.close()


def test_duplicate_membership_is_rejected() -> None:
    db = SessionLocal()

    user = User(
        email="duplicate-membership@example.com",
        full_name="Duplicate Membership User",
    )

    organization = Organization(
        name="Duplicate Membership Organization",
        slug="duplicate-membership-organization",
    )

    try:
        db.add_all([user, organization])
        db.commit()

        first = Membership(
            user_id=user.id,
            organization_id=organization.id,
        )

        second = Membership(
            user_id=user.id,
            organization_id=organization.id,
        )

        db.add(first)
        db.commit()

        db.add(second)

        with pytest.raises(IntegrityError):
            db.commit()

        db.rollback()
    finally:
        db.rollback()

        db.query(Membership).filter(Membership.user_id == user.id).delete()

        db.query(User).filter(User.email == "duplicate-membership@example.com").delete()

        db.query(Organization).filter(
            Organization.slug == "duplicate-membership-organization"
        ).delete()

        db.commit()
        db.close()
