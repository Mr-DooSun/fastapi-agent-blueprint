"""Shared governor policy (Tier B). Consumed by Claude/Codex hook adapters.

Boundary: this package owns governor *policy* — token vocab, lifecycle, gate
logic, reminder text, glob matching. Tool-specific runtime utilities (e.g.
``.codex/hooks/_shared.py`` git/subprocess helpers, Codex session tracking)
remain per-tool and are not duplicated here.

Phase 5 (#124) consolidates duplicate helpers from Phase 2/3/4 hook scripts
into this single package. Hook scripts under ``.claude/hooks/`` and
``.codex/hooks/`` import from here as thin shims.

Public API is declared via ``__all__`` and grows as Phase 5 commits land:
    commit 1 — paths, time_window
    commit 2 — tokens, markers (lifecycle), safety
    commit 3 — verify
    commit 4 — completion_gate (GateResult)
"""

from .paths import GOVERNOR_PATHS_MD, REPO_ROOT
from .time_window import _within_24h

__all__ = [
    "REPO_ROOT",
    "GOVERNOR_PATHS_MD",
    "_within_24h",
]
