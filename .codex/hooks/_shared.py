from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

_SHARED_PKG = REPO_ROOT / ".agents" / "shared"
if str(_SHARED_PKG) not in sys.path:
    sys.path.insert(0, str(_SHARED_PKG))

try:
    from governor.completion_gate import (  # noqa: E402 — sys.path adjusted above
        changed_files_via_git as _impl,
    )

    _GATE_OK = True
except Exception:  # noqa: BLE001 — HC-5.5 fail-open
    _impl = None  # type: ignore[assignment]
    _GATE_OK = False


def load_payload() -> dict:
    return json.load(__import__("sys").stdin)


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        args,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def changed_files() -> list[str]:
    if _GATE_OK and _impl is not None:
        return _impl()
    # Fallback when governor module is unavailable (HC-5.5 fail-open).
    tracked = run_command(["git", "diff", "--name-only", "HEAD"])
    untracked = run_command(["git", "ls-files", "--others", "--exclude-standard"])
    seen: list[str] = []
    for chunk in (tracked.stdout, untracked.stdout):
        for line in chunk.splitlines():
            if line and line not in seen:
                seen.append(line)
    return seen


def extract_python_paths(command: str) -> list[Path]:
    matches = re.findall(r"([A-Za-z0-9_./-]+\.py)\b", command)
    paths: list[Path] = []
    for match in matches:
        candidate = (
            (REPO_ROOT / match).resolve() if not match.startswith("/") else Path(match)
        )
        try:
            candidate.relative_to(REPO_ROOT)
        except ValueError:
            continue
        if candidate.exists() and candidate.is_file():
            paths.append(candidate)
    return list(dict.fromkeys(paths))
