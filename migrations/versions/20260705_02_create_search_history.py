"""Create search history table."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260705_02"
down_revision: str | None = "20260705_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "search_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("query", sa.String(length=500), nullable=False),
        sa.Column("results_count", sa.Integer(), nullable=False),
        sa.Column(
            "searched_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("search_history")
