# ADR-012: Local Structured Logging

## Status
Accepted

## Context
Processing must expose stage status, failures, model metadata, retrieval results, latency, and token/cost metadata when available. The project should not introduce a production observability platform. This supports NFR-01, NFR-02, NFR-10, FR-13, and the MVP auditability requirements.

## Decision
Use Python standard logging with JSON-compatible structured records and persisted processing status records.

## Alternatives considered
Plain print statements, structlog, OpenTelemetry, Sentry, and hosted log platforms.

## Consequences
Local debugging and audit trails are supported without managed services. Logs can include processing IDs, email IDs, stage names, prompt versions, model names, retrieval scores, and errors. The trade-off is less advanced tracing than a full observability stack.

## Reversal strategy
Adopt structlog or OpenTelemetry later by adapting logging setup and preserving existing event field names.
