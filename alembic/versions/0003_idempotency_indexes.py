"""add idempotency indexes

Revision ID: 0003_idempotency_indexes
Revises: 0002_email_analyses
Create Date: 2026-09-05
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0003_idempotency_indexes"
down_revision: str | None = "0002_email_analyses"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "uq_emails_provider_message_id",
        "emails",
        ["provider_message_id"],
        unique=True,
    )
    op.create_index(
        "uq_calendar_event_proposals_provider_event_id",
        "calendar_event_proposals",
        ["provider_event_id"],
        unique=True,
    )
    op.create_index(
        "uq_tool_approvals_proposal_tool",
        "tool_approvals",
        ["proposal_id", "tool_name"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_tool_approvals_proposal_tool", table_name="tool_approvals")
    op.drop_index(
        "uq_calendar_event_proposals_provider_event_id",
        table_name="calendar_event_proposals",
    )
    op.drop_index("uq_emails_provider_message_id", table_name="emails")
