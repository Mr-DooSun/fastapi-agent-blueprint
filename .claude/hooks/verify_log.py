"""PostToolUse Bash hook — record verify-class commands (#334).

`.claude/` read verify-log state it never produced. `tools/check_state_lifecycle.py`
globs `verify-log-*.json` across every harness state dir and
`tools/governor_state_doctor.py` reports stale counts for all three, but only
`.codex` and `.antigravity` ever wrote one: `.claude` had no `PostToolUse`
matcher for `Bash`, so no hook here ever saw a command to record.

Registering the matcher is the substance of the fix — adding the functions alone
would have left them with no call site.

Thin shim over `.agents/shared/governor`, matching the Phase 5 (#124) hook
convention. Always exits 0: this is bookkeeping, and a bookkeeping failure must
never block a tool call (HC-3.3 / HC-5.5 fail-open).
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

_HOOK_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _HOOK_DIR.parent.parent
_SHARED = _REPO_ROOT / ".agents" / "shared"
STATE_ROOT = Path(os.environ.get("GOVERNOR_STATE_ROOT", str(_REPO_ROOT)))
STATE_DIR = STATE_ROOT / ".claude" / "state"

if str(_SHARED) not in sys.path:
    sys.path.insert(0, str(_SHARED))

try:
    from governor import append_verify_log  # noqa: E402 — sys.path adjusted above

    _SHARED_OK = True
except Exception:  # noqa: BLE001 — HC-5.5 fail-open
    _SHARED_OK = False

    def append_verify_log(*_args, **_kwargs):  # type: ignore[misc]
        return None


# Cached at import — collision-resistant even if a PID is reused.
_PROCESS_START_NS = time.monotonic_ns()


def session_id(payload: dict | None = None) -> str:
    """Stable id for one Claude Code session.

    Priority mirrors the Codex adapter's: the value the harness injects, then
    an env fallback, then a process-derived id. The payload wins because Claude
    Code puts `session_id` in every hook payload, which is the only source that
    is identical across the several hook processes a session spawns.
    """
    if payload:
        from_payload = payload.get("session_id")
        if from_payload:
            return str(from_payload)
    explicit = os.environ.get("CLAUDE_CODE_HOST_SESSION_ID") or os.environ.get(
        "CLAUDE_SESSION_ID"
    )
    if explicit:
        return explicit
    return f"{os.getppid()}-{os.getpid()}-{_PROCESS_START_NS:016x}"


def extract_command(payload: dict) -> str | None:
    """Pull the shell command out of a PostToolUse Bash payload."""
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return None
    command = tool_input.get("command")
    return command if isinstance(command, str) and command.strip() else None


def main() -> int:
    if not _SHARED_OK:
        return 0
    try:
        payload = json.load(sys.stdin)
    except Exception:  # noqa: BLE001 — malformed payload is not our problem
        return 0
    if not isinstance(payload, dict):
        return 0

    command = extract_command(payload)
    if command is None:
        return 0

    try:
        append_verify_log(command, STATE_DIR, session_id(payload))
    except Exception:  # noqa: BLE001 — HC-3.3, never block a tool call
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
