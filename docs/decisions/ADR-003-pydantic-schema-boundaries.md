# ADR-003: Pydantic Schema Boundaries

## Status
Accepted

## Context
The system must validate structured LLM outputs before downstream use and keep domain entities, API contracts, and database records from becoming one tightly coupled model. This supports FR-04 through FR-18, NFR-02, NFR-06, NFR-07, and NFR-09.

## Decision
Use Pydantic v2 for domain validation, LLM output schemas, API request models, API response models, and typed settings. Keep SQLAlchemy ORM models separate from Pydantic models.

## Alternatives considered
Python dataclasses, SQLAlchemy ORM models as shared domain models, and SQLModel.

## Consequences
Schema validation is explicit and reusable across LLM, API, and service boundaries. Mapping between domain/API/persistence models adds some boilerplate but protects auditability and prevents persistence concerns from leaking into business logic.

## Reversal strategy
Replace Pydantic domain models with dataclasses or another validation library behind mapping functions. Keep API and persistence boundaries separate during migration.
