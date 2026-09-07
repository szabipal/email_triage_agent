from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from email_agent.domain import (
    ApprovalDecision,
    CalendarEventProposal,
    CalendarProposalSource,
    CalendarProposalStatus,
    EmailAnalysisSignals,
    ExecutionStatus,
    ToolApproval,
)


@dataclass(frozen=True)
class CalendarEventResult:
    provider_event_id: str


class CalendarPort(Protocol):
    def create_event(self, proposal: CalendarEventProposal) -> CalendarEventResult: ...


class FakeCalendarAdapter:
    def __init__(self, fail_proposal_ids: set[str] | None = None) -> None:
        self.fail_proposal_ids = fail_proposal_ids or set()
        self.events: dict[str, CalendarEventResult] = {}
        self.unauthorized_writes = 0

    def create_event(self, proposal: CalendarEventProposal) -> CalendarEventResult:
        if not proposal.can_execute:
            self.unauthorized_writes += 1
            raise PermissionError("proposal is not approved")
        if proposal.id in self.fail_proposal_ids:
            raise RuntimeError("calendar adapter failure")
        if proposal.id not in self.events:
            self.events[proposal.id] = CalendarEventResult(
                provider_event_id=f"fake-calendar-{proposal.id}"
            )
        return self.events[proposal.id]


class GoogleCalendarAdapter:
    def __init__(self, credentials_path: Path) -> None:
        self.credentials_path = credentials_path

    def create_event(self, proposal: CalendarEventProposal) -> CalendarEventResult:
        raise NotImplementedError(
            "Google Calendar execution needs an OAuth client wired to "
            f"{self.credentials_path}"
        )


class CalendarExecutionRepository(Protocol):
    def get_proposal(self, proposal_id: str) -> CalendarEventProposal | None: ...

    def get_approval_for_proposal(self, proposal_id: str) -> ToolApproval | None: ...

    def save_proposal(self, proposal: CalendarEventProposal) -> None: ...

    def save_approval(self, approval: ToolApproval) -> None: ...


def create_calendar_proposals(
    email_id: str,
    signals: EmailAnalysisSignals,
) -> list[CalendarEventProposal]:
    proposals: list[CalendarEventProposal] = []
    for index, meeting in enumerate(signals.meeting_details, start=1):
        proposals.append(
            CalendarEventProposal(
                id=f"proposal-{email_id}-meeting-{index}",
                email_id=email_id,
                title=meeting.title or "Meeting",
                start_at=meeting.start_at,
                end_at=meeting.end_at,
                attendees=meeting.attendees,
                location=meeting.location,
                status=(
                    CalendarProposalStatus.PENDING
                    if meeting.start_at
                    else CalendarProposalStatus.INCOMPLETE
                ),
                source=CalendarProposalSource.MEETING,
                confidence=meeting.confidence,
                missing_fields=[] if meeting.start_at else ["start_at"],
                time_ambiguity=meeting.uncertainty,
            )
        )
    for index, deadline in enumerate(signals.deadlines, start=1):
        proposals.append(
            CalendarEventProposal(
                id=f"proposal-{email_id}-deadline-{index}",
                email_id=email_id,
                title=deadline.description,
                start_at=deadline.due_at,
                status=(
                    CalendarProposalStatus.PENDING
                    if deadline.due_at
                    else CalendarProposalStatus.INCOMPLETE
                ),
                source=CalendarProposalSource.DEADLINE,
                confidence=deadline.confidence,
                missing_fields=[] if deadline.due_at else ["start_at"],
                time_ambiguity=deadline.uncertainty,
            )
        )
    return proposals


def decide_proposal(
    proposal: CalendarEventProposal,
    decision: ApprovalDecision,
    *,
    decided_by: str,
    approval_notes: str | None = None,
    now: datetime | None = None,
) -> tuple[CalendarEventProposal, ToolApproval]:
    if proposal.status not in {
        CalendarProposalStatus.PENDING,
        CalendarProposalStatus.INCOMPLETE,
    }:
        raise ValueError(f"cannot decide proposal in {proposal.status} state")
    if decision == ApprovalDecision.APPROVED and proposal.status != (
        CalendarProposalStatus.PENDING
    ):
        raise ValueError("only complete pending proposals can be approved")

    status = (
        CalendarProposalStatus.APPROVED
        if decision == ApprovalDecision.APPROVED
        else CalendarProposalStatus.REJECTED
    )
    approval = ToolApproval(
        id=f"approval-{proposal.id}",
        proposal_id=proposal.id,
        tool_name="calendar",
        decision=decision,
        decided_at=now or datetime.now(UTC),
        decided_by=decided_by,
        approval_notes=approval_notes,
        execution_status=(
            ExecutionStatus.NOT_STARTED
            if decision == ApprovalDecision.APPROVED
            else None
        ),
    )
    return proposal.model_copy(update={"status": status}), approval


def execute_approved_proposal(
    proposal_id: str,
    repository: CalendarExecutionRepository,
    calendar: CalendarPort,
) -> CalendarEventProposal:
    proposal = repository.get_proposal(proposal_id)
    if proposal is None:
        raise LookupError("proposal not found")
    if proposal.status == CalendarProposalStatus.EXECUTED:
        return proposal
    if not proposal.can_execute:
        raise PermissionError("proposal is not approved")

    approval = repository.get_approval_for_proposal(proposal_id)
    if approval is None or approval.execution_status is None:
        raise PermissionError("approved proposal has no approval record")
    if approval.execution_status == ExecutionStatus.EXECUTED:
        return proposal.model_copy(update={"status": CalendarProposalStatus.EXECUTED})

    repository.save_proposal(
        proposal.model_copy(update={"status": CalendarProposalStatus.EXECUTING})
    )
    repository.save_approval(
        approval.model_copy(update={"execution_status": ExecutionStatus.EXECUTING})
    )

    try:
        result = calendar.create_event(proposal)
    except Exception as error:
        repository.save_proposal(
            proposal.model_copy(update={"status": CalendarProposalStatus.FAILED})
        )
        repository.save_approval(
            approval.model_copy(
                update={
                    "execution_status": ExecutionStatus.FAILED,
                    "execution_error": str(error),
                }
            )
        )
        raise

    executed = proposal.model_copy(
        update={
            "status": CalendarProposalStatus.EXECUTED,
            "provider_event_id": result.provider_event_id,
        }
    )
    repository.save_proposal(executed)
    repository.save_approval(
        approval.model_copy(
            update={
                "execution_status": ExecutionStatus.EXECUTED,
                "external_result_id": result.provider_event_id,
            }
        )
    )
    return executed
