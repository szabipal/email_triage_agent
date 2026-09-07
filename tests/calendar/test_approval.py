from datetime import UTC, datetime

import pytest

from email_agent.calendar import decide_proposal
from email_agent.domain import (
    ApprovalDecision,
    CalendarEventProposal,
    CalendarProposalSource,
    CalendarProposalStatus,
    ExecutionStatus,
)

NOW = datetime(2026, 1, 2, 14, tzinfo=UTC)


def proposal(status: CalendarProposalStatus) -> CalendarEventProposal:
    return CalendarEventProposal(
        id="proposal-1",
        email_id="email-1",
        title="Planning",
        start_at=NOW if status != CalendarProposalStatus.INCOMPLETE else None,
        status=status,
        source=CalendarProposalSource.MEETING,
    )


def test_approval_records_not_started_execution_state() -> None:
    updated, approval = decide_proposal(
        proposal(CalendarProposalStatus.PENDING),
        ApprovalDecision.APPROVED,
        decided_by="user",
        now=NOW,
    )

    assert updated.status == CalendarProposalStatus.APPROVED
    assert approval.execution_status == ExecutionStatus.NOT_STARTED


def test_incomplete_proposal_cannot_be_approved() -> None:
    with pytest.raises(ValueError, match="complete pending"):
        decide_proposal(
            proposal(CalendarProposalStatus.INCOMPLETE),
            ApprovalDecision.APPROVED,
            decided_by="user",
        )


def test_terminal_proposal_cannot_be_decided_again() -> None:
    with pytest.raises(ValueError, match="cannot decide"):
        decide_proposal(
            proposal(CalendarProposalStatus.REJECTED),
            ApprovalDecision.APPROVED,
            decided_by="user",
        )
