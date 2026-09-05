# V1 Technology Decisions

This document selects the V1 technology stack for the AI-powered email triage system. It treats `docs/spec/` and `docs/planning/10_spec_consistency_review.md` as authoritative.

## Decision Principles

The selected stack favors local reproducibility, clear boundaries, deterministic tests, auditability, and Python-native AI development. It avoids microservices, Kubernetes, distributed queues, production authentication, knowledge graphs, multi-agent frameworks, and managed infrastructure that is not required by V1.

## 1. Python And Dependency Management

Decision: Python 3.12, `uv`, `pyproject.toml`, `src/` layout, Ruff, Pyright, and pytest.

- Supported Python version: Python 3.12.
- Dependency and virtual environment tool: `uv`.
- Package/project configuration: `pyproject.toml`.
- Source layout: `src/email_agent/`.
- Linting and formatting: Ruff for linting, import sorting, and formatting.
- Static type checking: Pyright.
- Test runner: pytest with pytest-asyncio where async tests are needed.

Why: Python 3.12 is modern and stable, `uv` gives fast reproducible local setup, and `pyproject.toml` keeps packaging, linting, typing, and test configuration centralized.

## 2. Backend And API

Decision: FastAPI.

FastAPI fits the requirements for typed request/response models, generated OpenAPI documentation, dependency injection, testability, and async external calls. Flask is smaller but would require more manual conventions for schemas, validation, OpenAPI, and async behavior.

## 3. Domain Validation

Decision: Pydantic v2 schemas for domain validation and API contracts, with separate SQLAlchemy ORM models for persistence.

Domain entities, API contracts, and database records must not collapse into one shared class. Use separate model layers:

- Domain schemas: business-facing Pydantic models.
- API schemas: request/response Pydantic models.
- Persistence models: SQLAlchemy ORM models.
- Mapping functions: explicit conversion between layers.

## 4. Persistence

Decision: SQLite for V1, SQLAlchemy 2.x ORM/Core, Alembic migrations, and repository classes as the persistence boundary.

SQLite supports local reproducibility and portfolio-scale data volume. SQLAlchemy and Alembic keep a future PostgreSQL move realistic.

Storage coverage:

- Source email metadata and content: relational tables.
- Processed email content: relational tables.
- Analysis signals: relational records with JSON columns for structured nested fields.
- Retrieved-context references: relational table plus vector-store document IDs and scores.
- Priority results and factors: relational records with JSON factor list.
- User preferences: relational table with typed preference fields or JSON value.
- Action proposals: relational table.
- Approvals: relational table.
- Execution results: ToolApproval execution fields plus CalendarEventProposal provider fields.

## 5. Embeddings And Vector Retrieval

Decision: Chroma for local vector retrieval.

Chroma gives persistent local collections, metadata filtering, simple setup, and test isolation without requiring PostgreSQL or a separate service. FAISS is fast but lower-level and needs more metadata/persistence plumbing. pgvector is attractive later but would require PostgreSQL, which is unnecessary for local V1.

Retrieved document IDs, source email IDs, ranks, relevance scores, embedding model, and retrieval query metadata must be persisted in application storage for auditability.

## 6. LLM Provider Abstraction

Decision: A plain Python provider port with adapters, not an agent framework.

Use a typed `LLMClient`-style interface that supports:

- Structured output using provider-native JSON/schema features where available.
- Pydantic validation after every response.
- Bounded retries for transient failures and malformed output.
- Timeout handling.
- Provider/model configuration through typed settings.
- Deterministic fake implementation for tests.
- Prompt version tracking in persisted analysis signals.

Domain logic must depend on the port, not on one provider SDK.

## 7. Embedding Provider Abstraction

Decision: A plain Python embedding provider port with real and deterministic fake adapters.

The real adapter can call a configured embedding provider. The fake adapter returns deterministic vectors for tests. Store model name, model version, embedding dimension, and index collection version. If model or dimension changes, create a new index collection or force re-indexing.

## 8. Orchestration

Decision: Ordinary typed Python application services.

V1 orchestration should not use a workflow library or agent framework. The orchestrator owns stage ordering, conditional retrieval, error isolation, retries at service boundaries, persistence of stage status, and handoff between services. Individual services own their domain behavior: ingestion, preprocessing, retrieval, LLM analysis, priority, proposal creation, approval, calendar execution, and persistence.

## 9. Calendar Integration

Decision: Calendar port with fake adapter for tests and Google Calendar as the intended real demo provider.

The real provider is optional for MVP because calendar execution is Should. Proposal and approval gating are Must. Approval enforcement lives in the backend/application service before the calendar adapter is called. Calendar execution must be idempotent per proposal ID. Automated tests use the fake adapter and verify unauthorized writes remain zero.

