#!/usr/bin/env bash
set -euo pipefail

trap 'kill 0' EXIT
uv run uvicorn email_agent.api:create_app --factory --reload --host 127.0.0.1 --port 8000 &
npm --prefix frontend run dev -- --host 127.0.0.1
