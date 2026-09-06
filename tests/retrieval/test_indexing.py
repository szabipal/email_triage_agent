from datetime import UTC, datetime

from email_agent.domain import ProcessedEmail, ProcessedEmailStatus
from email_agent.retrieval import (
    ChromaIndex,
    EmbeddingRequest,
    FakeEmbeddingProvider,
    index_processed_email,
)


def test_index_processed_email_stores_text_and_embedding_metadata(tmp_path) -> None:
    index = ChromaIndex(tmp_path)
    provider = FakeEmbeddingProvider(dimension=8)
    processed = ProcessedEmail(
        id="processed-1",
        email_id="email-1",
        normalized_subject="Invoice approval",
        normalized_body="Legal approved the vendor exception.",
        processed_at=datetime(2026, 1, 1, tzinfo=UTC),
        status=ProcessedEmailStatus.PROCESSED,
    )

    document_id = index_processed_email(processed, provider, index)
    query = provider.embed(EmbeddingRequest(text="Invoice approval vendor exception"))
    matches = index.query(query.vector, limit=1)

    assert document_id == "processed:processed-1"
    assert matches[0].metadata["email_id"] == "email-1"
    assert matches[0].metadata["embedding_model"] == "fake-embedding"
