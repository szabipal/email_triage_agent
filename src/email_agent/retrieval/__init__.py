from email_agent.retrieval.embeddings import (
    Embedding,
    EmbeddingProvider,
    EmbeddingRequest,
    FakeEmbeddingProvider,
)
from email_agent.retrieval.indexing import index_processed_email
from email_agent.retrieval.vector_store import ChromaIndex, VectorDocument, VectorMatch

__all__ = [
    "ChromaIndex",
    "Embedding",
    "EmbeddingProvider",
    "EmbeddingRequest",
    "FakeEmbeddingProvider",
    "VectorDocument",
    "VectorMatch",
    "index_processed_email",
]
