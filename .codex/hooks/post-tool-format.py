"""PostToolUse Bash hook (Codex side).

Two responsibilities, both fail-open per HC-3.6:
1. Format `.py` files touched by a Bash command via `ruff format` + `ruff check --fix`.
2. Phase 3 (#122): record verify-class commands (`pytest`, `make test`, etc.)
   to the current-session verify-log so the Stop hook can determine whether
   verify happened in this session.

R0.4 reinforcement: the entire body is wrapped in a top-level fail-open so
malformed stdin / missing dependencies / unexpected exceptions never crash
the hook.
"""

from __future__ import annotations

import contextlib
import json
import shutil
import subprocess
import sys


def _format_python_paths(command: str) -> None:
    from _shared import REPO_ROOT, extract_python_paths  # local import — fail-open

    paths = extract_python_paths(command)
    if not paths or shutil.which("ruff") is None:
        return
    for path in paths:
        subprocess.run(  # noqa: S603
            ["ruff", "format", str(path)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        subprocess.run(  # noqa: S603
            ["ruff", "check", "--fix", str(path)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )


def _record_verify_class(command: str) -> None:
    from verify_first import append_verify_log  # local import — fail-open

    append_verify_log(command)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if not isinstance(payload, dict):
        return 0
    command = payload.get("tool_input", {}).get("command", "")
    if not isinstance(command, str) or not command:
        return 0

    # Both branches fail-open per HC-3.6: formatting / verify-log writer errors
    # must never crash the hook.
    with contextlib.suppress(Exception):
        _format_python_paths(command)
    with contextlib.suppress(Exception):
        _record_verify_class(command)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
