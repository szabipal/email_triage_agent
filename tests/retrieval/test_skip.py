from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from email_agent.domain import (
    EmailAnalysisSignals,
    LowValueType,
    ProcessedEmail,
    ProcessedEmailStatus,
    RetrievedContext,
    RetrievalMethod,
)
from email_agent.retrieval import record_retrieval_skip, retrieval_skip_reason


def signals(low_value_type=None) -> EmailAnalysisSignals:
    return EmailAnalysisSignals(
        id="signals-1",
        processed_email_id="processed-1",
        summary="Newsletter.",
        category="newsletter",
        action_required=False,
        low_value_type=low_value_type,
        confidence=0.9,
    )


def test_retrieval_skip_reason_handles_low_value_and_no_history() -> None:
    assert retrieval_skip_reason(
        signals(LowValueType.NEWSLETTER), has_history=True
    ) == "low_value"
    assert retrieval_skip_reason(signals(), has_history=False) == "no_history"
    assert retrieval_skip_reason(signals(), has_history=True) is None


def test_record_retrieval_skip_can_persist_empty_source_context() -> None:
    processed = ProcessedEmail(
        id="processed-1",
        email_id="email-1",
        normalized_subject="Newsletter",
        normalized_body="Tips.",
        processed_at=datetime(2026, 1, 1, tzinfo=UTC),
        status=ProcessedEmailStatus.PROCESSED,
    )

    context = record_retrieval_skip(processed, "low_value")

    assert context.source_email_ids == []
    assert context.skip_reason == "low_value"


def test_retrieved_context_requires_sources_unless_skipped() -> None:
    with pytest.raises(ValidationError, match="unless retrieval is skipped"):
        RetrievedContext(
            id="context-1",
            query_email_id="email-1",
            retrieval_method=RetrievalMethod.RAG,
            summary="No source.",
            relevance_score=0,
        )
