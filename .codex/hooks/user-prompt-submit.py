"""UserPromptSubmit Hook (Codex side).

Behaviour-preserving extension under Phase 2 of #117 / #121. The pre-existing
safety check (rule-bypass / destructive git / destructive shell) runs first;
when it emits ``decision: block`` the hook exits **without** parsing the
exception-token vocabulary — i.e. dangerous prompts never produce a marker
file even if they happen to start with `[trivial]`. Only after safety has
passed the prompt does the parser run; its output is informational only and
mirrors the Claude-side payload schema (IC-3).

Decision payload (shared with `.claude/hooks/user_prompt_submit.py`):
    {"matched": bool, "token": str | None, "rationale_required": bool}

Marker file (when matched) carries the decision payload plus an ISO 8601 ``ts``
timestamp.
"""

from __future__ import annotations

import json
import re
import sys
import time
import unicodedata
import uuid
from pathlib import Path

PROMPT_RULES: list[tuple[re.Pattern[str], str, str]] = [
    (
        re.compile(
            r"(ignore|disable|bypass).*(AGENTS\.md|CLAUDE\.md|hooks?|sandbox|approval|rules?)",
            re.IGNORECASE,
        ),
        "Rule-bypass request detected.",
        "Do not bypass repository rules or Codex safety controls. Ask for a scoped goal instead.",
    ),
    (
        re.compile(r"\bgit\s+reset\s+--hard\b|\bgit\s+checkout\s+--\b", re.IGNORECASE),
        "Destructive git command requested.",
        "This repository does not allow destructive git rollback without explicit confirmation and scope.",
    ),
    (
        re.compile(r"\brm\s+-rf\b|\bdd\s+if=|\bmkfs\b", re.IGNORECASE),
        "Destructive shell command requested.",
        "Ask the user to confirm the exact path or target before any destructive command is considered.",
    ),
]

TOKEN_REGEX = re.compile(
    r"^\s*\[(trivial|hotfix|exploration|자명|긴급|탐색)\](?:\s|$)",
    re.IGNORECASE,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = REPO_ROOT / ".codex" / "state"


def parse_exception_token(prompt: str) -> dict:
    """Return canonical decision payload per IC-3 (mirrors Claude side)."""
    if not prompt:
        return {"matched": False, "token": None, "rationale_required": False}
    normalised = unicodedata.normalize("NFKC", prompt)
    match = TOKEN_REGEX.match(normalised)
    if not match:
        return {"matched": False, "token": None, "rationale_required": False}
    token = match.group(1)
    if token.isascii():
        token = token.lower()
    return {"matched": True, "token": token, "rationale_required": True}


def write_marker(payload: dict) -> Path | None:
    if not payload.get("matched"):
        return None
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%dT%H%M%S", time.gmtime())
    marker = STATE_DIR / f"exception-token-{ts}-{uuid.uuid4().hex[:12]}.json"
    record = dict(payload)
    record["ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    marker.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
    return marker


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        # Empty stdin → informational, fail-open (parity with Claude side).
        return 0
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        # Malformed payload → fail-open. The pre-Phase-2 hook crashed here;
        # Phase 2 prefers symmetry with Claude side and Non-Goal "false-positive
        # blocking" (issue #117) over preserving the crash behaviour.
        return 0
    if not isinstance(payload, dict):
        return 0
    prompt = payload.get("prompt", "") or ""

    for pattern, reason, extra in PROMPT_RULES:
        if pattern.search(prompt):
            print(
                json.dumps(
                    {
                        "decision": "block",
                        "reason": reason,
                        "hookSpecificOutput": {
                            "hookEventName": "UserPromptSubmit",
                            "additionalContext": extra,
                        },
                    }
                )
            )
            return 0

    decision = parse_exception_token(prompt)
    write_marker(decision)
    print(json.dumps(decision, ensure_ascii=False), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
