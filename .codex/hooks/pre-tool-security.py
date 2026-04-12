from __future__ import annotations

import json
import re
import sys


def deny(reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    raise SystemExit(0)


payload = json.load(sys.stdin)
command = payload.get("tool_input", {}).get("command", "")

if re.search(r"\bgit\s+reset\s+--hard\b|\bgit\s+checkout\s+--\b", command):
    deny("Destructive git rollback is forbidden in this repository.")

if re.search(r"\brm\s+-rf\b|\bdd\s+if=|\bmkfs\b", command):
    deny(
        "Destructive filesystem commands require explicit user approval and exact scope."
    )

if re.search(r"text\s*\(\s*f[\"']", command):
    deny("Potential SQL injection pattern detected in shell-written code.")

if re.search(r"from\s+src\..*\.infrastructure", command) and "/domain/" in command:
    deny("Domain layer must not import Infrastructure directly.")

if re.search(
    r"(password|secret|api_key|token)\s*=\s*[\"'][^\"']{3,}[\"']",
    command,
    re.IGNORECASE,
):
    deny("Possible hardcoded secret detected in shell-written content.")
