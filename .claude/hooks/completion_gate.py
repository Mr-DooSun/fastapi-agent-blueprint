"""Completion-gate helper (Phase 4 of #117 / #123).

Called by `.claude/hooks/stop-sync-reminder.sh`:
    COMPLETION_OUT=$(python3 "$(dirname "$0")/completion_gate.py" 2>/dev/null || true)

Responsibilities (Claude side):
1. Pillar 7 — emit reminder to stdout when changed files intersect
   governor-paths.md Tier A/B/C globs without a matching
   docs/ai/shared/governor-review-log/pr-{N}-*.md entry being created.
2. Phase 2 marker lifecycle — read-and-delete all exception-token-*.json
   in STATE_DIR (IC-11 Option A). Markers older than 24h are also skipped
   by the reader as a defensive measure against Stop-failure leftovers.

IC-10: governor-paths.md Tier A/B/C globs are never declared inline here;
they are parsed from the canonical markdown source.

Fail-open per HC-4.7: any unexpected error → silent, exit 0.
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

REPO_ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = REPO_ROOT / ".claude" / "state"
GOVERNOR_PATHS_MD = REPO_ROOT / "docs" / "ai" / "shared" / "governor-paths.md"
GOVERNOR_REVIEW_LOG_PREFIX = "docs/ai/shared/governor-review-log/"

EXPLORATION_TOKENS = frozenset({"exploration", "탐색"})

# IC-2: string-equal to `.codex/hooks/completion_gate.py` constants.
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


def _run_git(*args: str) -> str:
    result = subprocess.run(  # noqa: S603
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout if result.returncode == 0 else ""


def _changed_files() -> list[str]:
    """Uncommitted changes (staged + unstaged) + untracked, with 2h commit fallback."""
    uncommitted = _run_git("diff", "--name-only", "HEAD")
    untracked = _run_git("ls-files", "--others", "--exclude-standard")
    combined = sorted(
        {
            line
            for chunk in (uncommitted, untracked)
            for line in chunk.splitlines()
            if line
        }
    )
    if combined:
        return combined
    with contextlib.suppress(Exception):
        last_epoch = int(_run_git("log", "-1", "--format=%ct").strip() or "0")
        if time.time() - last_epoch < 7200:
            last_commit = _run_git("diff", "--name-only", "HEAD~1", "HEAD")
            return [line for line in last_commit.splitlines() if line]
    return []


def _within_24h(ts: str) -> bool:
    """Return True if ISO 8601 UTC timestamp is within the last 24 hours."""
    try:
        dt = datetime.fromisoformat(ts.rstrip("Z")).replace(tzinfo=UTC)
        return (datetime.now(tz=UTC) - dt).total_seconds() < 86400
    except Exception:
        return True  # fail-open: include timestamps we can't parse


def _read_latest_token(state_dir: Path) -> str | None:
    """Return the most-recent non-stale Phase 2 marker token, or None."""
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
    """Match a repo-relative path against a governor-paths.md glob pattern."""
    if "**" in glob:
        prefix = glob.split("**")[0]
        return path.startswith(prefix)
    return fnmatch.fnmatch(path, glob)


def is_log_only_backfill(changed: list[str]) -> bool:
    """True when ALL changed files are under the governor-review-log dir (HC-4.5)."""
    return bool(changed) and all(
        p.startswith(GOVERNOR_REVIEW_LOG_PREFIX) for p in changed
    )


def is_governor_changing(changed: list[str], globs: list[str]) -> bool:
    return any(_matches_glob(p, g) for p in changed for g in globs)


def pr_number_from_branch() -> int | None:
    """Return current PR number via gh CLI, or None on any failure."""
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

    Returns:
      "match"   — entry pr-{current_pr}-*.md present in changed
      "mismatch"— entry with different N present (current_pr known)
      "missing" — no entry present in changed at all
      "unknown" — current_pr is None but some entry exists
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
    """Delete all Phase 2 exception-token markers (IC-11 Option A: read-and-delete).

    Called AFTER the token has been read by governor_changing_segment and
    (on Codex side) by verify_first.should_remind. All reads in this Stop
    event happen before this delete, so no reader sees a missing file.
    """
    if not state_dir.exists():
        return
    for path in state_dir.glob("exception-token-*.json"):
        with contextlib.suppress(Exception):
            path.unlink()


def governor_changing_segment() -> str | None:
    """Return a Pillar 7 reminder string, or None if not applicable."""
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

    if status == "match":
        return None

    if status == "unknown":
        # PR not created yet but some log entry staged — assume user will rename.
        return None

    if current_pr is None:
        # status == "missing", no PR created, no log entry
        return GOVERNOR_REMINDER_NO_PR

    # status in ("missing", "mismatch") with known PR number
    return GOVERNOR_REMINDER_WITH_PR.format(pr=current_pr)


def main() -> int:
    try:
        reminder: str | None = None
        with contextlib.suppress(Exception):
            reminder = governor_changing_segment()

        with contextlib.suppress(Exception):
            consume_phase2_markers()

        if reminder:
            print(reminder)
    except Exception:  # noqa: BLE001,S110 — fail-open per HC-4.7
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
