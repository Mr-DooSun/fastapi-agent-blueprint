"""Stop hook (Codex side) — sync-reminder + Phase 3 verify-first segment.

Single Stop event output (IC-2): all advisories are collected into a list of
segments and emitted as one ``{"systemMessage": "<segments joined by \\n\\n>"}``
JSON line. Empty list = no output.

Phase 3 (#122 / R0.1) reinforcement: the verify-first import is performed
inside the same ``try`` block that calls ``should_remind`` so an ImportError
or any module-level failure never crashes the existing sync-reminder
behaviour (HC-3.6 fail-open).
"""

from __future__ import annotations

import contextlib
import json

from _shared import changed_files

FOUNDATION_PREFIXES = (
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

STRUCTURE_MARKERS = (
    "/infrastructure/di/",
    "/interface/server/routers/",
    "/domain/protocols/",
    "/domain/dtos/",
)


changed = changed_files()
foundation = [path for path in changed if path.startswith(FOUNDATION_PREFIXES)]
structure = [
    path
    for path in changed
    if path.startswith("src/")
    and "/_" not in path
    and any(marker in path for marker in STRUCTURE_MARKERS)
]

segments: list[str] = []

if foundation:
    segments.append(
        "\n".join(
            [
                "Guideline sync required before closing this work.",
                "Foundation files changed:",
                *[f"- {path}" for path in foundation[:12]],
                "Codex: run $sync-guidelines",
                "Claude Code: run /sync-guidelines as well",
                "Sync is incomplete until project-dna, AUTO-FIX, REVIEW, and Remaining are all reported.",
                "REVIEW targets must be reported even when no automatic doc edit is needed.",
            ]
        )
    )
elif structure:
    segments.append(
        "\n".join(
            [
                "Guideline sync recommended.",
                "Domain structure files changed:",
                *[f"- {path}" for path in structure[:12]],
                "When you run sync, report both AUTO-FIX and REVIEW targets before closing.",
            ]
        )
    )

# Phase 3 verify-first segment — fail-open: ImportError / unexpected
# exception leaves only the existing sync-reminder behaviour intact (R0.1).
with contextlib.suppress(Exception):
    import verify_first  # noqa: PLC0415 — local import for fail-open per R0.1

    if verify_first.should_remind():
        segments.append(verify_first.REMINDER_TEXT)

if segments:
    print(json.dumps({"systemMessage": "\n\n".join(segments)}))
