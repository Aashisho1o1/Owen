#!/usr/bin/env bash
set -euo pipefail

API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:8000}"

# Health gate: stop immediately if backend is not healthy.
curl -sS -i "${API_BASE_URL}/api/health" | tee /tmp/owen-api-health.out >/dev/null
HEALTH_STATUS=$(awk 'NR==1 {print $2}' /tmp/owen-api-health.out)
if [[ "${HEALTH_STATUS}" != "200" ]]; then
  echo "backend smoke failed: /api/health returned HTTP ${HEALTH_STATUS}" >&2
  cat /tmp/owen-api-health.out >&2
  exit 1
fi

EMAIL="e2e.$(date +%s)@example.com"
PASSWORD="StrongPass123"

curl -sS -X POST "${API_BASE_URL}/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"${EMAIL}\",\"password\":\"${PASSWORD}\",\"name\":\"Eee User\"}" > /tmp/owen-register.json

curl -sS -X POST "${API_BASE_URL}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"${EMAIL}\",\"password\":\"${PASSWORD}\"}" > /tmp/owen-login.json

PYTHON_BIN="${PYTHON_BIN:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  PYTHON_BIN=python
fi

TOKEN=$($PYTHON_BIN - <<'PY'
import json
import sys

payload = json.load(open('/tmp/owen-login.json'))
token = payload.get('access_token')
if not token:
    print('backend smoke failed: login response did not include access_token', file=sys.stderr)
    print(json.dumps(payload, indent=2), file=sys.stderr)
    raise SystemExit(1)

print(token)
PY
)

curl -sS -i "${API_BASE_URL}/api/documents" -H "Authorization: Bearer ${TOKEN}" >/tmp/owen-documents.out
curl -sS -i "${API_BASE_URL}/api/folders" -H "Authorization: Bearer ${TOKEN}" >/tmp/owen-folders.out

echo "backend smoke ok"
