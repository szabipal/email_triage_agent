from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from email_agent.domain import (
    ActionItem,
    DeadlineCandidate,
    Email,
    EmailAnalysisSignals,
    EmailIdentity,
    EmailSource,
    EmailThread,
    MeetingCandidate,
    ProcessedEmail,
    ProcessedEmailStatus,
    RetrievalMethod,
    RetrievedContext,
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
