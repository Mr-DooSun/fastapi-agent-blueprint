"""UserPromptSubmit Hook: Exception-token parser (Phase 2 of #117 / #121)

Parses the leading exception token (`[trivial]` / `[hotfix]` / `[exploration]`
/ `[자명]` / `[긴급]` / `[탐색]`) from the first line of a user prompt, after
NFKC normalisation. Writes a per-session marker file under `.claude/state/`
when matched. Output is informational only — never blocks prompt submission.

Contract — payload schema shared with Codex side:
    {"matched": bool, "token": str | None, "rationale_required": bool}

Invariant: this hook never overrides safety / sandbox / Absolute Prohibitions
(IC-1). It only writes a marker file after a token is detected.
"""

from __future__ import annotations

import json
import re
import sys
import time
import unicodedata
import uuid
from pathlib import Path

TOKEN_REGEX = re.compile(
    r"^\s*\[(trivial|hotfix|exploration|자명|긴급|탐색)\](?:\s|$)",
    re.IGNORECASE,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = REPO_ROOT / ".claude" / "state"


def parse_exception_token(prompt: str) -> dict:
    """Return canonical decision payload per IC-3.

    Always returns the same shape regardless of input. Token name is lowercased
    for English variants; Korean tokens pass through unchanged (NFKC-normalised).
    """
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
    """Write the token decision payload to a per-session marker file.

    Marker schema: {matched, token, rationale_required, ts (ISO 8601)}.
    Returns the marker path on write, or None when not matched.
    """
    if not payload.get("matched"):
        return None
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%dT%H%M%S", time.gmtime())
    marker = STATE_DIR / f"exception-token-{ts}-{uuid.uuid4().hex[:12]}.json"
    record = dict(payload)
    record["ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    marker.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")
    return marker


def read_prompt() -> str:
    """Read prompt text from Claude UserPromptSubmit stdin payload.

    Claude Code SDK delivers a JSON object with a `prompt` field. Empty stdin
    or invalid JSON degrades to empty prompt — informational hook never crashes.
    """
    raw = sys.stdin.read()
    if not raw.strip():
        return ""
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return ""
    if isinstance(payload, dict):
        return str(payload.get("prompt", "") or "")
    return ""


def main() -> int:
    prompt = read_prompt()
    payload = parse_exception_token(prompt)
    write_marker(payload)
    print(json.dumps(payload, ensure_ascii=False), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
