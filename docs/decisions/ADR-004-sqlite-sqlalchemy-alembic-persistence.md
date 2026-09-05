# ADR-004: SQLite SQLAlchemy And Alembic Persistence

## Status
Accepted

## Context
V1 requires local persistence for source emails, processed content, analysis signals, retrieved context, priority factors, preferences, proposals, approvals, and execution results. It must be auditable, reproducible, and portable beyond SQLite if needed. This supports FR-13, NFR-02, NFR-05, NFR-07, and NFR-12.

## Decision
Use SQLite as the V1 database, SQLAlchemy 2.x for database access, Alembic for migrations, and repository classes as the persistence boundary.

## Alternatives considered
PostgreSQL, raw SQL, SQLModel, file-only JSON storage, and an embedded document database.

## Consequences
Local setup stays simple while schema evolution remains professional. SQLAlchemy keeps a realistic path to PostgreSQL. JSON columns can store structured factors and extracted candidates while relational tables preserve identity and relationships. The trade-off is maintaining mappings and avoiding SQLite-specific shortcuts.

## Reversal strategy
Switch SQLAlchemy engine configuration and migrations to PostgreSQL. Keep repository interfaces stable and update only persistence models and migration scripts.
