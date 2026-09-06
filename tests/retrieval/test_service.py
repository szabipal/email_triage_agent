from datetime import UTC, datetime

from email_agent.domain import ProcessedEmail, ProcessedEmailStatus, RetrievedContext
from email_agent.retrieval import (
    ChromaIndex,
    FakeEmbeddingProvider,
    index_processed_email,
    retrieve_context,
)


class ContextRepo:
    def __init__(self) -> None:
        self.saved: list[RetrievedContext] = []

    def save_context(self, context: RetrievedContext) -> None:
        self.saved.append(context)


def processed(email_id: str, subject: str, body: str) -> ProcessedEmail:
    return ProcessedEmail(
        id=f"processed-{email_id}",
        email_id=email_id,
        normalized_subject=subject,
        normalized_body=body,
        processed_at=datetime(2026, 1, 1, tzinfo=UTC),
        status=ProcessedEmailStatus.PROCESSED,
    )


def test_retrieve_context_excludes_current_email_and_persists_scores(tmp_path) -> None:
    index = ChromaIndex(tmp_path)
    provider = FakeEmbeddingProvider()
    source = processed(
        "email-dev-007",
        "Q1 invoice approval background",
        "legal approved the vendor exception yesterday",
    )
    current = processed(
        "email-dev-008",
        "Re: Q1 invoice approval background",
        "approve INV-4421 today exception discussed",
    )
    index_processed_email(source, provider, index)
    index_processed_email(current, provider, index)
    repo = ContextRepo()

    contexts = retrieve_context(current, provider, index, repository=repo, limit=1)

    assert contexts[0].source_email_ids == ["email-dev-007"]
    assert contexts[0].query_email_id == "email-dev-008"
    assert contexts[0].relevance_score > 0
    assert repo.saved == contexts
