"""Stop-side verify-first helper (Phase 3 of #117 / #122).

Imported by `.codex/hooks/stop-sync-reminder.py` (segment merge — IC-2 single
Stop event output) and by `.codex/hooks/post-tool-format.py` (verify-log
writer on PostToolUse Bash). NOT registered as its own hook.

Read-only on Phase 2 markers (IC-11 from PR #126; Phase 4 #123 owns
lifecycle).

R0 reinforcement (post-Round-0 of PR #122):
- session_id includes pid + monotonic_ns to defeat PPID collisions across
  concurrent Codex sessions (R0.2).
- verify-log freshness reads ONLY current session's log file (R0.2 — defeats
  cross-session silence).
- Timestamps stored as `ts_epoch_ns: int` (`time.time_ns()`) and compared
  against `Path.stat().st_mtime_ns`; subsecond precision preserves
  ordering when pytest and an edit land in the same wall-clock second
  (R0.3).

R1 reinforcement (post-Round-1 of PR #127):
- session_id prefers CODEX_THREAD_ID (injected by Codex CLI into ALL hook
  processes in a session — same value for PostToolUse writer and Stop reader).
  Falls back to CODEX_SESSION_ID, then to ppid-pid-startns. The ppid-pid-startns
  fallback is writer/reader-incompatible (each hook process has a different PID
  and startns) but is preserved for non-Codex test environments (R1.1).

REMINDER_TEXT is frozen at Phase 3 and string-equal to
`.claude/hooks/verify_first.py` REMINDER_TEXT.
"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

from _shared import REPO_ROOT, changed_files

STATE_DIR = REPO_ROOT / ".codex" / "state"

EXPLORATION_TOKENS = frozenset({"exploration", "탐색"})

REMINDER_TEXT = "\n".join(
    [
        "[verify-first] verify 단계가 누락된 것 같습니다. 변경된 .py 파일에 대해 테스트/검증을 권장합니다.",
        "[verify-first] Verify step appears to be missing for the changed .py files.",
        "Suggested next: `/test-domain run <domain>` (or `pytest tests/unit/<domain>/`)",
        "Silence with `[exploration]` / `[탐색]` prefix when intentionally exploring.",
    ]
)

VERIFY_PATTERNS = (
    r"\bpytest\b",
    r"\bmake\s+test\b",
    r"\bmake\s+demo(?:-rag)?\b",
    r"\balembic\s+upgrade\b",
)

# Cached at module import — collision-resistant suffix even if PPID is reused.
_PROCESS_START_NS = time.monotonic_ns()


def session_id() -> str:
    """Stable id within one Codex CLI invocation.

    Priority: CODEX_THREAD_ID (Codex-injected, same across all hook processes in
    a session — R1.1) → CODEX_SESSION_ID (fallback alias) → ppid-pid-startns
    (non-Codex environments only; writer/reader-incompatible in live Codex).
    """
    explicit = os.environ.get("CODEX_THREAD_ID") or os.environ.get("CODEX_SESSION_ID")
    if explicit:
        return explicit
    return f"{os.getppid()}-{os.getpid()}-{_PROCESS_START_NS:016x}"


def verify_log_path(state_dir: Path = STATE_DIR) -> Path:
    return state_dir / f"verify-log-{session_id()}.json"


def append_verify_log(command: str, state_dir: Path = STATE_DIR) -> Path | None:
    """Append a verify-class command record to current-session JSONL.

    Append-only (race-safe across concurrent Codex sessions writing different
    files). Records both ``ts`` (ISO 8601 UTC for human reading) and
    ``ts_epoch_ns`` (int for subsecond freshness comparison — R0.3).
    Returns the log path on append, or None if the command does not match
    any verify pattern.
    """
    if not any(re.search(pattern, command) for pattern in VERIFY_PATTERNS):
        return None
    state_dir.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "ts_epoch_ns": time.time_ns(),
        "cmd": command,
    }
    path = verify_log_path(state_dir)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path


def current_session_latest_verify_ns(state_dir: Path = STATE_DIR) -> int | None:
    """Most-recent verify-class entry in the CURRENT session's log only.

    Reads `verify-log-{session_id()}.json` exclusively — does not glob other
    sessions. Defeats cross-session silence (R0.2). Returns the largest
    ``ts_epoch_ns`` integer, or ``None`` if the file is missing / empty /
    every line malformed.
    """
    path = verify_log_path(state_dir)
    if not path.exists():
        return None
    latest: int | None = None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        ns = record.get("ts_epoch_ns")
        if isinstance(ns, int) and (latest is None or ns > latest):
            latest = ns
    return latest


def read_latest_token_marker(state_dir: Path) -> str | None:
    """Return token of the most-recent valid Phase 2 marker, or None.

    Same contract as `.claude/hooks/verify_first.py.read_latest_token_marker`.
    Duplicated until Phase 5 (#124) consolidates into
    `.agents/shared/governor/`.
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


def changed_python_files() -> list[str]:
    return [p for p in changed_files() if p.endswith(".py")]


def max_changed_py_mtime_ns(repo_root: Path = REPO_ROOT) -> int | None:
    """Largest ``st_mtime_ns`` across changed `.py` files.

    Uses ``stat().st_mtime_ns`` directly so subsecond ordering is preserved
    (R0.3). Returns ``None`` when no changed `.py` exists or when every
    file disappeared between ``git status`` and the stat (race).
    """
    paths = changed_python_files()
    mtimes_ns: list[int] = []
    for relative in paths:
        full = repo_root / relative
        try:
            mtimes_ns.append(full.stat().st_mtime_ns)
        except OSError:
            continue
    if not mtimes_ns:
        return None
    return max(mtimes_ns)


def should_remind() -> bool:
    """Codex-side decision. ``False`` = silent, ``True`` = emit reminder.

    Logic:
      1. No changed `.py` → silent.
      2. Latest Phase 2 marker is `[exploration]`/`[탐색]` → silent.
      3. Current session has a verify-class log entry whose
         ``ts_epoch_ns`` ≥ the largest changed-`.py` ``st_mtime_ns`` →
         silent (verification is fresh enough).
      4. Otherwise → emit reminder.
    """
    if not changed_python_files():
        return False
    token = read_latest_token_marker(REPO_ROOT / ".codex" / "state")
    if token in EXPLORATION_TOKENS:
        return False
    verify_ns = current_session_latest_verify_ns()
    if verify_ns is None:
        return True
    py_mtime_ns = max_changed_py_mtime_ns()
    if py_mtime_ns is None:
        return True
    # Stale verify when log is older than the most recent .py edit.
    return verify_ns < py_mtime_ns
