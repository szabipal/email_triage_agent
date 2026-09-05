from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from email_agent.domain import (
    ActionItem,
    ApprovalDecision,
    CalendarEventProposal,
    CalendarProposalSource,
    CalendarProposalStatus,
    DeadlineCandidate,
    Email,
    EmailAnalysisSignals,
    EmailIdentity,
    EmailSource,
    EmailThread,
    ExecutionStatus,
    MeetingCandidate,
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
    ProposedActionStatus,
    ProposedActionType,
    RetrievalMethod,
    RetrievedContext,
    ToolApproval,
    UserPreference,
)


def test_email_preserves_source_facts_through_json_round_trip() -> None:
    email = Email(
        id="email-1",
        provider_message_id="provider-1",
        subject="Quarterly planning",
        sender=EmailIdentity(email="ada@example.com", display_name="Ada"),
        recipients=[EmailIdentity(email="user@example.com")],
        received_at=datetime(2026, 1, 2, 3, 4, tzinfo=UTC),
        body_raw="<p>Please review the plan.</p>",
        source=EmailSource.FIXTURE,
        thread_id="thread-1",
        headers={"Message-ID": "<provider-1@example.com>"},
        labels=["inbox"],
    )

    restored = Email.model_validate_json(email.model_dump_json())

    assert restored == email
    assert restored.body_raw == "<p>Please review the plan.</p>"


def test_email_requires_recipient() -> None:
    with pytest.raises(ValidationError, match="recipients"):
        Email(
            id="email-1",
            provider_message_id="provider-1",
            subject="No recipient",
            sender=EmailIdentity(email="ada@example.com"),
            recipients=[],
            received_at=datetime(2026, 1, 2, 3, 4, tzinfo=UTC),
            body_raw="Hello",
            source=EmailSource.FIXTURE,
        )


def test_email_thread_validates_seen_range() -> None:
    with pytest.raises(ValidationError, match="last_seen_at"):
        EmailThread(
            id="thread-1",
            subject_key="quarterly-planning",
            email_ids=["email-1"],
            first_seen_at=datetime(2026, 1, 2, tzinfo=UTC),
            last_seen_at=datetime(2026, 1, 1, tzinfo=UTC),
        )


def test_processed_email_serializes_normalized_content_and_language_metadata() -> None:
    processed_email = ProcessedEmail(
        id="processed-1",
        email_id="email-1",
        normalized_subject="quarterly planning",
        normalized_body="Please review the plan.",
        processed_at=datetime(2026, 1, 2, 3, 5, tzinfo=UTC),
        status=ProcessedEmailStatus.PROCESSED,
        body_without_quotes="Please review the plan.",
        signature_removed=True,
        detected_language="en",
        language_confidence=0.97,
        locale_hint="en_US",
    )

    restored = ProcessedEmail.model_validate_json(processed_email.model_dump_json())

    assert restored == processed_email
    assert restored.email_id == "email-1"


def test_processed_email_rejects_invalid_language_confidence() -> None:
    with pytest.raises(ValidationError, match="language_confidence"):
        ProcessedEmail(
            id="processed-1",
            email_id="email-1",
            normalized_subject="subject",
            normalized_body="body",
            processed_at=datetime(2026, 1, 2, 3, 5, tzinfo=UTC),
            status=ProcessedEmailStatus.PROCESSED,
            language_confidence=1.2,
        )


def test_failed_processed_email_serializes_errors_predictably() -> None:
    processed_email = ProcessedEmail(
        id="processed-1",
        email_id="email-1",
        normalized_subject="",
        normalized_body="",
        processed_at=datetime(2026, 1, 2, 3, 5, tzinfo=UTC),
        status=ProcessedEmailStatus.FAILED,
        processing_errors=["missing body"],
    )

    restored = ProcessedEmail.model_validate_json(processed_email.model_dump_json())

    assert restored.status == ProcessedEmailStatus.FAILED
    assert restored.processing_errors == ["missing body"]


