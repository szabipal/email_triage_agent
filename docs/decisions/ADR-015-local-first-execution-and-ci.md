# ADR-015: Local-First Execution And CI

## Status
Accepted

## Context
The project must be runnable locally by another developer and automated testing must not require deployment. V1 should remain portfolio-scale. This supports NFR-05, NFR-12, NFR-11, and the MVP setup requirement.

## Decision
Use local startup commands with `uv`, two local processes for FastAPI and Vite during development, embedded/local SQLite and Chroma storage, GitHub Actions for CI, and optional Docker Compose for demo packaging.

## Alternatives considered
Cloud-first deployment, Docker-only development, Kubernetes, managed database/vector services, and no CI.

## Consequences
Local development remains simple and cheap. CI can run linting, typing, tests, and evaluation with fake providers. Optional containerization can improve demo reproducibility without blocking development. The trade-off is that public deployment details remain deferred.

## Reversal strategy
Add a deployment-specific configuration, managed database, or hosted frontend/backend later while preserving local mode and provider ports.
