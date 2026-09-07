# Email Agent

Local-first email triage demo with deterministic fake providers. It imports a
synthetic inbox, analyzes messages, ranks priority, shows retrieved context,
captures user preferences, and requires approval before calendar execution.

## Setup

Requirements:

- Python 3.12
- `uv`
- Node.js 25 or compatible current Node

Install dependencies:

```bash
uv sync
npm --prefix frontend ci
```

Runtime defaults are safe for local use and need no real credentials. Copy
`.env.example` to `.env` only for local overrides.

## Run Locally

Start the API and frontend:

```bash
scripts/dev.sh
```

Open `http://127.0.0.1:5173`. The API runs at `http://127.0.0.1:8000`.

Seed and process the demo inbox after the API is running:

```bash
scripts/demo.sh
```

## Real Email Smoke

Use a test mailbox or sanitized exported `.eml` files. Keep samples under
`real-email-smoke/`; that directory and `*.eml` files are ignored by Git.

Start the API with a local throwaway database and OpenAI settings:

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

Cleanup:

```bash
rm -f data/real_email_smoke.db
```

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

Private deployment notes are in `docs/deployment.md`.

## Current Limits

- Providers default to deterministic fakes.
- Google Calendar is adapter-scaffolded and only executes when credentials and
  `EMAIL_AGENT_CALENDAR_EXECUTION_ENABLED=true` are configured.
- The dataset is synthetic; do not commit real inbox data or secrets.
- The frontend is a local demo UI, not a production auth boundary.
- Real-email smoke testing does not need Gmail, IMAP, or calendar access.
