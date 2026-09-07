#!/usr/bin/env bash
set -euo pipefail

API="${API:-http://127.0.0.1:8000}"

curl -fsS "$API/health" >/dev/null
curl -fsS -X POST "$API/imports/fixtures" \
  -H "content-type: application/json" \
  -d '{"path":"datasets/fixtures/dev.jsonl"}'
printf '\n'
curl -fsS -X PUT "$API/preferences/preference-finance-demo" \
  -H "content-type: application/json" \
  -d '{"id":"preference-finance-demo","preference_type":"sender","value":"finance@example.com","effect":"boost","weight":1,"enabled":true}'
printf '\n'
curl -fsS -X POST "$API/processing/inbox" \
  -H "content-type: application/json" \
  -d '{}'
printf '\n'
curl -fsS -X POST "$API/proposals/proposal-email-dev-003-meeting-1/approval" \
  -H "content-type: application/json" \
  -d '{"decision":"approved","decided_by":"demo"}'
printf '\n'
curl -fsS -X POST "$API/proposals/proposal-email-dev-003-meeting-1/execute" \
  -H "content-type: application/json"
printf '\n'
curl -fsS "$API/inbox"
printf '\n'
