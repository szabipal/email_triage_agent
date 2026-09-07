from __future__ import annotations

from email_agent.domain import ProcessedEmail
from email_agent.retrieval.embeddings import EmbeddingProvider, EmbeddingRequest
from email_agent.retrieval.vector_store import ChromaIndex, VectorDocument


def index_processed_email(
    processed_email: ProcessedEmail,
    provider: EmbeddingProvider,
    index: ChromaIndex,
) -> str:
    text = f"{processed_email.normalized_subject}\n{processed_email.normalized_body}"
    embedding = provider.embed(EmbeddingRequest(text=text))
    document_id = f"processed:{processed_email.id}"
    index.add(
        VectorDocument(
            id=document_id,
            text=text,
            embedding=embedding.vector,
            metadata={
                "email_id": processed_email.email_id,
                "processed_email_id": processed_email.id,
                "embedding_model": embedding.model_name,
                "embedding_version": embedding.model_version,
                "embedding_dimension": embedding.dimension,
            },
        )
    )
    return document_id
