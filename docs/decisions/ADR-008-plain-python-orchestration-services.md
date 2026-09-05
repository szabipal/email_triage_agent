# ADR-008: Plain Python Orchestration Services

## Status
Accepted

## Context
V1 has a fixed processing workflow and explicitly avoids unnecessary multi-agent architecture. The orchestrator must coordinate components, isolate per-email failures, and avoid duplicating service logic. This supports FR-01 through FR-18, NFR-01, NFR-07, NFR-09, and the AI responsibility specification.

## Decision
Use ordinary typed Python application services for orchestration.

## Alternatives considered
A workflow/state-machine library, Celery or another queue, and an LLM agent framework.

## Consequences
The workflow remains readable, debuggable, and easy to test locally. Conditional retrieval and approval gating can be plain application logic. The trade-off is less built-in workflow visualization or persistence than a dedicated workflow engine.

## Reversal strategy
Keep orchestration steps explicit. If future continuous monitoring or retries require it, wrap the same service calls in a workflow engine or task queue.
