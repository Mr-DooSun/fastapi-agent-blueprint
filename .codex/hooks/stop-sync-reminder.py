from __future__ import annotations

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

if foundation:
    message = "\n".join(
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
    print(json.dumps({"systemMessage": message}))
elif structure:
    message = "\n".join(
        [
            "Guideline sync recommended.",
            "Domain structure files changed:",
            *[f"- {path}" for path in structure[:12]],
            "When you run sync, report both AUTO-FIX and REVIEW targets before closing.",
        ]
    )
    print(json.dumps({"systemMessage": message}))
