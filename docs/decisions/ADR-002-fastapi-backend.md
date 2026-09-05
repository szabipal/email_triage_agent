# ADR-002: FastAPI Backend

## Status
Accepted

## Context
The API/backend must expose processing, inbox, detail, preference, approval, and optional calendar execution operations. It must support typed request and response models, generated documentation, testability, dependency separation, and async external calls. This supports FR-14, FR-16, FR-17, NFR-03, NFR-07, and NFR-09.

## Decision
Use FastAPI for the backend API.

## Alternatives considered
Flask and a server-rendered-only backend.

## Consequences
Typed Pydantic request/response models and OpenAPI documentation come naturally. Dependency injection supports replaceable providers and test fakes. Async routes can wrap LLM, embedding, and calendar calls where useful. The trade-off is slightly more framework structure than Flask.

## Reversal strategy
Keep application services framework-independent. If needed, replace FastAPI route adapters with Flask or another HTTP framework while preserving service and schema boundaries.
