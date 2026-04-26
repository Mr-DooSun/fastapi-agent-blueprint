"""Cascade-defence tests (Phase 5 #124, R0-C.3).

Phase 5 is the last phase of #117. After it ships, future contributors
must add new governor assets *to the shared module*, not back into
hooks. These tests defend that boundary:

1. ``__all__`` stability — removing a public name from
   ``governor.__all__`` requires a deliberate test update, not a silent
   drop. Adding new names is fine and does not break this test.
2. Inline glob redeclaration ban (IC-10) — hook scripts MUST NOT
   declare governor-paths.md globs inline; they must call
   ``parse_trigger_globs`` from the shared module.
3. Inline reminder redeclaration ban — hook scripts MUST NOT carry the
   canonical Korean reminder lines anymore; they must import
   ``REMINDER_TEXT`` / ``GOVERNOR_REMINDER_*`` from the shared module.
"""

from __future__ import annotations

from pathlib import Path

import governor

REPO_ROOT = Path(__file__).resolve().parents[3]


# ---------------------------------------------------------------------------
# 1. __all__ stability
# ---------------------------------------------------------------------------
EXPECTED_ALL = {
    "Blocked",
    "EXPLORATION_TOKENS",
    "GOVERNOR_PATHS_MD",
    "GOVERNOR_REMINDER_NO_PR",
    "GOVERNOR_REMINDER_WITH_PR",
    "GOVERNOR_REVIEW_LOG_PREFIX",
    "GateResult",
    "MarkerLifecycle",
    "PROMPT_RULES",
    "ParsedToken",
    "REMINDER_TEXT",
    "REPO_ROOT",
    "SafeParseResult",
    "TOKEN_REGEX",
    "_within_24h",
    "changed_files_via_git",
    "check_safety",
    "consume_phase2_markers",
    "evaluate_gate",
    "extract_file_path",
    "governor_changing_segment",
    "is_governor_changing",
    "is_log_only_backfill",
    "is_python_source",
    "match_log_entry",
    "parse_exception_token",
    "parse_trigger_globs",
    "pr_number_from_branch",
    "read_latest_token",
    "render_reminder",
    "safe_parse_exception_token",
    "should_remind_claude",
    "write_marker",
}


def test_governor_all_does_not_drop_known_names() -> None:
    """If you remove a name from __all__, update this test deliberately.
    Adding new names is allowed and does not break this assertion."""

    actual = set(governor.__all__)
    missing = EXPECTED_ALL - actual
    assert not missing, (
        f"governor.__all__ dropped names: {missing}. "
        "If intentional, update EXPECTED_ALL with rationale."
    )


def test_governor_all_names_are_actually_exported() -> None:
    """Every name in __all__ must resolve to an attribute of the package."""

    for name in governor.__all__:
        assert hasattr(governor, name), f"{name} declared in __all__ but missing"


# ---------------------------------------------------------------------------
# 2. IC-10 — no inline governor-paths.md glob redeclaration in hooks
# ---------------------------------------------------------------------------
HOOK_FILES = [
    REPO_ROOT / ".claude" / "hooks" / "user_prompt_submit.py",
    REPO_ROOT / ".claude" / "hooks" / "verify_first.py",
    REPO_ROOT / ".claude" / "hooks" / "completion_gate.py",
    REPO_ROOT / ".codex" / "hooks" / "user-prompt-submit.py",
    REPO_ROOT / ".codex" / "hooks" / "verify_first.py",
    REPO_ROOT / ".codex" / "hooks" / "completion_gate.py",
]


def test_hooks_do_not_redeclare_governor_paths_globs() -> None:
    """Hooks must call ``parse_trigger_globs`` from the shared module.
    Inline glob lists (``.claude/**``, ``.codex/**``, ``AGENTS.md`` as a
    bareword glob assignment) would break IC-10."""

    for hook in HOOK_FILES:
        text = hook.read_text(encoding="utf-8")
        # The hook may still mention ".claude/" / ".codex/" in path
        # discovery (REPO_ROOT / ".claude" / ...). What it MUST NOT do
        # is declare a glob list literal — heuristic: a backtick-quoted
        # path glob inside the hook body. Because docstring backticks
        # are still allowed, we only check for assignment patterns.
        forbidden_patterns = [
            "TIER_GLOBS = [",
            "GLOBS = [",
            "TRIGGER_GLOBS = [",
        ]
        for pat in forbidden_patterns:
            assert pat not in text, (
                f"{hook.name}: inline glob-list assignment '{pat}' violates IC-10"
            )


