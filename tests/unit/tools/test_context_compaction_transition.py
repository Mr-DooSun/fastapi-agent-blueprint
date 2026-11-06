"""Temporary issue415/417 contract checks until issue416 supplies the full gate."""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SOURCES = (
    ".claude/rules/architecture-conventions.md",
    ".claude/rules/commands.md",
    ".claude/rules/project-overview.md",
    ".claude/rules/project-status.md",
    "docs/ai/shared/project-dna.md",
)


def test_sync_headers_stay_compact_without_prior_chains() -> None:
    for name in SOURCES:
        lines = (REPO_ROOT / name).read_text().splitlines()
        headers = [line for line in lines if line.startswith("> Last synced:")]
        assert len(headers) == 1, name
        assert len(headers[0].encode()) <= 200, name
        assert re.fullmatch(
            r"> Last synced: [0-9]{4}-[0-9]{2}-[0-9]{2} via #[0-9]+(?:, #[0-9]+)*",
            headers[0],
        ), name
        assert "Prior:" not in headers[0], name
        assert not any(line.startswith("> Prior:") for line in lines), name
