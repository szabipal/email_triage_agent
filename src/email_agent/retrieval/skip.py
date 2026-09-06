from __future__ import annotations

from typing import Protocol

from email_agent.domain import EmailAnalysisSignals, ProcessedEmail, RetrievedContext, RetrievalMethod


class ContextRepository(Protocol):
    def save_context(self, context: RetrievedContext) -> None: ...


def retrieval_skip_reason(
    signals: EmailAnalysisSignals,
    *,
    has_history: bool,
) -> str | None:
    if signals.low_value_type is not None:
        return "low_value"
    if not has_history:
        return "no_history"
    return None


def record_retrieval_skip(
    processed_email: ProcessedEmail,
    reason: str,
    repository: ContextRepository | None = None,
) -> RetrievedContext:
    context = RetrievedContext(
        id=f"context:{processed_email.email_id}:skip",
        query_email_id=processed_email.email_id,
        retrieval_method=RetrievalMethod.RAG,
        summary="Retrieval skipped.",
        relevance_score=0,
        skip_reason=reason,
    )
    if repository is not None:
        repository.save_context(context)
    return context
