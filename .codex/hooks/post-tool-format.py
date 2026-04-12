from __future__ import annotations

import json
import shutil
import subprocess
import sys

from _shared import REPO_ROOT, extract_python_paths

payload = json.load(sys.stdin)
command = payload.get("tool_input", {}).get("command", "")
paths = extract_python_paths(command)

if not paths or shutil.which("ruff") is None:
    raise SystemExit(0)

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
