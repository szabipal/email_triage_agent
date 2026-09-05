# ADR-007: Replaceable Embedding Provider Port

## Status
Accepted

## Context
Embedding generation must support real provider calls, deterministic tests, model/version configuration, dimension validation, and re-indexing when the model changes. This supports FR-09, FR-18, NFR-05, NFR-09, and NFR-13.

## Decision
Use a plain Python embedding provider port with real and deterministic fake adapters.

## Alternatives considered
Calling provider SDKs directly, using only local sentence-transformer models, and letting the vector store own embedding generation.

## Consequences
Tests can run without remote calls, and the system can detect embedding dimension mismatches. Index versioning can be tied to model configuration. The trade-off is maintaining a small abstraction and fake vector behavior.

## Reversal strategy
Implement a new adapter for a different provider or local model, create a new Chroma collection or replacement index, and re-index stored processed emails.
