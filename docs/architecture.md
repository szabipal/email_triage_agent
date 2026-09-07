# Architecture

The app is a local-first FastAPI and React system with replaceable provider
ports. The default path uses synthetic fixtures and fake providers so the whole
demo runs without secrets.

## Components

- `src/email_agent/domain`: Pydantic domain models for email, analysis,
  priority, retrieved context, preferences, calendar proposals, and approvals.
- `src/email_agent/api`: FastAPI app factory, fixture import, processing,
  `.eml` import, processing, inbox/detail reads, preference writes, and calendar
  approval/execution routes.
- `src/email_agent/orchestration`: Plain Python triage flow that normalizes
  email, retrieves context when configured, calls analysis, scores priority, and
  writes calendar proposals.
- `src/email_agent/ai`: Analysis service and provider port. Fake output is used
  for deterministic tests and demos.
- `src/email_agent/retrieval`: Chroma-backed local retrieval with replaceable
  embedding provider.
- `src/email_agent/priority`: Rule-based priority scoring and explanations.
- `src/email_agent/calendar`: Calendar port, fake adapter, Google adapter
  boundary, proposal decisions, and approval-gated execution.
- `src/email_agent/persistence`: SQLAlchemy repository over SQLite.
- `src/email_agent/evaluation`: Fixture validation and deterministic scenario
  evaluation.
- `frontend`: React/Vite local inbox UI.

## Data Flow

1. Fixtures are imported through `POST /imports/fixtures`, or controlled local
   `.eml` files are imported through `POST /imports/eml`.
2. `POST /processing/inbox` loads emails and runs `triage_inbox`.
3. Each email is normalized, optionally matched against retrieved context,
   analyzed, scored, and persisted with proposals.
4. The UI reads `GET /inbox`, `GET /emails/{email_id}`, `GET /preferences`,
   and `GET /proposals`.
5. Calendar proposals move through `POST /proposals/{id}/approval`.
6. `POST /proposals/{id}/execute` writes to the calendar adapter only after an
   approval exists.

## Boundaries

Configuration is typed in `Settings` and read from `EMAIL_AGENT_` environment
variables. Real provider credentials are required only when a non-fake provider
is selected. CI and local gates include tests, type checks, evaluation, and a
privacy scan for obvious secret patterns.

OpenAI mode uses the configured model for analysis. Real-email smoke testing
keeps calendar execution on the fake adapter unless a later milestone wires a
real calendar provider.

Structured logs include stable email IDs and triage stages so local runs can be
audited without hosted tracing.
