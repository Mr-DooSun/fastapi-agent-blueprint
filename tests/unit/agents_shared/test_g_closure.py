"""Regression tests for tools/check_g_closure.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


def _import_checker():
    module_name = "_check_g_closure"
    if module_name in sys.modules:
        return sys.modules[module_name]
    module_path = REPO_ROOT / "tools" / "check_g_closure.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


CHECKER = _import_checker()


VALID_TABLE = """# PR #999

## R-points Closure Table

| Source | R-point | Closure | Note |
|---|---|---|---|
| Round 1 | handled | **Fixed** | applied |
| Round 1 | deferred | Deferred-with-rationale | scoped follow-up |
| Round 1 | rejected | **Rejected** | not a defect |
"""


def _scan(
    tmp_path: Path,
    content: str,
    rel_path: str = "docs/ai/shared/governor-review-log/pr-999-test.md",
):
    target = tmp_path / rel_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8", newline="")
    return CHECKER.find_violations(target, repo_root=tmp_path)


def test_valid_table_with_plain_and_bold_closures_passes(tmp_path: Path) -> None:
    assert _scan(tmp_path, VALID_TABLE) == []


def test_missing_heading_fails(tmp_path: Path) -> None:
    violations = _scan(tmp_path, "# PR #999\n")
    assert len(violations) == 1
    assert "missing required heading" in violations[0].reason


def test_multiple_headings_fail(tmp_path: Path) -> None:
    violations = _scan(tmp_path, VALID_TABLE + "\n## R-points Closure Table\n")
    assert len(violations) == 1
    assert "duplicate heading" in violations[0].reason


def test_heading_inside_fenced_code_is_ignored(tmp_path: Path) -> None:
    content = "```\n## R-points Closure Table\n```\n\n" + VALID_TABLE
    assert _scan(tmp_path, content) == []


def test_heading_inside_tilde_fenced_code_is_ignored(tmp_path: Path) -> None:
    content = "~~~markdown\n## R-points Closure Table\n~~~\n\n" + VALID_TABLE
    assert _scan(tmp_path, content) == []


def test_blockquoted_heading_is_ignored(tmp_path: Path) -> None:
    content = "> ## R-points Closure Table\n\n" + VALID_TABLE
    assert _scan(tmp_path, content) == []


def test_malformed_header_fails(tmp_path: Path) -> None:
    violations = _scan(
        tmp_path,
        VALID_TABLE.replace(
            "| Source | R-point | Closure | Note |", "| Source | Closure | Note |"
        ),
    )
    assert any("malformed header" in violation.reason for violation in violations)


def test_malformed_separator_fails(tmp_path: Path) -> None:
    violations = _scan(
        tmp_path, VALID_TABLE.replace("|---|---|---|---|", "|---|---|---|")
    )
    assert any("malformed separator" in violation.reason for violation in violations)


def test_empty_table_fails(tmp_path: Path) -> None:
    content = """# PR #999

## R-points Closure Table

| Source | R-point | Closure | Note |
|---|---|---|---|
"""
    violations = _scan(tmp_path, content)
    assert len(violations) == 1
    assert "at least one data row" in violations[0].reason


def test_malformed_row_column_count_fails(tmp_path: Path) -> None:
    violations = _scan(
        tmp_path, VALID_TABLE + "| Round 2 | missing columns | **Fixed** |\n"
    )
    assert any("exactly four columns" in violation.reason for violation in violations)


def test_escaped_pipe_in_note_cell_passes(tmp_path: Path) -> None:
    content = (
        VALID_TABLE
        + "| Round 2 | escaped pipe | **Fixed** | `a \\| b` remains one note cell |\n"
    )
    assert _scan(tmp_path, content) == []


def test_bom_and_crlf_pass(tmp_path: Path) -> None:
    assert _scan(tmp_path, "\ufeff" + VALID_TABLE.replace("\n", "\r\n")) == []


@pytest.mark.parametrize(
    "closure",
    [
        "**Fixed **",
        "__Fixed__",
        "*Fixed*",
        "fixed",
        "Fixed (retracted)",
        "Rejected after correction",
        "Deferred",
        "",
    ],
)
def test_invalid_closure_variants_fail(tmp_path: Path, closure: str) -> None:
    content = VALID_TABLE + f"| Round 2 | invalid | {closure} | note |\n"
    violations = _scan(tmp_path, content)
    assert any("closure" in violation.reason for violation in violations)


def test_prose_invalid_labels_outside_table_are_ignored(tmp_path: Path) -> None:
    content = (
        "# PR #999\n\n"
        "Historical prose mentions `Rejected after correction` and `Fixed (retracted)`.\n\n"
        + VALID_TABLE
    )
    assert _scan(tmp_path, content) == []


def test_argv_filtering_scans_only_review_log_entries(tmp_path: Path) -> None:
    valid = tmp_path / "docs/ai/shared/governor-review-log/pr-999-valid.md"
    valid.parent.mkdir(parents=True, exist_ok=True)
    valid.write_text(VALID_TABLE, encoding="utf-8")
    ignored = tmp_path / "docs/ai/shared/governor-review-log/README.md"
    ignored.write_text("# README\n", encoding="utf-8")

    paths = CHECKER._filter_review_log_paths([valid, ignored], tmp_path)

    assert paths == [valid]


def test_working_tree_has_zero_g_closure_violations() -> None:
    all_violations = []
    for path in CHECKER.discover_review_log_paths(REPO_ROOT):
        all_violations.extend(CHECKER.find_violations(path, repo_root=REPO_ROOT))
    if all_violations:
        formatted = "\n".join(violation.format() for violation in all_violations[:20])
        pytest.fail(f"{len(all_violations)} G-closure violations found:\n{formatted}")