## 10. User Interface

Decision: Small React/TypeScript frontend using Vite.

Streamlit is fastest but weakens the API-boundary demonstration. Server-rendered UI is viable but gives less frontend portfolio value. A small React app demonstrates a clean backend/API boundary while keeping V1 screens limited to the spec: prioritized inbox, email detail, preferences, calendar proposal approval, errors/status, and evaluation/demo visibility where needed.

## 11. Configuration And Secrets

Decision: Pydantic Settings with environment variables, `.env` for local development, checked-in `.env.example`, and separate development/test/demo settings.

Secrets and real email content must never be committed. Model selection, provider keys, calendar credentials, feature flags, database path, vector-store path, output language, locale/timezone defaults, and priority weights are configuration. Tests should default to fake providers and fixture data.

## 12. Logging And Observability

Decision: Python structured logging with JSON-compatible records and persisted processing status.

Track request or processing IDs, email IDs, stage status, model name, prompt version, token/cost metadata when available, retrieval IDs and scores, latency, failure reasons, and calendar proposal/execution status. No production observability platform is needed for V1.

## 13. Testing

Decision: pytest-centered testing with deterministic fakes.

- Unit tests: pytest.
- Integration tests: pytest with temporary SQLite and Chroma directories.
- API tests: FastAPI TestClient or HTTPX ASGI transport.
- Database tests: SQLAlchemy sessions against isolated SQLite databases.
- Retrieval tests: deterministic fake embeddings and isolated Chroma collections.
- LLM contract tests: fake LLM responses plus schema validation tests.
- Calendar approval tests: fake calendar adapter; assert zero unauthorized writes.
- End-to-end tests: API-level workflow over fixture inbox.
- Evaluation tests: scenario-based pass/fail checks plus reported metrics.

Dependencies requiring fakes: LLM provider, embedding provider, calendar provider, email source where provider-backed ingestion is used, and time/clock.

## 14. Evaluation And Experiment Tracking

Decision: Versioned JSONL fixtures, JSON predictions, CSV/Markdown reports, and lightweight run metadata files.

An experiment-tracking framework is not justified for V1. Store examples, expected labels, predictions, metrics, scenario pass/fail results, prompt versions, model names, retrieval settings, preference settings, and timestamped run IDs in versioned local files. This supports comparison of LLM-only analysis, LLM plus RAG, and RAG plus user preferences plus deterministic scoring.

## 15. Local Execution And Deployment

Decision: Local startup scripts using `uv`, optional Docker Compose for demo packaging, GitHub Actions CI, and lightweight demo deployment only after local execution works.

Local development and automated tests must not require deployment. V1 can run as two local processes: FastAPI backend and Vite frontend. SQLite and Chroma run embedded/local. A Dockerfile or Docker Compose setup is optional for demo reproducibility, not a prerequisite for development.

## Technology Decision Matrix

| Area | Options considered | Selected option | Primary reason | Main trade-off | Replacement difficulty |
|---|---|---|---|---|---|
| Python/runtime | Python 3.11, 3.12, 3.13 | Python 3.12 | Stable modern baseline with strong package compatibility | Not newest possible runtime | Low |
| Dependency management | pip/venv, Poetry, uv | uv | Fast reproducible local setup | Newer tool than pip | Low |
| Backend/API | FastAPI, Flask | FastAPI | Typed schemas, OpenAPI, DI, async support | Slightly more structure than Flask | Medium |
| Validation | Pydantic, dataclasses, ORM models | Pydantic v2 | Strong schema validation for LLM/API data | Requires mapping to persistence models | Medium |
| Database | SQLite, PostgreSQL | SQLite | Local reproducibility and no service dependency | Less production-like than PostgreSQL | Medium |
| DB access | SQLAlchemy, raw SQL, SQLModel | SQLAlchemy 2.x | Mature ORM/Core with PostgreSQL path | More setup than raw SQL | Medium |
| Migrations | Alembic, manual SQL | Alembic | Professional schema evolution | Added configuration | Low |
| Vector retrieval | Chroma, FAISS, pgvector | Chroma | Persistent local vectors with metadata filtering | Additional local storage format | Medium |
| LLM integration | Provider SDK directly, LangChain, custom port | Custom provider port | Replaceable and testable | More app-owned glue code | Low |
| Embeddings | Provider SDK directly, custom port | Custom provider port | Deterministic tests and re-index control | More app-owned glue code | Low |
| Orchestration | Python services, workflow library, agent framework | Python services | Matches fixed V1 workflow | Less visual workflow tooling | Medium |
| Calendar | Google Calendar direct, generic port, no real provider | Generic port plus Google adapter | Replaceable and testable | Adapter design required | Low |
| UI | Streamlit, React/TS, server-rendered | React/TypeScript/Vite | Demonstrates clean API boundary and usable UI | More effort than Streamlit | Medium |
| Config | python-dotenv only, Pydantic Settings, custom config | Pydantic Settings | Typed settings and env support | Added dependency | Low |
| Logging | print/logging, structlog, OpenTelemetry | stdlib logging with structured records | Simple and local | Less feature-rich than tracing stack | Low |
| Testing | unittest, pytest, Playwright-only | pytest plus focused tools | Broad Python testing support | Requires fixtures discipline | Low |
| Evaluation tracking | JSON/CSV, MLflow, Weights & Biases | Versioned JSONL/JSON/CSV/Markdown | Reproducible and small | Less dashboarding | Low |
| CI | GitHub Actions, none, cloud-specific CI | GitHub Actions | Common portfolio default | Requires repo hosting | Low |

