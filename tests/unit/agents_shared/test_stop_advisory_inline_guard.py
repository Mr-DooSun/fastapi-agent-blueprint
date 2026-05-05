"""Static guards and fail-open behavioral tests for PR-A.5.

After PR-A.5, the Codex stop-sync-reminder hook must delegate classification
logic to governor.sync_advisory rather than redeclaring FOUNDATION_PREFIXES /
STRUCTURE_MARKERS inline.

Guards:
  1. FOUNDATION_PREFIXES tuple not defined inline in the hook.
  2. STRUCTURE_MARKERS tuple not defined inline in the hook.
  3. Hook imports classify_advisory from governor.sync_advisory (not facade).
  4. No getattr(governor, ...) bypass in the hook.

Behavioral tests:
  5. When _SYNC_OK=False (import failed), build_segments must not emit any
     sync advisory segment (HC-5.5 fail-open — IC-19 always-fallback does
     not apply when the import itself failed).
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[3]
_CODEX_HOOKS = REPO_ROOT / ".codex" / "hooks"


def _load_module(name: str, path: Path) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _load_codex_stop_sync() -> types.ModuleType:
    """Load stop-sync-reminder.py with the Codex _shared shim pre-installed."""
    saved_shared = sys.modules.pop("_shared", None)
    saved_mod = sys.modules.pop("_codex_stop_sync_advisory_test", None)
    try:
        _load_module("_shared", _CODEX_HOOKS / "_shared.py")
        return _load_module(
            "_codex_stop_sync_advisory_test",
            _CODEX_HOOKS / "stop-sync-reminder.py",
        )
    finally:
        for name, saved in (
            ("_shared", saved_shared),
            ("_codex_stop_sync_advisory_test", saved_mod),
        ):
            if saved is not None:
                sys.modules[name] = saved
            else:
                sys.modules.pop(name, None)


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


# ---------------------------------------------------------------------------
# 5. Fail-open: _SYNC_OK=False → no sync advisory segment (HC-5.5)
# ---------------------------------------------------------------------------


def test_sync_ok_false_no_advisory_segment() -> None:
    """When _SYNC_OK is False, build_segments must not emit a sync advisory.

    Simulates the HC-5.5 path where governor.sync_advisory failed to import.
    build_segments must still return without error (fail-open), but the
    advisory text must be absent from all returned segments.
    """
    m = _load_codex_stop_sync()
    with (
        patch.object(m, "_SYNC_OK", False),
        patch.object(m, "_classify_advisory", None),
    ):
        segments = m.build_segments(changed=["src/_core/x.py"])

    advisory_markers = (
        "Guideline sync required before closing this work.",
        "Foundation files changed:",
        "Guideline sync recommended.",
        "Domain structure files changed:",
    )
    for seg in segments:
        for marker in advisory_markers:
            assert marker not in seg, (
                f"Sync advisory appeared despite _SYNC_OK=False: {marker!r} found in segment"
            )
