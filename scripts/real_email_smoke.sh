#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -eq 0 ]; then
  echo "usage: scripts/real_email_smoke.sh path/to/message.eml [...]" >&2
  exit 2
fi

API="${API:-http://127.0.0.1:8000}"
PAYLOAD="$(python -c 'import json,sys; print(json.dumps({"paths": sys.argv[1:]}))' "$@")"

curl -fsS "$API/health" >/dev/null
curl -fsS -X POST "$API/imports/eml" \
  -H "content-type: application/json" \
  -d "$PAYLOAD"
printf '\n'
curl -fsS -X POST "$API/processing/inbox" \
  -H "content-type: application/json" \
  -d '{}'
printf '\n'
curl -fsS "$API/inbox"
printf '\n'
