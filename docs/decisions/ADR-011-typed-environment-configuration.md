# ADR-011: Typed Environment Configuration

## Status
Accepted

## Context
The system must keep secrets and real email contents out of Git while supporting model selection, feature flags, priority weights, database paths, vector paths, output language, locale/timezone defaults, and development/test/demo environments. This supports NFR-04, NFR-05, NFR-11, FR-10, and FR-18.

## Decision
Use Pydantic Settings with environment variables, local `.env` files, checked-in `.env.example`, and typed settings objects.

## Alternatives considered
Raw `os.environ`, python-dotenv only, YAML-only configuration, and custom config loaders.

## Consequences
Configuration is validated at startup and documented through typed fields. Tests can override settings cleanly. The trade-off is an additional dependency and a small settings module.

## Reversal strategy
Replace Pydantic Settings with another configuration loader while keeping the same settings object interface for application services.
