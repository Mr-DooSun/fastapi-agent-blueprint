"""PostToolUse Edit|Write — verify-first reminder (Phase 3 of #117 / #122).

Emits a stderr reminder when a `.py` file is edited and the latest Phase 2
marker is NOT an [exploration]/[탐색] token. Read-only on Phase 2 markers
(IC-11 from PR #126; Phase 4 #123 owns lifecycle). Fail-open on every error
path (HC-3.6).

REMINDER_TEXT is frozen at Phase 3 and string-equal to the Codex side's
`.codex/hooks/verify_first.py` constant. Parity is asserted by
`tests/unit/agents_shared/test_verify_first.py::test_reminder_text_string_equality`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = REPO_ROOT / ".claude" / "state"

EXPLORATION_TOKENS = frozenset({"exploration", "탐색"})

REMINDER_TEXT = "\n".join(
    [
        "[verify-first] verify 단계가 누락된 것 같습니다. 변경된 .py 파일에 대해 테스트/검증을 권장합니다.",
        "[verify-first] Verify step appears to be missing for the changed .py files.",
        "Suggested next: `/test-domain run <domain>` (or `pytest tests/unit/<domain>/`)",
        "Silence with `[exploration]` / `[탐색]` prefix when intentionally exploring.",
    ]
)


def read_latest_token_marker(state_dir: Path) -> str | None:
    """Return token of the most-recent valid Phase 2 marker, or None.

    Most-recent = max by `ts` field (ISO 8601 UTC; lexically chronological).
    Read-only — never deletes/mutates (IC-11). Phase 4 owns lifecycle.
    """
    if not state_dir.exists():
        return None
    candidates: list[tuple[str, str]] = []
    for path in state_dir.glob("exception-token-*.json"):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        ts = record.get("ts")
        token = record.get("token")
        if isinstance(ts, str) and isinstance(token, str):
            candidates.append((ts, token))
    if not candidates:
        return None
    return max(candidates, key=lambda item: item[0])[1]


def extract_file_path(payload: dict) -> str | None:
    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path")
    return file_path if isinstance(file_path, str) else None


def is_python_source(file_path: str | None) -> bool:
    return bool(file_path) and file_path.endswith(".py")


def should_remind(payload: dict, state_dir: Path = STATE_DIR) -> bool:
    if not is_python_source(extract_file_path(payload)):
        return False
    token = read_latest_token_marker(state_dir)
    return token not in EXPLORATION_TOKENS


def main() -> int:
    """Read PostToolUse Edit|Write payload from stdin; emit reminder if needed.

    Fail-open: any unexpected exception returns 0 with no output.
    """
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return 0
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            return 0
        if should_remind(payload):
            print(REMINDER_TEXT, file=sys.stderr)
    except Exception:  # noqa: BLE001 — fail-open per HC-3.6
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