# ---------------------------------------------------------------------------
# 3. Inline reminder redeclaration ban (R0-C.3)
# ---------------------------------------------------------------------------
CANONICAL_KOREAN_LINES = [
    "PR #{pr}에 매칭되는 governor-review-log 항목이 없습니다.",
    "PR 번호 미확인 — PR 생성 후 governor-review-log/ 항목을 추가하세요.",
    "[verify-first] verify 단계가 누락된 것 같습니다. 변경된 .py 파일에 대해 테스트/검증을 권장합니다.",
]


def test_hooks_do_not_redeclare_canonical_reminder_lines() -> None:
    """Each canonical Korean reminder line must live ONLY in the shared
    module — hooks must import constants instead of duplicating strings."""

    for hook in HOOK_FILES:
        text = hook.read_text(encoding="utf-8")
        for line in CANONICAL_KOREAN_LINES:
            assert line not in text, (
                f"{hook.name} re-declares canonical reminder line:\n{line}\n"
                "Use governor.* import instead of inline literal."
            )


# ---------------------------------------------------------------------------
# 4. R2.2 — completion-gate shim must handle every GateStatus variant
# ---------------------------------------------------------------------------
COMPLETION_GATE_SHIMS = [
    REPO_ROOT / ".claude" / "hooks" / "completion_gate.py",
    REPO_ROOT / ".codex" / "hooks" / "completion_gate.py",
]


def test_gatestatus_variants_referenced_by_completion_gate_shims() -> None:
    """If a future contributor adds a new GateStatus variant, the shim's
    manual orchestration in ``governor_changing_segment`` must be
    updated to handle it. This test fails when the closed Literal grows
    a new variant that isn't reflected in the shim flow.

    Heuristic: every silent_* status maps to an early ``return None``
    branch in the shim; ``match`` / ``unknown`` collapse into the same
    silence; ``missing`` / ``mismatch`` produce a reminder. We therefore
    ensure each shim reads ``EXPLORATION_TOKENS`` (silent_exploration),
    calls ``is_log_only_backfill`` (silent_log_only), checks empty
    ``changed`` (silent_no_changes), calls ``is_governor_changing``
    (silent_not_governor), and gates on ``match_log_entry`` returning
    one of the four log-entry statuses.
    """

    from governor.completion_gate import GateStatus  # noqa: PLC0415

    # Variants that warrant explicit shim handling.
    expected_branch_signals = {
        "silent_no_changes": "if not",  # `if not changed: return None`
        "silent_log_only": "is_log_only_backfill",
        "silent_exploration": "EXPLORATION_TOKENS",
        "silent_not_governor": "is_governor_changing",
        "match": "match_log_entry",  # match/mismatch/missing/unknown share entry
    }
    # Sanity: GateStatus must contain every variant we expect to see.
    expected_variants = set(expected_branch_signals) | {
        "mismatch",
        "missing",
        "unknown",
    }
    actual_variants = set(GateStatus.__args__)  # type: ignore[attr-defined]
    assert actual_variants == expected_variants, (
        f"GateStatus variants changed: {actual_variants ^ expected_variants}. "
        "Update the shim flow in .{claude,codex}/hooks/completion_gate.py "
        "and refresh this test."
    )

    for shim in COMPLETION_GATE_SHIMS:
        text = shim.read_text(encoding="utf-8")
        for variant, signal in expected_branch_signals.items():
            assert signal in text, (
                f"{shim.name}: missing branch signal for GateStatus={variant!r} "
                f"(expected token {signal!r}). Add the corresponding silence "
                "or render path before introducing the new variant."
            )
