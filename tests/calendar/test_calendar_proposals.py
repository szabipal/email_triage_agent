from datetime import UTC, datetime

from email_agent.calendar import create_calendar_proposals
from email_agent.domain import (
    CalendarProposalStatus,
    DeadlineCandidate,
    EmailAnalysisSignals,
    EmailIdentity,
    MeetingCandidate,
)


def signals(**updates) -> EmailAnalysisSignals:
    values = {
        "id": "signals-1",
        "processed_email_id": "processed-1",
        "summary": "Meeting request.",
        "category": "meeting",
        "action_required": True,
        "low_value_type": None,
        "confidence": 0.9,
    }
    values.update(updates)
    return EmailAnalysisSignals.model_validate(values)


def test_create_calendar_proposals_marks_complete_and_incomplete_items() -> None:
    start = datetime(2026, 1, 2, 14, tzinfo=UTC)
    proposals = create_calendar_proposals(
        "email-1",
        signals(
            meeting_details=[
                MeetingCandidate(
                    title="Planning",
                    start_at=start,
                    end_at=datetime(2026, 1, 2, 15, tzinfo=UTC),
                    attendees=[EmailIdentity(email="ada@example.com")],
                    location="Room 1",
                )
            ],
            deadlines=[
                DeadlineCandidate(
                    description="Send notes",
                    uncertainty="soon is ambiguous",
                )
            ],
        ),
    )

    assert proposals[0].status == CalendarProposalStatus.PENDING
    assert proposals[0].location == "Room 1"
    assert proposals[1].status == CalendarProposalStatus.INCOMPLETE
    assert proposals[1].missing_fields == ["start_at"]
