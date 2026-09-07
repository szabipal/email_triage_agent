from __future__ import annotations

from typing import Protocol

from email_agent.domain import ProcessedEmail, RetrievalMethod, RetrievedContext
from email_agent.retrieval.embeddings import EmbeddingProvider, EmbeddingRequest
from email_agent.retrieval.vector_store import ChromaIndex


class ContextRepository(Protocol):
    def save_context(self, context: RetrievedContext) -> None: ...


def retrieve_context(
    processed_email: ProcessedEmail,
    provider: EmbeddingProvider,
    index: ChromaIndex,
    *,
    repository: ContextRepository | None = None,
    limit: int = 3,
) -> list[RetrievedContext]:
    query = f"{processed_email.normalized_subject}\n{processed_email.normalized_body}"
    embedding = provider.embed(EmbeddingRequest(text=query))
    contexts = []
    for match in index.query(embedding.vector, limit=limit + 1):
        source_email_id = match.metadata.get("email_id")
        if (
            not isinstance(source_email_id, str)
            or source_email_id == processed_email.email_id
        ):
            continue
        context = RetrievedContext(
            id=f"context:{processed_email.email_id}:{len(contexts) + 1}",
            source_email_ids=[source_email_id],
            query_email_id=processed_email.email_id,
            retrieval_method=RetrievalMethod.RAG,
            summary=match.text,
            relevance_score=1 / (1 + match.distance),
            snippet_text=match.text[:240],
            rank=len(contexts) + 1,
            embedding_model=str(match.metadata.get("embedding_model", "")) or None,
            retrieval_query=query,
        )
        if repository is not None:
            repository.save_context(context)
        contexts.append(context)
        if len(contexts) == limit:
            break
    return contexts
