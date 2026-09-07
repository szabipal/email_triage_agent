from datetime import UTC, datetime

import pytest

from email_agent.calendar import (
    FakeCalendarAdapter,
    decide_proposal,
    execute_approved_proposal,
)
from email_agent.domain import (
    ApprovalDecision,
    CalendarEventProposal,
    CalendarProposalSource,
    CalendarProposalStatus,
    ToolApproval,
)

NOW = datetime(2026, 1, 2, 14, tzinfo=UTC)


class Repository:
    def __init__(self, proposal: CalendarEventProposal) -> None:
        self.proposal = proposal
        self.approval: ToolApproval | None = None

    def get_proposal(self, proposal_id: str) -> CalendarEventProposal | None:
        return self.proposal if proposal_id == self.proposal.id else None

    def get_approval_for_proposal(self, proposal_id: str) -> ToolApproval | None:
        if self.approval is None or self.approval.proposal_id != proposal_id:
            return None
        return self.approval

    def save_proposal(self, proposal: CalendarEventProposal) -> None:
        self.proposal = proposal

    def save_approval(self, approval: ToolApproval) -> None:
        self.approval = approval


def proposal(status: CalendarProposalStatus) -> CalendarEventProposal:
    return CalendarEventProposal(
        id="proposal-1",
        email_id="email-1",
        title="Planning",
        start_at=NOW,
        status=status,
        source=CalendarProposalSource.MEETING,
    )


def test_fake_adapter_counts_unauthorized_writes() -> None:
    calendar = FakeCalendarAdapter()

    with pytest.raises(PermissionError):
        calendar.create_event(proposal(CalendarProposalStatus.PENDING))

    assert calendar.unauthorized_writes == 1


def test_execute_requires_approved_proposal_and_approval_record() -> None:
    repository = Repository(proposal(CalendarProposalStatus.PENDING))

    with pytest.raises(PermissionError, match="not approved"):
        execute_approved_proposal("proposal-1", repository, FakeCalendarAdapter())

    approved, _approval = decide_proposal(
        repository.proposal,
        ApprovalDecision.APPROVED,
        decided_by="user",
        now=NOW,
    )
    repository.proposal = approved
    with pytest.raises(PermissionError, match="no approval"):
        execute_approved_proposal("proposal-1", repository, FakeCalendarAdapter())


def test_execute_is_idempotent_by_proposal_id() -> None:
    repository = Repository(proposal(CalendarProposalStatus.PENDING))
    repository.proposal, repository.approval = decide_proposal(
        repository.proposal,
        ApprovalDecision.APPROVED,
        decided_by="user",
        now=NOW,
    )
    calendar = FakeCalendarAdapter()

    first = execute_approved_proposal("proposal-1", repository, calendar)
    second = execute_approved_proposal("proposal-1", repository, calendar)

    assert first.provider_event_id == second.provider_event_id
    assert len(calendar.events) == 1
    assert repository.approval is not None
    assert repository.approval.external_result_id == first.provider_event_id
