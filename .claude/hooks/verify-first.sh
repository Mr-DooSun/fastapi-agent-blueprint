#!/usr/bin/env bash
# PostToolUse Edit|Write Hook — verify-first reminder (Phase 3 of #117 / #122).
# Always exits 0 (informational only, never blocks tool use — HC-3.3).
INPUT=$(cat)
echo "$INPUT" | python3 "$(dirname "$0")/verify_first.py" || true
exit 0
