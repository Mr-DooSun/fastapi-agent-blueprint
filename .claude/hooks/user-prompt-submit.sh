#!/usr/bin/env bash
# UserPromptSubmit Hook: Exception-token parser (Phase 2 of #117 / #121)
# Informational only — exit 0 in all cases, never blocks prompt submission.

INPUT=$(cat)
echo "$INPUT" | python3 "$(dirname "$0")/user_prompt_submit.py"