## Compatibility Check

- Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic, pytest, Ruff, Pyright, Chroma, and modern React/Vite are mutually plausible.
- The stack supports local development with no managed database or vector service.
- Deterministic tests can run without paid external services using fake LLM, embedding, calendar, email, and clock adapters.
- SQLite and Chroma can coexist as local persistence layers; relational storage remains the audit source of truth.
- React communicates with the backend through typed JSON API contracts.
- Approval is enforced in backend/application services before calendar adapters are called.
- Model, embedding, calendar, and email providers remain replaceable behind ports.
- No multi-agent infrastructure is required.
- The stack is achievable for one developer and still demonstrates professional engineering.

## Final Stack Summary

Final technology stack:

- Python 3.12.
- `uv` and `pyproject.toml`.
- FastAPI backend.
- Pydantic v2 validation/settings.
- SQLAlchemy 2.x, Alembic, SQLite.
- Chroma local vector store.
- Plain Python provider ports for LLM, embeddings, email source, and calendar.
- React, TypeScript, and Vite frontend.
- pytest, pytest-asyncio, HTTPX/TestClient, Ruff, Pyright.

Development tools:

- `uv`, Ruff, Pyright, pytest, Alembic, Vite.

Runtime services:

- FastAPI backend process.
- Vite/dev or built frontend.
- Local SQLite database.
- Local Chroma persistence directory.

External services:

- Configured LLM provider.
- Configured embedding provider.
- Optional Google Calendar demo adapter.

Replaceable adapters:

- LLM provider.
- Embedding provider.
- Email source.
- Calendar provider.
- Vector store.
- Database backend.

Unresolved decisions:

- Exact LLM provider and model.
- Exact embedding provider and model.
- Exact supported non-English fixture languages.
- Exact priority scoring weights and thresholds.
- Exact deployment host if a public demo is needed.

Decisions intentionally deferred until implementation:

- Concrete API route names.
- Database table and migration details.
- Pydantic schema field names beyond the conceptual domain model.
- UI component library, if any.
- Exact date parsing library.
- Exact CI workflow commands.

## ADR Index

- [ADR-001: Python Tooling And Project Layout](../decisions/ADR-001-python-tooling-and-project-layout.md)
- [ADR-002: FastAPI Backend](../decisions/ADR-002-fastapi-backend.md)
- [ADR-003: Pydantic Schema Boundaries](../decisions/ADR-003-pydantic-schema-boundaries.md)
- [ADR-004: SQLite SQLAlchemy And Alembic Persistence](../decisions/ADR-004-sqlite-sqlalchemy-alembic-persistence.md)
- [ADR-005: Chroma Local Vector Retrieval](../decisions/ADR-005-chroma-local-vector-retrieval.md)
- [ADR-006: Replaceable LLM Provider Port](../decisions/ADR-006-replaceable-llm-provider-port.md)
- [ADR-007: Replaceable Embedding Provider Port](../decisions/ADR-007-replaceable-embedding-provider-port.md)
- [ADR-008: Plain Python Orchestration Services](../decisions/ADR-008-plain-python-orchestration-services.md)
- [ADR-009: Calendar Port With Optional Google Adapter](../decisions/ADR-009-calendar-port-with-optional-google-adapter.md)
- [ADR-010: React TypeScript Vite UI](../decisions/ADR-010-react-typescript-vite-ui.md)
- [ADR-011: Typed Environment Configuration](../decisions/ADR-011-typed-environment-configuration.md)
- [ADR-012: Local Structured Logging](../decisions/ADR-012-local-structured-logging.md)
- [ADR-013: Pytest With Deterministic Fakes](../decisions/ADR-013-pytest-with-deterministic-fakes.md)
- [ADR-014: File-Based Evaluation Tracking](../decisions/ADR-014-file-based-evaluation-tracking.md)
- [ADR-015: Local-First Execution And CI](../decisions/ADR-015-local-first-execution-and-ci.md)
