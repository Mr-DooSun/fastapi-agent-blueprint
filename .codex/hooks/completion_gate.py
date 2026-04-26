"""Completion-gate helper (Codex side, Phase 4 of #117 / #123).

Imported by `.codex/hooks/stop-sync-reminder.py` inside a
``with contextlib.suppress(Exception):`` block (IC-2 single Stop event):
    seg = completion_gate.governor_changing_segment()
    if seg:
        segments.append(seg)
    completion_gate.consume_phase2_markers(STATE_DIR)
    completion_gate.cleanup_stale_verify_logs(STATE_DIR)

Responsibilities (Codex side):
1. Pillar 7 — same as Claude side: reminder when changed files intersect
   governor-paths.md Tier A/B/C globs without a matching log entry.
2. Phase 2 marker lifecycle — read-and-delete (IC-11 Option A).
3. Stale verify-log cleanup — opportunistic 24h cleanup of OTHER sessions'
   verify-log-*.json files (current session's log is preserved).

IC-10: Tier A/B/C globs parsed from governor-paths.md (never inline).
Fail-open per HC-4.7.
"""

from __future__ import annotations

import contextlib
import fnmatch
import json
import re
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path

from _shared import REPO_ROOT, changed_files
from verify_first import EXPLORATION_TOKENS, session_id

STATE_DIR = REPO_ROOT / ".codex" / "state"
GOVERNOR_PATHS_MD = REPO_ROOT / "docs" / "ai" / "shared" / "governor-paths.md"
GOVERNOR_REVIEW_LOG_PREFIX = "docs/ai/shared/governor-review-log/"

# IC-2: string-equal to `.claude/hooks/completion_gate.py` constants.
# Parity asserted by tests/unit/agents_shared/test_completion_gate.py.
GOVERNOR_REMINDER_WITH_PR = "\n".join(
    [
        "[completion-gate] governor-changing 변경이 감지됨 (Pillar 7).",
        "[completion-gate] Governor-changing changes detected (Pillar 7).",
        "PR #{pr}에 매칭되는 governor-review-log 항목이 없습니다.",
        "Expected: docs/ai/shared/governor-review-log/pr-{pr}-<slug>.md",
        "See: docs/ai/shared/governor-review-log/README.md",
    ]
)

GOVERNOR_REMINDER_NO_PR = "\n".join(
    [
        "[completion-gate] governor-changing 변경이 감지됨 (Pillar 7).",
        "[completion-gate] Governor-changing changes detected (Pillar 7).",
        "PR 번호 미확인 — PR 생성 후 governor-review-log/ 항목을 추가하세요.",
        "See: docs/ai/shared/governor-review-log/README.md",
    ]
)


def _within_24h(ts: str) -> bool:
    try:
        dt = datetime.fromisoformat(ts.rstrip("Z")).replace(tzinfo=UTC)
        return (datetime.now(tz=UTC) - dt).total_seconds() < 86400
    except Exception:
        return True


def _read_latest_token(state_dir: Path) -> str | None:
    if not state_dir.exists():
        return None
    candidates: list[tuple[str, str]] = []
    for path in state_dir.glob("exception-token-*.json"):
        with contextlib.suppress(Exception):
            record = json.loads(path.read_text(encoding="utf-8"))
            ts = record.get("ts")
            token = record.get("token")
            if isinstance(ts, str) and isinstance(token, str) and _within_24h(ts):
                candidates.append((ts, token))
    return max(candidates, key=lambda x: x[0])[1] if candidates else None


def parse_trigger_globs(md_path: Path = GOVERNOR_PATHS_MD) -> list[str]:
    """Extract Tier A/B/C glob patterns from governor-paths.md bullet lists."""
    try:
        text = md_path.read_text(encoding="utf-8")
    except OSError:
        return []
    globs: list[str] = []
    in_tier = False
    for line in text.splitlines():
        if re.match(r"^### Tier [ABC]", line):
            in_tier = True
            continue
        if in_tier and re.match(r"^##", line):
            in_tier = False
            continue
        if in_tier and line.strip().startswith("-"):
            m = re.search(r"`([^`]+)`", line)
            if m:
                globs.append(m.group(1))
    return globs


def _matches_glob(path: str, glob: str) -> bool:
    if "**" in glob:
        prefix = glob.split("**")[0]
        return path.startswith(prefix)
    return fnmatch.fnmatch(path, glob)


def is_log_only_backfill(changed: list[str]) -> bool:
    return bool(changed) and all(
        p.startswith(GOVERNOR_REVIEW_LOG_PREFIX) for p in changed
    )


def is_governor_changing(changed: list[str], globs: list[str]) -> bool:
    return any(_matches_glob(p, g) for p in changed for g in globs)


def pr_number_from_branch() -> int | None:
    try:
        result = subprocess.run(  # noqa: S603
            ["gh", "pr", "view", "--json", "number"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return int(data["number"])
    except Exception:  # noqa: BLE001,S110 — fail-open per HC-4.7
        pass
    return None


def match_log_entry(changed: list[str], current_pr: int | None) -> str:
    """Classify governor-review-log entry presence vs the current PR number.

    Returns "match", "mismatch", "missing", or "unknown" (no PR, some entry).
    """
    log_entries = [p for p in changed if re.search(r"governor-review-log/pr-\d+-", p)]
    if not log_entries:
        return "missing"
    if current_pr is None:
        return "unknown"
    for entry in log_entries:
        m = re.search(r"governor-review-log/pr-(\d+)-", entry)
        if m and int(m.group(1)) == current_pr:
            return "match"
    return "mismatch"


def consume_phase2_markers(state_dir: Path = STATE_DIR) -> None:
    """Delete all Phase 2 exception-token markers (IC-11 Option A)."""
    if not state_dir.exists():
        return
    for path in state_dir.glob("exception-token-*.json"):
        with contextlib.suppress(Exception):
            path.unlink()


def cleanup_stale_verify_logs(state_dir: Path = STATE_DIR) -> None:
    """Delete verify-log-*.json files older than 24h from OTHER sessions."""
    if not state_dir.exists():
        return
    current_name = f"verify-log-{session_id()}.json"
    cutoff = time.time() - 86400
    for path in state_dir.glob("verify-log-*.json"):
        if path.name == current_name:
            continue
        with contextlib.suppress(Exception):
            if path.stat().st_mtime < cutoff:
                path.unlink()


def governor_changing_segment() -> str | None:
    """Return a Pillar 7 reminder string, or None if not applicable."""
    try:
        ch = changed_files()
        if not ch:
            return None

        if is_log_only_backfill(ch):
            return None

        token = _read_latest_token(STATE_DIR)
        if token in EXPLORATION_TOKENS:
            return None

        globs = parse_trigger_globs()
        if not globs or not is_governor_changing(ch, globs):
            return None

        current_pr = pr_number_from_branch()
        status = match_log_entry(ch, current_pr)

        if status == "match":
            return None

        if status == "unknown":
            return None

        if current_pr is None:
            return GOVERNOR_REMINDER_NO_PR

        return GOVERNOR_REMINDER_WITH_PR.format(pr=current_pr)
    except Exception:
        return None
