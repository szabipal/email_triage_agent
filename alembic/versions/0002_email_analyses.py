"""create email analyses table

Revision ID: 0002_email_analyses
Revises: 0001_core_tables
Create Date: 2026-09-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_email_analyses"
down_revision: str | None = "0001_core_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "email_analyses",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("email_id", sa.String(), nullable=False),
        sa.Column("processed_email_id", sa.String(), nullable=False),
        sa.Column("signals_id", sa.String(), nullable=False),
        sa.Column("priority_result_id", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["email_id"], ["emails.id"]),
        sa.ForeignKeyConstraint(["processed_email_id"], ["processed_emails.id"]),
        sa.ForeignKeyConstraint(["signals_id"], ["analysis_signals.id"]),
        sa.ForeignKeyConstraint(["priority_result_id"], ["priority_results.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("email_analyses")
