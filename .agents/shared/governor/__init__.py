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

from .markers import (
    MarkerLifecycle,
    consume_phase2_markers,
    read_latest_token,
    write_marker,
)
from .paths import GOVERNOR_PATHS_MD, REPO_ROOT
from .safety import (
    PROMPT_RULES,
    Blocked,
    ParsedToken,
    SafeParseResult,
    check_safety,
    safe_parse_exception_token,
)
from .time_window import _within_24h
from .tokens import EXPLORATION_TOKENS, TOKEN_REGEX, parse_exception_token

__all__ = [
    "Blocked",
    "EXPLORATION_TOKENS",
    "GOVERNOR_PATHS_MD",
    "MarkerLifecycle",
    "PROMPT_RULES",
    "ParsedToken",
    "REPO_ROOT",
    "SafeParseResult",
    "TOKEN_REGEX",
    "_within_24h",
    "check_safety",
    "consume_phase2_markers",
    "parse_exception_token",
    "read_latest_token",
    "safe_parse_exception_token",
    "write_marker",
]
