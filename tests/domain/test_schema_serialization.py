from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from email_agent.domain import (
    ApprovalDecision,
    CalendarEventProposal,
    CalendarProposalSource,
    CalendarProposalStatus,
    Email,
    EmailAnalysis,
    EmailAnalysisSignals,
    EmailAnalysisStatus,
    EmailIdentity,
    EmailSource,
    EmailThread,
    PreferenceEffect,
    PreferenceType,
    PriorityBand,
    PriorityFactor,
    PriorityFactorDirection,
    PriorityResult,
    ProcessedEmail,
    ProcessedEmailStatus,
    ProposedAction,
    ProposedActionSource,
    ProposedActionType,
    RetrievalMethod,
    RetrievedContext,
    ToolApproval,
    UserPreference,
)

NOW = datetime(2026, 1, 2, 3, 4, tzinfo=UTC)


def test_domain_schemas_round_trip_through_json() -> None:
    schemas = [
        Email(
            id="email-1",
            provider_message_id="provider-1",
            subject="Planning",
            sender=EmailIdentity(email="ada@example.com"),
            recipients=[EmailIdentity(email="user@example.com")],
            received_at=NOW,
            body_raw="Please review.",
            source=EmailSource.FIXTURE,
        ),
        EmailThread(
            id="thread-1",
            subject_key="planning",
            email_ids=["email-1"],
        ),
        ProcessedEmail(
            id="processed-1",
            email_id="email-1",
            normalized_subject="planning",
            normalized_body="Please review.",
            processed_at=NOW,
            status=ProcessedEmailStatus.PROCESSED,
        ),
        RetrievedContext(
            id="context-1",
            source_email_ids=["email-0"],
            query_email_id="email-1",
            retrieval_method=RetrievalMethod.THREAD,
            summary="Earlier planning email.",
            relevance_score=0.8,
        ),
        EmailAnalysisSignals(
            id="signals-1",
            processed_email_id="processed-1",
            summary="Ada asks for review.",
            category="work",
            action_required=True,
            low_value_type=None,
            confidence=0.9,
        ),
        UserPreference(
            id="preference-1",
            preference_type=PreferenceType.SENDER,
            value="ada@example.com",
            effect=PreferenceEffect.BOOST,
            weight=1.0,
            enabled=True,
        ),
        PriorityResult(
            id="priority-1",
            email_id="email-1",
            score=80,
            band=PriorityBand.HIGH,
            factors=[
                PriorityFactor(
                    name="action required",
                    direction=PriorityFactorDirection.POSITIVE,
                    weight=1.0,
                    source_ids=["signals-1"],
                )
            ],
            calculated_at=NOW,
            ruleset_version="priority-v1",
        ),
        EmailAnalysis(
            id="analysis-1",
            email_id="email-1",
            processed_email_id="processed-1",
            signals_id="signals-1",
            priority_result_id="priority-1",
            status=EmailAnalysisStatus.COMPLETED,
            retrieved_context_ids=["context-1"],
            explanation="Action required from a known sender.",
            completed_at=NOW,
        ),
        ProposedAction(
            id="action-1",
            email_id="email-1",
            description="Review the plan",
            action_type=ProposedActionType.TASK,
            source=ProposedActionSource.ANALYSIS,
        ),
        CalendarEventProposal(
            id="proposal-1",
            email_id="email-1",
            title="Planning review",
            start_at=NOW,
            status=CalendarProposalStatus.PENDING,
            source=CalendarProposalSource.MEETING,
        ),
        ToolApproval(
            id="approval-1",
            proposal_id="proposal-1",
            tool_name="calendar",
            decision=ApprovalDecision.APPROVED,
            decided_at=NOW,
            decided_by="user",
        ),
    ]

    for schema in schemas:
        assert type(schema).model_validate_json(schema.model_dump_json()) == schema


def test_invalid_enum_values_are_rejected() -> None:
    with pytest.raises(ValidationError, match="Input should be"):
        Email.model_validate(
            {
                "id": "email-1",
                "provider_message_id": "provider-1",
                "subject": "Planning",
                "sender": {"email": "ada@example.com"},
                "recipients": [{"email": "user@example.com"}],
                "received_at": NOW,
                "body_raw": "Please review.",
                "source": "unknown",
            }
        )
