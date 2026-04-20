#!/usr/bin/env bash
# --------------------------------------------------------------
# Quickstart demo — exercise the user domain via curl.
# Expects a quickstart server running on http://127.0.0.1:8001
# (start it with `make quickstart` in another terminal).
# --------------------------------------------------------------

set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8001}"

note() { printf "\n\033[1;36m→ %s\033[0m\n" "$*"; }
run()  { printf "\033[0;90m$ %s\033[0m\n" "$*"; eval "$*"; }

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required but not installed." >&2
  exit 1
fi

# Pretty-print JSON if python3 is available, otherwise pass through.
pretty() {
  if command -v python3 >/dev/null 2>&1; then
    python3 -m json.tool 2>/dev/null || cat
  else
    cat
  fi
}

note "Health check"
run "curl -sS '${BASE_URL}/health' | pretty"

note "Create a user"
CREATE_BODY='{"username":"alice","full_name":"Alice Liddell","email":"alice@example.com","password":"secret123"}'
CREATE_RESPONSE="$(curl -sS -X POST "${BASE_URL}/v1/user" \
  -H 'Content-Type: application/json' \
  -d "${CREATE_BODY}")"
echo "${CREATE_RESPONSE}" | pretty

USER_ID="$(echo "${CREATE_RESPONSE}" | python3 -c "import json,sys;print(json.load(sys.stdin)['data']['id'])" 2>/dev/null || echo "")"

if [ -z "${USER_ID}" ]; then
  echo "Could not parse created user id from response — aborting." >&2
  exit 1
fi

note "Get the user by id (id=${USER_ID})"
run "curl -sS '${BASE_URL}/v1/user/${USER_ID}' | pretty"

note "List users (page=1, pageSize=10)"
run "curl -sS '${BASE_URL}/v1/users?page=1&pageSize=10' | pretty"

note "Update the user"
UPDATE_BODY='{"full_name":"Alice (updated)"}'
run "curl -sS -X PUT '${BASE_URL}/v1/user/${USER_ID}' -H 'Content-Type: application/json' -d '${UPDATE_BODY}' | pretty"

note "Delete the user"
run "curl -sS -X DELETE '${BASE_URL}/v1/user/${USER_ID}' | pretty"

note "Done. Swagger UI: ${BASE_URL}/docs-swagger"
