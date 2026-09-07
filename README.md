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

## Current Limits

- Providers default to deterministic fakes.
- Google Calendar is adapter-scaffolded and only executes when credentials and
  `EMAIL_AGENT_CALENDAR_EXECUTION_ENABLED=true` are configured.
- The dataset is synthetic; do not commit real inbox data or secrets.
- The frontend is a local demo UI, not a production auth boundary.
