"""ensure membership organization cascade delete

Revision ID: 2ae5327a70a1
Revises: 5b66ee808493
Create Date: 2026-10-25 07:54:01.930294

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2ae5327a70a1"
down_revision: str | Sequence[str] | None = "5b66ee808493"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        "memberships_organization_id_fkey",
        "memberships",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "memberships_organization_id_fkey",
        "memberships",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "memberships_organization_id_fkey",
        "memberships",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "memberships_organization_id_fkey",
        "memberships",
        "organizations",
        ["organization_id"],
        ["id"],
    )
