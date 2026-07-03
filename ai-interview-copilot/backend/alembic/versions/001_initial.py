"""Initial schema"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sessions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("role", sa.Text(), nullable=True),
        sa.Column("resume", sa.Text(), nullable=True),
        sa.Column("experience_level", sa.String(), server_default="mid"),
        sa.Column("status", sa.String(), server_default="in_progress"),
        sa.Column("questions", JSONB, nullable=True),
        sa.Column("answers", JSONB, nullable=True),
        sa.Column("feedback", JSONB, nullable=True),
        sa.Column("average_score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("sessions")
