"""Add document status."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260705_01"
down_revision: str | None = "20260625_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column(
            "status",
            sa.String(length=20),
            server_default="ready",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("documents", "status")
