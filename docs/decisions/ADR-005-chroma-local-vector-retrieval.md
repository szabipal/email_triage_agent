# ADR-005: Chroma Local Vector Retrieval

## Status
Accepted

## Context
V1 must demonstrate meaningful RAG with local reproducibility, metadata filtering, test isolation, and auditability of retrieved document IDs and relevance scores. This supports FR-09, NFR-02, NFR-05, NFR-09, and the MVP RAG demonstration requirement.

## Decision
Use Chroma as the local vector store for V1 retrieval.

## Alternatives considered
FAISS, pgvector, SQLite-only lexical retrieval, and a managed vector database.

## Consequences
Chroma provides local persistence and metadata filtering without a separate server or PostgreSQL dependency. Application persistence remains the audit source of truth for retrieval outputs. The trade-off is adding a second local persistence directory beside SQLite.

## Reversal strategy
Keep retrieval behind a vector-store port. Replace Chroma with FAISS, pgvector, or another store by rewriting the adapter and preserving retrieved context records in application storage.