def test_retrieved_context_serializes_source_references() -> None:
    context = RetrievedContext(
        id="context-1",
        source_email_ids=["email-previous"],
        query_email_id="email-current",
        retrieval_method=RetrievalMethod.THREAD,
        summary="Earlier thread confirmed the deadline.",
        relevance_score=0.82,
        snippet_text="Please send it by Friday.",
        rank=1,
        embedding_model="fake-embedding",
        retrieval_query="quarterly planning deadline",
    )

    restored = RetrievedContext.model_validate_json(context.model_dump_json())

    assert restored == context
    assert restored.source_email_ids == ["email-previous"]


def test_retrieved_context_rejects_current_email_as_source() -> None:
    with pytest.raises(ValidationError, match="exclude query_email_id"):
        RetrievedContext(
            id="context-1",
            source_email_ids=["email-current"],
            query_email_id="email-current",
            retrieval_method=RetrievalMethod.RAG,
            summary="Bad context",
            relevance_score=1,
        )


def test_analysis_signals_serialize_candidates_and_model_metadata() -> None:
    signals = EmailAnalysisSignals(
        id="signals-1",
        processed_email_id="processed-1",
        summary="Ada asks for review before Friday.",
        category="work",
        action_required=True,
        low_value_type=None,
        confidence=0.9,
        action_items=[
            ActionItem(
                description="Review the quarterly plan",
                owner="user",
                due_at=datetime(2026, 1, 9, tzinfo=UTC),
                confidence=0.88,
            )
        ],
        deadlines=[
            DeadlineCandidate(
                description="Review deadline",
                due_at=datetime(2026, 1, 9, tzinfo=UTC),
                confidence=0.91,
            )
        ],
        meeting_details=[
            MeetingCandidate(
                title="Planning review",
                start_at=datetime(2026, 1, 7, 15, tzinfo=UTC),
                end_at=datetime(2026, 1, 7, 15, 30, tzinfo=UTC),
                attendees=[EmailIdentity(email="ada@example.com")],
            )
        ],
        semantic_flags=["deadline"],
        source_language="en",
        output_language="en",
        model_name="fake-llm",
        prompt_version="analysis-v1",
        schema_version="signals-v1",
    )

    restored = EmailAnalysisSignals.model_validate_json(signals.model_dump_json())

    assert restored == signals
    assert restored.action_items[0].description == "Review the quarterly plan"


def test_analysis_signals_reject_invalid_confidence() -> None:
    with pytest.raises(ValidationError, match="confidence"):
        EmailAnalysisSignals(
            id="signals-1",
            processed_email_id="processed-1",
            summary="Summary",
            category="work",
            action_required=False,
            low_value_type=None,
            confidence=1.1,
        )


