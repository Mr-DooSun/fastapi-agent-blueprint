#!/usr/bin/env python3
"""CLI bridge for governor.paths.resolve_session_roots — bash integration (#425).

Reads a hook payload (JSON) from stdin and prints one line:

* the top level of the session's working tree — re-rooted;
* ``rejected`` — the payload names a ``cwd`` this harness cannot place, so the
  caller must skip session-scoped work rather than fall back to its own
  checkout (see ``governor.paths.SessionRoots``);
* nothing — no ``cwd``: the caller keeps its own checkout (pre-#425 behaviour).

Always exits 0 — HC-5.5 fail-open: any exception produces empty output.

Invocation (from .claude/hooks/stop-sync-reminder.sh):
  printf '%s' "$INPUT" \\
    | PYTHONPATH="$SHARED_DIR" sh "$PY_LAUNCHER" -m governor.session_root_cli
"""

from __future__ import annotations

import json
import sys


def main() -> None:
    try:
        from governor.paths import resolve_session_roots

        roots = resolve_session_roots(json.loads(sys.stdin.read() or "{}"))
        if roots.rejected:
            print("rejected")
        elif roots.repo_root is not None:
            print(roots.repo_root)
    except Exception:  # noqa: BLE001,S110 — HC-5.5 fail-open: no session root
        pass


if __name__ == "__main__":
    main()
