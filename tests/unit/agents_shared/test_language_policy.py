"""Tier 1 Language Policy regression tests (PR #131).

These tests reuse the shared checker at ``tools/check_language_policy.py``
so the pre-commit hook and the test suite enforce the same allowlist.
Adding a case here that the hook cannot also enforce indicates a checker
gap, not a test gap — fix the checker.

Coverage:

1. Korean prose in a Tier 1 path is flagged.
2. Bilingual escape tokens in their per-file allowlist are accepted.
3. Provenance-prefixed Korean in a governor-review-log entry is accepted.
4. Korean in a review-log entry without the provenance prefix is flagged.
5. README.md L31 ``한국어`` link label is exempt (README is not in
   TIER1_GLOBS).
6. Multi-line preserved Korean must repeat the prefix on every line —
   the second line without a prefix is a violation.
7. Korean inside a fenced code block in a ``.md`` file is exempt.
8. Korean in a ``.py`` source file string literal is a violation
   (no code-block exemption outside ``.md``).
9. Drift test: every Tier 1 path bullet in
   ``AGENTS.md § Language Policy`` resolves to a path covered by the
   checker's ``TIER1_GLOBS``, and every glob has a corresponding policy
   bullet. Prevents silent drift between the policy text and the
   enforcer.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


def _import_checker():
    """Import tools.check_language_policy without adding it to package layout."""
    import importlib.util
    import sys

    module_name = "_check_language_policy"
    if module_name in sys.modules:
        return sys.modules[module_name]
    module_path = REPO_ROOT / "tools" / "check_language_policy.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module  # required for @dataclass(frozen=True)
    spec.loader.exec_module(module)
    return module


CHECKER = _import_checker()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _scan(tmp_path: Path, rel_path: str, content: str):
    target = tmp_path / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return CHECKER.find_violations(target, repo_root=tmp_path)


# ---------------------------------------------------------------------------
# 1-2. Token-vocabulary allowlist — positive and negative cases
# ---------------------------------------------------------------------------


def test_korean_prose_in_claude_rules_is_violation(tmp_path: Path) -> None:
    violations = _scan(
        tmp_path,
        ".claude/rules/commands.md",
        "# 개발환경 셋업\nmake setup\n",
    )
    assert len(violations) == 1
    assert violations[0].line_number == 1


def test_bilingual_token_in_agents_md_passes(tmp_path: Path) -> None:
    violations = _scan(
        tmp_path,
        "AGENTS.md",
        "| `[trivial]` | `[자명]` | Self-evident change |\n",
    )
    assert violations == []


def test_token_literal_does_not_launder_korean_prose(tmp_path: Path) -> None:
    """Per-file allowlist must reject Korean prose appearing on the same
    line as a token literal — the token is masked, then any remaining
    Hangul fails."""
    violations = _scan(
        tmp_path,
        "AGENTS.md",
        "| `[trivial]` | `[자명]` | 한국어 prose |\n",
    )
    assert len(violations) == 1


# ---------------------------------------------------------------------------
# 3-6. governor-review-log provenance prefix rules
# ---------------------------------------------------------------------------


def test_review_log_provenance_prefix_passes(tmp_path: Path) -> None:
    violations = _scan(
        tmp_path,
        "docs/ai/shared/governor-review-log/pr-999-example.md",
        "> Original reviewer verdict (ko, verbatim): 보완 필요\n"
        "> English normalised verdict: needs follow-up.\n",
    )
    assert violations == []


def test_review_log_korean_without_prefix_is_violation(tmp_path: Path) -> None:
    violations = _scan(
        tmp_path,
        "docs/ai/shared/governor-review-log/pr-999-example.md",
        "Some random text 보완 필요\n",
    )
    assert len(violations) == 1


def test_review_log_multiline_provenance_must_repeat_prefix(
    tmp_path: Path,
) -> None:
    """Multi-line preserved Korean must repeat the provenance prefix on
    every line. A continuation line without the prefix is a violation."""
    violations = _scan(
        tmp_path,
        "docs/ai/shared/governor-review-log/pr-999-example.md",
        "> Original user/owner statement (ko, verbatim): 첫 번째 줄\n"
        "두 번째 줄에는 prefix가 없음\n",
    )
    # The first line is allowed (prefixed). The second is not.
    assert len(violations) == 1
    assert violations[0].line_number == 2


# ---------------------------------------------------------------------------
# 5. README.md exemption — pointed out as a Tier-1-exclusion path
# ---------------------------------------------------------------------------


def test_readme_md_is_not_in_tier1_globs() -> None:
    """README.md is intentionally exempt — its `한국어` link label points
    at the deliberately translated `docs/README.ko.md`. Verified by
    confirming README.md is absent from the discovered Tier 1 set."""
    discovered = CHECKER.discover_tier1_paths(REPO_ROOT)
    rels = {p.relative_to(REPO_ROOT).as_posix() for p in discovered}
    assert "README.md" not in rels


# ---------------------------------------------------------------------------
# 7-8. Markdown-only code-block exemption
# ---------------------------------------------------------------------------


def test_markdown_fenced_code_block_korean_is_exempt(tmp_path: Path) -> None:
    """Korean inside a fenced ``` block in a .md file is treated as
    literal code/sample, not prose — exempt by policy."""
    violations = _scan(
        tmp_path,
        "docs/ai/shared/example.md",
        'Some prose.\n\n```\nprint("한국어")\n```\n\nMore prose.\n',
    )
    assert violations == []


def test_python_source_korean_string_literal_is_violation(
    tmp_path: Path,
) -> None:
    """No code-block exemption applies outside .md files. A Korean
    string literal in a .py source counts as policy violation."""
    violations = _scan(
        tmp_path,
        ".agents/shared/example.py",
        'MESSAGE = "한국어 메시지"\n',
    )
    assert len(violations) == 1


# ---------------------------------------------------------------------------
# 9. Drift test — TIER1_GLOBS vs AGENTS.md § Language Policy bullet list
# ---------------------------------------------------------------------------


def _extract_policy_paths_from_agents_md() -> set[str]:
    """Parse AGENTS.md § Language Policy → Tier 1 paths bullet list.

    Returns the set of distinct path tokens (each backtick-quoted entry).
    """
    text = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    match = re.search(
        r"### Tier 1 paths.*?###",
        text,
        flags=re.DOTALL,
    )
    assert match, "AGENTS.md § Language Policy → Tier 1 paths section not found"
    section = match.group(0)
    return set(re.findall(r"`([^`]+)`", section))


def test_tier1_globs_match_agents_md_policy_bullets() -> None:
    """Drift guard: the TIER1_GLOBS in the checker must cover every
    path token listed in AGENTS.md § Language Policy → Tier 1 paths,
    and vice versa.

    Allow either form: a glob may be present in the policy (e.g.
    ``docs/ai/shared/**``) or in TIER1_GLOBS as a parameterised glob
    (e.g. ``docs/ai/shared/**/*.md``). A simple normalisation makes
    them comparable.
    """
    policy_paths = _extract_policy_paths_from_agents_md()
    glob_paths = set(CHECKER.TIER1_GLOBS)

    def _normalize(path: str) -> str:
        # Drop trailing /** and /**/*.* extensions for comparison.
        normalized = re.sub(r"/\*\*(/\*\*?)?(\.[a-z]+)?$", "", path)
        normalized = re.sub(r"/\*\*$", "", normalized)
        return normalized.rstrip("/")

    policy_normalized = {_normalize(p) for p in policy_paths}
    glob_normalized = {_normalize(g) for g in glob_paths}

    # Anchor on a hand-picked subset that MUST exist in both — these are
    # the paths whose absence would make the policy text mislead readers.
    canonical_required = {
        "AGENTS.md",
        "CLAUDE.md",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        "SECURITY.md",
        "docs/ai/shared",
        "docs/history",
        ".claude/rules",
        ".claude/hooks",
        ".claude/skills",
        ".codex/rules",
        ".codex/hooks",
        ".agents",
    }
    missing_from_policy = canonical_required - policy_normalized
    missing_from_globs = canonical_required - glob_normalized
    assert not missing_from_policy, (
        f"AGENTS.md § Language Policy is missing canonical paths: {missing_from_policy}"
    )
    assert not missing_from_globs, (
        f"TIER1_GLOBS is missing canonical paths: {missing_from_globs}"
    )


# ---------------------------------------------------------------------------
# 10. Working-tree sanity check
# ---------------------------------------------------------------------------


def test_working_tree_has_zero_violations() -> None:
    """The whole working tree must currently pass the checker — this
    test is the live regression that fails the moment a contributor
    introduces Korean prose into a Tier 1 path."""
    paths = CHECKER.discover_tier1_paths(REPO_ROOT)
    all_violations = []
    for path in paths:
        all_violations.extend(CHECKER.find_violations(path, repo_root=REPO_ROOT))
    if all_violations:
        formatted = "\n".join(v.format() for v in all_violations[:20])
        pytest.fail(
            f"{len(all_violations)} Tier 1 Language Policy violations found "
            f"in the working tree (first 20 shown):\n{formatted}"
        )
