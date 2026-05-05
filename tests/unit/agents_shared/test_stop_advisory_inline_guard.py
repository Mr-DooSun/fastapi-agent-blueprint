"""Static guards for PR-A.5 sync-advisory thin-shim refactor.

After PR-A.5, the Codex stop-sync-reminder hook must delegate classification
logic to governor.sync_advisory rather than redeclaring FOUNDATION_PREFIXES /
STRUCTURE_MARKERS inline.

Guards:
  1. FOUNDATION_PREFIXES tuple not defined inline in the hook.
  2. STRUCTURE_MARKERS tuple not defined inline in the hook.
  3. Hook imports classify_advisory from governor.sync_advisory (not facade).
  4. No getattr(governor, ...) bypass in the hook.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

_HOOK = REPO_ROOT / ".codex" / "hooks" / "stop-sync-reminder.py"


def _text() -> str:
    return _HOOK.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 1. FOUNDATION_PREFIXES not defined inline
# ---------------------------------------------------------------------------


def test_no_inline_foundation_prefixes() -> None:
    text = _text()
    # Must NOT define the tuple as a local name
    assert "FOUNDATION_PREFIXES = (" not in text, (
        f"{_HOOK.name}: FOUNDATION_PREFIXES defined inline. "
        "Move to governor.sync_advisory — hook must be a thin shim."
    )


# ---------------------------------------------------------------------------
# 2. STRUCTURE_MARKERS not defined inline
# ---------------------------------------------------------------------------


def test_no_inline_structure_markers() -> None:
    text = _text()
    assert "STRUCTURE_MARKERS = (" not in text, (
        f"{_HOOK.name}: STRUCTURE_MARKERS defined inline. "
        "Move to governor.sync_advisory — hook must be a thin shim."
    )


# ---------------------------------------------------------------------------
# 3. Hook imports from governor.sync_advisory submodule
# ---------------------------------------------------------------------------


def test_imports_from_sync_advisory_submodule() -> None:
    text = _text()
    assert "from governor.sync_advisory import" in text, (
        f"{_HOOK.name}: does not import from governor.sync_advisory. "
        "Classification must delegate to the shared submodule."
    )


# ---------------------------------------------------------------------------
# 4. No getattr(governor, ...) bypass
# ---------------------------------------------------------------------------


def test_no_getattr_governor_bypass() -> None:
    text = _text()
    assert "getattr(governor," not in text, (
        f"{_HOOK.name}: getattr(governor, ...) pattern detected. "
        "Use explicit submodule imports instead."
    )
