#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "usage: scripts/hosted_smoke.sh https://api.example" >&2
  exit 2
fi

API="${1%/}"

curl -fsS "$API/health" >/dev/null
curl -fsS -X POST "$API/imports/fixtures" \
  -H "content-type: application/json" \
  -d '{"path":"datasets/fixtures/dev.jsonl"}' >/dev/null
curl -fsS -X POST "$API/processing/inbox" \
  -H "content-type: application/json" \
  -d '{}' >/dev/null
curl -fsS "$API/inbox"
printf '\n'
