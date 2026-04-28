"""Governor review-log closure table checker.

Enforces AGENTS.md guard G for `docs/ai/shared/governor-review-log/pr-*.md`.
Each PR entry must contain exactly one `## R-points Closure Table` with the
canonical four-column shape:

| Source | R-point | Closure | Note |
|---|---|---|---|

V1 validates row-level closure labels only. It intentionally does not validate
summary counts, Source format, R-point ID format, or the semantic correctness
of a chosen closure category.

Used by:
- `.pre-commit-config.yaml` `governor-review-log-g-closure` hook
- `tests/unit/agents_shared/test_g_closure.py`
- Ad-hoc dry-run: `python3 tools/check_g_closure.py`
"""

from __future__ import annotations

import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REVIEW_LOG_DIR = "docs/ai/shared/governor-review-log"
REVIEW_LOG_GLOB = f"{REVIEW_LOG_DIR}/pr-*.md"

HEADING = "## R-points Closure Table"
CANONICAL_HEADER = ("Source", "R-point", "Closure", "Note")
VALID_CLOSURES = frozenset({"Fixed", "Deferred-with-rationale", "Rejected"})
FENCED_CODE_RE = re.compile(r"^[ ]{0,3}(```|~~~)")


@dataclass(frozen=True)
class Violation:
    path: str
    line_number: int
    reason: str
    line_content: str = ""

    def format(self) -> str:
        suffix = f"\n  {self.line_content!r}" if self.line_content else ""
        return f"{self.path}:{self.line_number}: {self.reason}{suffix}"


def _rel_path(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def discover_review_log_paths(repo_root: Path = REPO_ROOT) -> list[Path]:
    return sorted(repo_root.glob(REVIEW_LOG_GLOB))


def _strip_bom(text: str) -> str:
    return text[1:] if text.startswith("\ufeff") else text


def _outside_fence_lines(text: str) -> list[tuple[int, str]]:
    in_fence = False
    lines: list[tuple[int, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if FENCED_CODE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append((line_number, line))
    return lines


def _split_markdown_row(line: str) -> list[str] | None:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None

    cells: list[str] = []
    current: list[str] = []
    escaped = False
    # Drop the leading and trailing pipe. Escaped pipes inside the row stay.
    body = stripped[1:-1]
    for char in body:
        if escaped:
            if char == "|":
                current.append("|")
            else:
                current.append("\\")
                current.append(char)
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == "|":
            cells.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    if escaped:
        current.append("\\")
    cells.append("".join(current).strip())
    return cells


def _is_separator(cells: list[str]) -> bool:
    return len(cells) == 4 and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def _normalize_closure(cell: str) -> str:
    return unicodedata.normalize("NFKC", cell).strip()


def _valid_closure(cell: str) -> bool:
    normalized = _normalize_closure(cell)
    if normalized in VALID_CLOSURES:
        return True
    if normalized.startswith("**") and normalized.endswith("**"):
        inner = normalized[2:-2]
        return inner in VALID_CLOSURES
    return False


def find_violations(path: Path, repo_root: Path = REPO_ROOT) -> list[Violation]:
    rel = _rel_path(path, repo_root)
    text = _strip_bom(path.read_text(encoding="utf-8")).replace("\r\n", "\n")
    outside_fence = _outside_fence_lines(text)
    violations: list[Violation] = []

    heading_lines = [
        (line_no, line) for line_no, line in outside_fence if line.strip() == HEADING
    ]
    if not heading_lines:
        return [Violation(rel, 1, f"missing required heading `{HEADING}`")]
    if len(heading_lines) > 1:
        for line_no, line in heading_lines[1:]:
            violations.append(
                Violation(rel, line_no, f"duplicate heading `{HEADING}`", line)
            )
        return violations

    heading_index = next(
        index
        for index, (line_no, _line) in enumerate(outside_fence)
        if line_no == heading_lines[0][0]
    )
    table_lines: list[tuple[int, str]] = []
    table_started = False
    for line_no, line in outside_fence[heading_index + 1 :]:
        stripped = line.strip()
        if not stripped:
            if table_started:
                break
            continue
        if stripped.startswith("#"):
            break
        table_started = True
        table_lines.append((line_no, line))

    if len(table_lines) < 2:
        return [
            Violation(
                rel,
                heading_lines[0][0],
                "closure table is missing header and separator rows",
            )
        ]

    header_line_no, header_line = table_lines[0]
    header_cells = _split_markdown_row(header_line)
    if header_cells != list(CANONICAL_HEADER):
        violations.append(
            Violation(
                rel,
                header_line_no,
                "malformed header; expected `| Source | R-point | Closure | Note |`",
                header_line,
            )
        )

    separator_line_no, separator_line = table_lines[1]
    separator_cells = _split_markdown_row(separator_line)
    if separator_cells is None or not _is_separator(separator_cells):
        violations.append(
            Violation(
                rel,
                separator_line_no,
                "malformed separator row; expected four markdown separator cells",
                separator_line,
            )
        )

    data_rows = table_lines[2:]
    if not data_rows:
        violations.append(
            Violation(
                rel,
                heading_lines[0][0],
                "closure table must contain at least one data row",
            )
        )
        return violations

    for line_no, line in data_rows:
        cells = _split_markdown_row(line)
        if cells is None:
            violations.append(
                Violation(
                    rel, line_no, "table row must use leading and trailing pipes", line
                )
            )
            continue
        if len(cells) != 4:
            violations.append(
                Violation(
                    rel, line_no, "table row must have exactly four columns", line
                )
            )
            continue
        closure = cells[2]
        if not closure:
            violations.append(Violation(rel, line_no, "closure cell is empty", line))
            continue
        if not _valid_closure(closure):
            allowed = "Fixed, Deferred-with-rationale, Rejected"
            violations.append(
                Violation(
                    rel,
                    line_no,
                    f"non-canonical closure `{closure}`; expected one of {allowed}",
                    line,
                )
            )

    return violations


def _filter_review_log_paths(paths: list[Path], repo_root: Path) -> list[Path]:
    result: list[Path] = []
    for path in paths:
        rel = _rel_path(path, repo_root)
        if (
            rel.startswith(f"{REVIEW_LOG_DIR}/")
            and path.name.startswith("pr-")
            and path.suffix == ".md"
        ):
            result.append(path)
    return sorted(result)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv:
        candidates = [
            Path(arg) if Path(arg).is_absolute() else REPO_ROOT / arg for arg in argv
        ]
        paths = _filter_review_log_paths(
            [path for path in candidates if path.exists()], REPO_ROOT
        )
    else:
        paths = discover_review_log_paths(REPO_ROOT)

    violations: list[Violation] = []
    for path in paths:
        violations.extend(find_violations(path, repo_root=REPO_ROOT))

    if violations:
        print(f"Governor review-log G closure: {len(violations)} violation(s)")
        for violation in violations:
            print(violation.format())
        return 1

    print(f"Governor review-log G closure: 0 violations across {len(paths)} entries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
