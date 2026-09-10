# Private Demo Deployment

Target: one private Docker host, using Docker Compose. Keep this deployment on
fixture data and fake providers until the real-provider milestones are done.

## Environment

Backend:

```text
EMAIL_AGENT_ENVIRONMENT=demo
EMAIL_AGENT_DATABASE_URL=sqlite:////data/email_agent.db
EMAIL_AGENT_VECTOR_STORE_PATH=/data/chroma
EMAIL_AGENT_ALLOWED_ORIGINS=["https://your-private-frontend.example"]
EMAIL_AGENT_LLM_PROVIDER=fake
EMAIL_AGENT_EMBEDDING_PROVIDER=fake
EMAIL_AGENT_CALENDAR_PROVIDER=fake
EMAIL_AGENT_CALENDAR_EXECUTION_ENABLED=false
```

Frontend build:

```text
VITE_API_BASE=https://your-private-api.example
```

## Deploy

```bash
docker compose build
docker compose up -d
scripts/hosted_smoke.sh https://your-private-api.example
```

Restrict access with the host firewall, VPN, reverse-proxy basic auth, or the
hosting provider's private app controls.

## Persistence

Mount `/data` for the API if demo state should survive restarts. SQLite and
Chroma are acceptable for a private single-user demo; use a managed database
before multi-user production.

## Rollback

```bash
docker compose down
docker compose up -d
```

To remove demo data:

```bash
docker compose down -v
```
