# Email Agent

Email Agent is a local-first AI email triage app. It imports a synthetic inbox,
extracts structured signals, ranks priority, retrieves related context, applies
user preferences, and creates calendar proposals that require explicit approval
before execution.

The default demo runs with deterministic fake AI providers, so the full system
can be cloned, tested, and reviewed without API keys or private email data.

## Why This Project Exists

This project is a portfolio-grade example of practical AI engineering rather
than a thin prompt wrapper. It shows how to build an LLM feature behind stable
interfaces, test the orchestration deterministically, evaluate behavior with
fixtures, and keep risky tool actions behind approval gates.

It demonstrates:

- FastAPI backend with typed request and response schemas.
- React and TypeScript inbox UI for triage, preferences, and approvals.
- Replaceable LLM and embedding provider ports with deterministic fakes.
- Retrieval-augmented context using a local Chroma vector store.
- Rule-based priority scoring with explanations.
- SQLAlchemy persistence with Alembic migrations.
- Gmail import and label-writing boundaries, disabled unless configured.
- Calendar proposal flow with fake and Google adapter boundaries.
- Scenario evaluation for classification, retrieval, preferences, priority, and
  unauthorized-write checks.
- CI-friendly tests, type checks, formatting, linting, and privacy scanning.

## Demo Flow

The local demo uses `datasets/fixtures/dev.jsonl` and fake providers:

1. Import synthetic emails.
2. Analyze each email into structured signals.
3. Retrieve related prior context where useful.
4. Apply user preferences and priority scoring.
5. Persist analysis, priority factors, context, and calendar proposals.
6. Review the prioritized inbox in the frontend.
7. Approve or reject proposed calendar actions.

No real mailbox, calendar, or model credentials are required for this path.

## Architecture

```text
Synthetic fixtures or .eml files
        |
        v
FastAPI import and processing routes
        |
        v
Triage orchestration
  |-- email normalization
  |-- retrieval service and vector store
  |-- LLM analysis provider port
  |-- priority scoring engine
  |-- calendar proposal generation
        |
        v
SQLite persistence via SQLAlchemy
        |
        v
React inbox UI and approval controls
```

Key code areas:

- `src/email_agent/api` - FastAPI app factory and HTTP routes.
- `src/email_agent/ai` - provider interface, fake provider, OpenAI adapter, and
  analysis service.
- `src/email_agent/orchestration` - end-to-end triage flow.
- `src/email_agent/retrieval` - local retrieval and embedding abstractions.
- `src/email_agent/priority` - deterministic priority scoring.
- `src/email_agent/calendar.py` - approval-gated calendar port.
- `src/email_agent/persistence` - repository and SQLAlchemy implementation.
- `src/email_agent/evaluation` - fixture validation and scenario evaluation.
- `frontend` - React/Vite triage UI.

More detail is in `docs/architecture.md`.

## Requirements

- Python 3.12
- `uv`
- Node.js 22 LTS or newer

## Setup

```bash
uv sync
npm --prefix frontend ci
```

Runtime defaults are safe for local use. Copy `.env.example` to `.env` only if
you want local overrides or real provider settings.

## Run Locally

Start the API and frontend:

```bash
scripts/dev.sh
```

Open `http://127.0.0.1:5173`. The API runs at `http://127.0.0.1:8000`.

Seed and process the synthetic demo inbox after the API is running:

```bash
scripts/demo.sh
```

## API Highlights

- `GET /health` - health check.
- `POST /imports/fixtures` - import synthetic fixture emails.
- `POST /imports/eml` - import bounded local `.eml` files.
- `POST /sync/gmail` - optional Gmail unread sync when credentials are
  configured.
- `POST /processing/inbox` - run triage across imported emails.
- `GET /inbox` - read prioritized inbox items.
- `GET /emails/{email_id}` - inspect analysis, priority factors, context, and
  proposals for one email.
- `PUT /preferences/{preference_id}` - save a user preference.
- `POST /proposals/{proposal_id}/approval` - approve or reject a calendar
  proposal.
- `POST /proposals/{proposal_id}/execute` - execute only approved proposals.

## Evaluation

The deterministic evaluation compares three variants:

- `llm_only` - analysis and priority without retrieval or preferences.
- `llm_rag` - adds retrieval context.
- `full_system` - adds retrieval plus preference behavior.

Run it locally:

```bash
uv run python -m email_agent.evaluation.run --config proposed/config/eval.dev.json
```

The current fixture-backed report is in `docs/evaluation_report.md`. It covers
classification, extraction, summary faithfulness, retrieval recall, preference
adherence, priority band accuracy, calendar proposal behavior, and unauthorized
calendar writes.

The evaluation is intentionally synthetic and deterministic. It proves local
workflow behavior and schema contracts; it does not claim production LLM quality
or broad mailbox coverage.

## Quality Gate

Backend:

```bash
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv run python scripts/check_privacy.py
uv run python -m email_agent.evaluation.run --config proposed/config/eval.dev.json
```

Frontend:

```bash
npm --prefix frontend run format:check
npm --prefix frontend run lint
npm --prefix frontend run typecheck
npm --prefix frontend test
npm --prefix frontend run build
```

Optional container build:

```bash
docker compose build
```

GitHub Actions runs the backend and frontend quality gates on push and pull
request.

## Real Email Smoke Testing

Use a test mailbox or sanitized exported `.eml` files. Keep samples under
`real-email-smoke/`; that directory and `*.eml` files are ignored by Git.

Start the API with a throwaway database and OpenAI settings:

```bash
EMAIL_AGENT_DATABASE_URL=sqlite:///./data/real_email_smoke.db \
EMAIL_AGENT_LLM_PROVIDER=openai \
EMAIL_AGENT_LLM_MODEL=gpt-5 \
EMAIL_AGENT_LLM_API_KEY=... \
EMAIL_AGENT_CALENDAR_PROVIDER=fake \
EMAIL_AGENT_CALENDAR_EXECUTION_ENABLED=false \
uv run uvicorn email_agent.api:create_app --factory --host 127.0.0.1 --port 8000
```

In another shell, import and process up to five `.eml` files:

```bash
scripts/real_email_smoke.sh real-email-smoke/message-1.eml
```

Review output quality with `docs/real_llm_quality_smoke.md`.

## Safety Boundaries

- Fake providers are the default.
- Real credentials are required only when real providers are explicitly enabled.
- Calendar execution is disabled by default.
- Calendar actions require stored approval before execution.
- Real email smoke files, local databases, tokens, and secrets are ignored by
  Git.
- `scripts/check_privacy.py` scans tracked files for obvious secret patterns.

## Current Limits

- The UI is a local demo interface, not a production authentication boundary.
- The default dataset is synthetic and small.
- Real Gmail behavior requires local OAuth configuration.
- Google Calendar execution is represented by an adapter boundary and fake
  execution path; the real Google adapter is not implemented yet.
- This repo should not be used as a production personal-data service without
  auth, retention policy, backups, and managed secrets.

## License

MIT. See `LICENSE`.