def test_user_preference_serializes_structured_value() -> None:
    preference = UserPreference(
        id="preference-1",
        preference_type=PreferenceType.SENDER,
        value={"email": "ada@example.com"},
        effect=PreferenceEffect.BOOST,
        weight=2.0,
        enabled=True,
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    restored = UserPreference.model_validate_json(preference.model_dump_json())

    assert restored == preference
    assert restored.value == {"email": "ada@example.com"}


def test_user_preference_rejects_expiry_before_creation() -> None:
    with pytest.raises(ValidationError, match="expires_at"):
        UserPreference(
            id="preference-1",
            preference_type=PreferenceType.KEYWORD,
            value="invoice",
            effect=PreferenceEffect.BOOST,
            weight=1.0,
            enabled=True,
            created_at=datetime(2026, 1, 2, tzinfo=UTC),
            expires_at=datetime(2026, 1, 1, tzinfo=UTC),
        )


def test_priority_result_serializes_reconstructable_factors() -> None:
    result = PriorityResult(
        id="priority-1",
        email_id="email-1",
        score=82,
        band=PriorityBand.HIGH,
        factors=[
            PriorityFactor(
                name="known sender",
                direction=PriorityFactorDirection.POSITIVE,
                weight=2.0,
                source_ids=["preference-1", "signals-1"],
                details={"matched_sender": "ada@example.com"},
            )
        ],
        calculated_at=datetime(2026, 1, 2, 3, 6, tzinfo=UTC),
        ruleset_version="priority-v1",
        preference_matches=["preference-1"],
        context_influence="Earlier thread confirmed urgency.",
    )

    restored = PriorityResult.model_validate_json(result.model_dump_json())

    assert restored == result
    assert restored.factors[0].source_ids == ["preference-1", "signals-1"]


def test_priority_result_requires_factor() -> None:
    with pytest.raises(ValidationError, match="factors"):
        PriorityResult(
            id="priority-1",
            email_id="email-1",
            score=10,
            band=PriorityBand.LOW,
            factors=[],
            calculated_at=datetime(2026, 1, 2, 3, 6, tzinfo=UTC),
            ruleset_version="priority-v1",
        )


def test_proposed_action_serializes_suggestion_state() -> None:
    action = ProposedAction(
        id="action-1",
        email_id="email-1",
        description="Review the quarterly plan",
        action_type=ProposedActionType.TASK,
        source=ProposedActionSource.ANALYSIS,
        owner="user",
        due_at=datetime(2026, 1, 9, tzinfo=UTC),
        confidence=0.9,
        source_excerpt="Please review before Friday.",
        status=ProposedActionStatus.PROPOSED,
    )

    restored = ProposedAction.model_validate_json(action.model_dump_json())

    assert restored == action


def test_calendar_proposal_only_approved_status_can_execute() -> None:
    proposal = CalendarEventProposal(
        id="proposal-1",
        email_id="email-1",
        title="Planning review",
        start_at=datetime(2026, 1, 7, 15, tzinfo=UTC),
        status=CalendarProposalStatus.APPROVED,
        source=CalendarProposalSource.MEETING,
        end_at=datetime(2026, 1, 7, 15, 30, tzinfo=UTC),
        attendees=[EmailIdentity(email="ada@example.com")],
        confidence=0.88,
    )

    restored = CalendarEventProposal.model_validate_json(proposal.model_dump_json())

    assert restored == proposal
    assert restored.can_execute is True

    rejected = proposal.model_copy(update={"status": CalendarProposalStatus.REJECTED})

    assert rejected.can_execute is False


def test_calendar_proposal_rejects_missing_start_unless_incomplete() -> None:
    with pytest.raises(ValidationError, match="start_at"):
        CalendarEventProposal(
            id="proposal-1",
            email_id="email-1",
            title="Planning review",
            start_at=None,
            status=CalendarProposalStatus.PENDING,
            source=CalendarProposalSource.MEETING,
        )

    incomplete = CalendarEventProposal(
        id="proposal-1",
        email_id="email-1",
        title="Planning review",
        start_at=None,
        status=CalendarProposalStatus.INCOMPLETE,
        source=CalendarProposalSource.MEETING,
        missing_fields=["start_at"],
    )

    assert incomplete.can_execute is False


def test_calendar_proposal_rejects_end_before_start() -> None:
    with pytest.raises(ValidationError, match="end_at"):
        CalendarEventProposal(
            id="proposal-1",
            email_id="email-1",
            title="Planning review",
            start_at=datetime(2026, 1, 7, 15, tzinfo=UTC),
            end_at=datetime(2026, 1, 7, 14, 30, tzinfo=UTC),
            status=CalendarProposalStatus.PENDING,
            source=CalendarProposalSource.MEETING,
        )


def test_tool_approval_serializes_decision_and_execution_state() -> None:
    approval = ToolApproval(
        id="approval-1",
        proposal_id="proposal-1",
        tool_name="calendar",
        decision=ApprovalDecision.APPROVED,
        decided_at=datetime(2026, 1, 7, 14, tzinfo=UTC),
        decided_by="user",
        approval_notes="Looks right.",
        execution_status=ExecutionStatus.NOT_STARTED,
    )

    restored = ToolApproval.model_validate_json(approval.model_dump_json())

    assert restored == approval
