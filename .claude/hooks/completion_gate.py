"""Completion-gate helper (Phase 5 of #117 / #124) — thin shim.

Called by ``.claude/hooks/stop-sync-reminder.sh``:
    COMPLETION_OUT=$(python3 "$(dirname "$0")/completion_gate.py" 2>/dev/null || true)

Phase 5 consolidates governor *policy* (reminder templates, glob parsing,
match-log classification, marker lifecycle) into ``.agents/shared/governor``.
This shim orchestrates the Claude-side flow and exposes the same
attributes the existing test suite monkeypatches (``_changed_files``,
``_read_latest_token``, ``pr_number_from_branch``, ``STATE_DIR``, etc.).

IC-10 preserved: ``parse_trigger_globs`` is imported from the shared
module — no inline glob declarations here.
HC-5.5: shared import failure → silent ``main()`` return-0.
Module-level invariant (Plan §D3): no top-level ``sys.exit``.
"""

from __future__ import annotations

import contextlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = REPO_ROOT / ".claude" / "state"
GOVERNOR_PATHS_MD = REPO_ROOT / "docs" / "ai" / "shared" / "governor-paths.md"
GOVERNOR_REVIEW_LOG_PREFIX = "docs/ai/shared/governor-review-log/"

_SHARED = REPO_ROOT / ".agents" / "shared"
if str(_SHARED) not in sys.path:
    sys.path.insert(0, str(_SHARED))

try:
    from governor import (  # noqa: E402 — sys.path adjusted above
        EXPLORATION_TOKENS,
        GOVERNOR_REMINDER_NO_PR,
        GOVERNOR_REMINDER_WITH_PR,
        MarkerLifecycle,
        _within_24h,
        is_governor_changing,
        is_log_only_backfill,
        match_log_entry,
        parse_trigger_globs,
        pr_number_from_branch,
    )
    from governor import changed_files_via_git as _shared_changed_files  # noqa: E402
    from governor import (  # noqa: E402
        consume_phase2_markers as _shared_consume_phase2_markers,
    )
    from governor import read_latest_token as _shared_read_latest_token  # noqa: E402
    from governor.completion_gate import _matches_glob  # noqa: E402

    _SHARED_OK = True
except Exception:  # noqa: BLE001 — HC-5.5 fail-open
    EXPLORATION_TOKENS = frozenset()
    GOVERNOR_REMINDER_WITH_PR = ""
    GOVERNOR_REMINDER_NO_PR = ""
    MarkerLifecycle = None  # type: ignore[assignment,misc]
    _shared_read_latest_token = None
    _shared_consume_phase2_markers = None
    _shared_changed_files = None
    _SHARED_OK = False

    def _within_24h(ts: str) -> bool:  # type: ignore[no-redef]
        return True

    def parse_trigger_globs(md_path: Path = GOVERNOR_PATHS_MD) -> list[str]:  # type: ignore[no-redef]
        return []

    def _matches_glob(path: str, glob: str) -> bool:  # type: ignore[no-redef]
        return False

    def is_log_only_backfill(changed: list[str]) -> bool:  # type: ignore[no-redef]
        return False

    def is_governor_changing(  # type: ignore[no-redef]
        changed: list[str], globs: list[str]
    ) -> bool:
        return False

    def match_log_entry(  # type: ignore[no-redef]
        changed: list[str], current_pr: int | None
    ) -> str:
        return "missing"

    def pr_number_from_branch() -> int | None:  # type: ignore[no-redef]
        return None


def _changed_files() -> list[str]:
    """Module-level wrapper so tests can monkeypatch ``_changed_files``."""

    if _shared_changed_files is None:
        return []
    return _shared_changed_files(REPO_ROOT)


def _read_latest_token(state_dir: Path) -> str | None:
    """Module-level wrapper so tests can monkeypatch ``_read_latest_token``."""

    if not _SHARED_OK or _shared_read_latest_token is None or MarkerLifecycle is None:
        return None
    return _shared_read_latest_token(state_dir, MarkerLifecycle.READ_ONLY)


def consume_phase2_markers(state_dir: Path = STATE_DIR) -> None:
    """Module-level wrapper so tests can call without explicit import."""

    if not _SHARED_OK or _shared_consume_phase2_markers is None:
        return
    _shared_consume_phase2_markers(state_dir)


def governor_changing_segment() -> str | None:
    """Pillar 7 reminder, manually orchestrated so module attrs stay
    monkeypatchable for the existing test suite."""

    if not _SHARED_OK:
        return None
    try:
        changed = _changed_files()
        if not changed:
            return None
        if is_log_only_backfill(changed):
            return None
        token = _read_latest_token(STATE_DIR)
        if token in EXPLORATION_TOKENS:
            return None
        globs = parse_trigger_globs()
        if not globs or not is_governor_changing(changed, globs):
            return None
        current_pr = pr_number_from_branch()
        status = match_log_entry(changed, current_pr)
        if status in ("match", "unknown"):
            return None
        if current_pr is None:
            return GOVERNOR_REMINDER_NO_PR
        return GOVERNOR_REMINDER_WITH_PR.format(pr=current_pr)
    except Exception:  # noqa: BLE001 — HC-5.5 fail-open
        return None


def main() -> int:
    if not _SHARED_OK:
        return 0
    try:
        reminder: str | None = None
        with contextlib.suppress(Exception):
            reminder = governor_changing_segment()
        with contextlib.suppress(Exception):
            consume_phase2_markers()
        if reminder:
            print(reminder)
    except Exception:  # noqa: BLE001 — HC-5.5 fail-open
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
