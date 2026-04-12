from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


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
