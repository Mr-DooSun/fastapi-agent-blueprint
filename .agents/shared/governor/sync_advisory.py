"""Shared sync-advisory classification (PR-A.5).

Single source of truth for ``FOUNDATION_PREFIXES`` / ``STRUCTURE_MARKERS``
and the ``classify_advisory`` decision function. Extracted from the inline
declarations in ``.codex/hooks/stop-sync-reminder.py`` so both the Codex
Python hook and future Claude-side migrations consume identical rules
(IC-2 single-source goal).

The ``.claude/hooks/stop-sync-reminder.sh`` bash hook is NOT yet migrated
(F-1 follow-up — see GitHub issue linked in PR-A.5 Footer).
"""

from __future__ import annotations

from typing import Literal

FOUNDATION_PREFIXES: tuple[str, ...] = (
    "AGENTS.md",
    "CLAUDE.md",
    ".codex/",
    ".agents/",
    ".claude/hooks/",
    ".claude/rules/",
    ".claude/settings.json",
    "docs/ai/shared/",
    "docs/ai/shared/skills/",
    "src/_apps/",
    "src/_core/",
    "pyproject.toml",
    ".pre-commit-config.yaml",
)

STRUCTURE_MARKERS: tuple[str, ...] = (
    "/infrastructure/di/",
    "/interface/server/routers/",
    "/domain/protocols/",
    "/domain/dtos/",
)

AdvisoryLevel = Literal["foundation", "structure", None]


def classify_advisory(
    changed_files: list[str],
) -> tuple[AdvisoryLevel, list[str]]:
    """Classify the advisory level for a set of changed file paths.

    Returns a ``(level, matching_files)`` pair:
      - ``("foundation", [...])`` — one or more foundation files changed;
        guideline sync is required before closing the work.
      - ``("structure", [...])`` — domain-structure files changed but no
        foundation files; guideline sync is recommended.
      - ``(None, [])`` — no advisory needed.

    Foundation takes precedence over structure when both are present.
    """
    foundation = [p for p in changed_files if p.startswith(FOUNDATION_PREFIXES)]
    if foundation:
        return "foundation", foundation

    structure = [
        p
        for p in changed_files
        if p.startswith("src/")
        and "/_" not in p
        and any(marker in p for marker in STRUCTURE_MARKERS)
    ]
    if structure:
        return "structure", structure

    return None, []
