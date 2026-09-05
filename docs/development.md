# Local Development

This project uses Python 3.12, `uv`, Ruff, Pyright, pytest, and local fake
providers by default.

## Setup

Install the selected Python version if it is not already available:

```bash
uv python install 3.12
```

Create and synchronize the project-local environment:

```bash
uv sync
```

The virtual environment is created at:

```text
.venv/
```

## Configuration

Runtime settings are loaded from environment variables with the
`EMAIL_AGENT_` prefix. A safe example file is checked in at `.env.example`.

The default local configuration uses fake providers and does not require real
credentials:

```text
EMAIL_AGENT_LLM_PROVIDER=fake
EMAIL_AGENT_LLM_MODEL=fake-llm
EMAIL_AGENT_EMBEDDING_PROVIDER=fake
EMAIL_AGENT_EMBEDDING_MODEL=fake-embedding
EMAIL_AGENT_CALENDAR_PROVIDER=fake
EMAIL_AGENT_CALENDAR_EXECUTION_ENABLED=false
EMAIL_AGENT_OUTPUT_LANGUAGE=en
EMAIL_AGENT_LOCALE=en_US
EMAIL_AGENT_TIMEZONE=UTC
```

For local overrides, create `.env` from `.env.example`. The `.env` file is
ignored by Git and must not contain real credentials in committed files.

## Quality Gate

Run the same commands used by CI:

```bash
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
```

## Health Check

The current backend skeleton exposes a FastAPI app factory and a stable
`/health` route. Until a server startup command is added later, smoke-test the
health route locally through the test client:

```bash
uv run python -c "from fastapi.testclient import TestClient; from email_agent.api import create_app; print(TestClient(create_app()).get('/health').json())"
```

Expected output:

```text
{'status': 'ok'}
```
