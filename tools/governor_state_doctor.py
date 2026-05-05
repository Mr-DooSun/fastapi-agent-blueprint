#!/usr/bin/env python3
"""Standalone diagnostic CLI for governor state lifecycle health.

Six checks:

    C1  gitignore_registered  — .claude/state/ and .codex/state/ in .gitignore
    C2  no_git_tracked_state  — no state/*.json files tracked by git
    C3  stop_hook_schema      — Stop entry in hooks.json + settings.json is valid
    C4  marker_glob_coverage  — Stop hooks reference all known marker globs
    C5  hook_interpreter      — Hook files exist; .sh exec bit; Stop .py imports governor
    C6  stale_stats           — Counts stale (>24 h) markers in both state dirs

Usage:
    python3 tools/governor_state_doctor.py [--json]

    --json  (default) emit results as a single JSON object to stdout
    --text  human-readable summary to stdout

Exit codes:
    0 — all six checks passed
    1 — one or more checks failed
"""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Project root detection
# ---------------------------------------------------------------------------

_SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = _SCRIPT_DIR.parent  # tools/ is one level below root


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str
    data: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# C1 — .gitignore registration
# ---------------------------------------------------------------------------

_REQUIRED_GITIGNORE_PATTERNS = (".claude/state/", ".codex/state/")


def check_gitignore_registered(root: Path = PROJECT_ROOT) -> CheckResult:
    gitignore = root / ".gitignore"
    if not gitignore.exists():
        return CheckResult("C1_gitignore_registered", False, ".gitignore not found")

    text = gitignore.read_text(encoding="utf-8")
    missing = [p for p in _REQUIRED_GITIGNORE_PATTERNS if p not in text]
    if missing:
        return CheckResult(
            "C1_gitignore_registered",
            False,
            f"Missing gitignore patterns: {missing}",
            {"missing": missing},
        )
    return CheckResult(
        "C1_gitignore_registered",
        True,
        "Both state/ patterns present in .gitignore",
    )


# ---------------------------------------------------------------------------
# C2 — no state files tracked by git
# ---------------------------------------------------------------------------


def check_no_git_tracked_state(root: Path = PROJECT_ROOT) -> CheckResult:
    try:
        result = subprocess.run(
            ["git", "ls-files", ".claude/state/", ".codex/state/"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return CheckResult(
            "C2_no_git_tracked_state",
            False,
            f"git ls-files failed: {exc}",
        )
    tracked = result.stdout.strip()
    if tracked:
        files = tracked.splitlines()
        return CheckResult(
            "C2_no_git_tracked_state",
            False,
            f"{len(files)} state file(s) tracked by git",
            {"tracked_files": files},
        )
    return CheckResult(
        "C2_no_git_tracked_state",
        True,
        "No state files tracked by git",
    )


# ---------------------------------------------------------------------------
# C3 — Stop hook entry schema
# ---------------------------------------------------------------------------


def _validate_stop_entries(
    config: dict,
    label: str,
) -> list[str]:
    """Return a list of issues found in a hooks config dict."""
    issues: list[str] = []
    stop_events = config.get("hooks", {}).get("Stop", [])
    if not stop_events:
        issues.append(f"{label}: no Stop entry found")
        return issues
    for event_block in stop_events:
        for hook in event_block.get("hooks", []):
            if hook.get("type") != "command":
                issues.append(
                    f"{label}: Stop hook type is not 'command': {hook.get('type')!r}"
                )
            cmd = hook.get("command", "").strip()
            if not cmd:
                issues.append(f"{label}: Stop hook has empty command")
    return issues


def check_stop_hook_schema(root: Path = PROJECT_ROOT) -> CheckResult:
    issues: list[str] = []

    codex_hooks_json = root / ".codex" / "hooks.json"
    if not codex_hooks_json.exists():
        issues.append(".codex/hooks.json not found")
    else:
        try:
            data = json.loads(codex_hooks_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            issues.append(f".codex/hooks.json JSON parse error: {exc}")
            data = {}
        issues.extend(_validate_stop_entries(data, "Codex hooks.json"))

    claude_settings = root / ".claude" / "settings.json"
    if not claude_settings.exists():
        issues.append(".claude/settings.json not found")
    else:
        try:
            data = json.loads(claude_settings.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            issues.append(f".claude/settings.json JSON parse error: {exc}")
            data = {}
        issues.extend(_validate_stop_entries(data, "Claude settings.json"))

    if issues:
        return CheckResult(
            "C3_stop_hook_schema",
            False,
            "; ".join(issues),
            {"issues": issues},
        )
    return CheckResult(
        "C3_stop_hook_schema",
        True,
        "Stop hook entries valid in both hooks.json and settings.json",
    )


# ---------------------------------------------------------------------------
# C4 — marker glob coverage
# ---------------------------------------------------------------------------


def check_marker_glob_coverage(root: Path = PROJECT_ROOT) -> CheckResult:
    issues: list[str] = []

    # Codex Stop hook must call consume_phase2_markers
    codex_stop = root / ".codex" / "hooks" / "stop-sync-reminder.py"
    if not codex_stop.exists():
        issues.append(".codex/hooks/stop-sync-reminder.py not found")
    else:
        if "consume_phase2_markers" not in codex_stop.read_text(encoding="utf-8"):
            issues.append(
                ".codex/hooks/stop-sync-reminder.py: consume_phase2_markers not referenced"
            )

    # governor/markers.py must define the exception-token glob
    markers_py = root / ".agents" / "shared" / "governor" / "markers.py"
    if not markers_py.exists():
        issues.append(".agents/shared/governor/markers.py not found")
    else:
        text = markers_py.read_text(encoding="utf-8")
        if "exception-token-*.json" not in text:
            issues.append(
                "governor/markers.py: exception-token-*.json glob pattern not found"
            )

    # completion_gate.py must define the verify-log glob
    gate_py = root / ".codex" / "hooks" / "completion_gate.py"
    if not gate_py.exists():
        issues.append(".codex/hooks/completion_gate.py not found")
    else:
        if "verify-log-*.json" not in gate_py.read_text(encoding="utf-8"):
            issues.append(
                ".codex/hooks/completion_gate.py: verify-log-*.json glob pattern not found"
            )

    if issues:
        return CheckResult(
            "C4_marker_glob_coverage",
            False,
            "; ".join(issues),
            {"issues": issues},
        )
    return CheckResult(
        "C4_marker_glob_coverage",
        True,
        "All expected marker glob patterns present",
    )


# ---------------------------------------------------------------------------
# C5 — hook file existence, .sh exec bit, Stop .py governor import
# ---------------------------------------------------------------------------


def _collect_hook_commands(root: Path) -> list[str]:
    """Return all hook command strings from hooks.json and settings.json."""
    commands: list[str] = []

    for cfg_path in (
        root / ".codex" / "hooks.json",
        root / ".claude" / "settings.json",
    ):
        if not cfg_path.exists():
            continue
        try:
            data = json.loads(cfg_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for event_blocks in data.get("hooks", {}).values():
            for block in event_blocks:
                for hook in block.get("hooks", []):
                    cmd = hook.get("command", "").strip()
                    if cmd:
                        commands.append(cmd)
    return commands


def check_hook_interpreter(root: Path = PROJECT_ROOT) -> CheckResult:
    issues: list[str] = []

    commands = _collect_hook_commands(root)
    for cmd in commands:
        # The first token after optional env modifiers is the interpreter/file
        parts = cmd.split()
        if not parts:
            continue
        # e.g. "bash .claude/hooks/stop-sync-reminder.sh"
        # e.g. "python3 .codex/hooks/stop-sync-reminder.py"
        hook_rel = parts[-1] if len(parts) >= 2 else parts[0]

        hook_path = (
            (root / hook_rel).resolve()
            if not hook_rel.startswith("/")
            else Path(hook_rel)
        )
        if not hook_path.exists():
            issues.append(f"Hook file not found: {hook_rel}")
            continue

        # .sh files must have exec bit
        if hook_path.suffix == ".sh":
            mode = hook_path.stat().st_mode
            if not (mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)):
                issues.append(f"{hook_rel}: .sh hook missing exec bit")

    # Stop .py import check: verify governor.markers is importable via subprocess.
    # PYTHONPATH is set to .agents/shared so the subprocess can resolve governor.*
    # without an f-string path injection.
    stop_py = root / ".codex" / "hooks" / "stop-sync-reminder.py"
    if stop_py.exists():
        shared = root / ".agents" / "shared"
        env = os.environ.copy()
        env["PYTHONPATH"] = str(shared)
        import_code = "from governor.markers import consume_phase2_markers; print('ok')"
        try:
            proc = subprocess.run(  # noqa: S603
                [sys.executable, "-c", import_code],
                capture_output=True,
                text=True,
                timeout=15,
                env=env,
            )
            if proc.returncode != 0 or "ok" not in proc.stdout:
                issues.append(
                    f"governor.markers import failed: {proc.stderr.strip()[:200]}"
                )
        except subprocess.TimeoutExpired:
            issues.append("governor.markers import check timed out")
    else:
        issues.append(
            ".codex/hooks/stop-sync-reminder.py not found (skip import check)"
        )

    if issues:
        return CheckResult(
            "C5_hook_interpreter",
            False,
            "; ".join(issues),
            {"issues": issues},
        )
    return CheckResult(
        "C5_hook_interpreter",
        True,
        "All hook files exist; .sh exec bits OK; governor.markers importable",
    )


# ---------------------------------------------------------------------------
# C6 — stale marker statistics
# ---------------------------------------------------------------------------

_STATE_DIRS = (
    Path(".claude/state"),
    Path(".codex/state"),
)
_STALE_THRESHOLD_S = 86_400  # 24 hours


def _count_stale(state_dir: Path, glob: str, threshold_s: float) -> dict:
    now = time.time()
    all_files = list(state_dir.glob(glob)) if state_dir.exists() else []
    stale = [f for f in all_files if (now - f.stat().st_mtime) > threshold_s]
    return {"total": len(all_files), "stale": len(stale)}


def check_stale_stats(root: Path = PROJECT_ROOT) -> CheckResult:
    stats: dict[str, dict] = {}
    total_stale = 0

    for rel_dir in _STATE_DIRS:
        abs_dir = root / rel_dir
        dir_key = str(rel_dir)
        token_counts = _count_stale(
            abs_dir, "exception-token-*.json", _STALE_THRESHOLD_S
        )
        verify_counts = _count_stale(abs_dir, "verify-log-*.json", _STALE_THRESHOLD_S)
        stats[dir_key] = {
            "exception_token": token_counts,
            "verify_log": verify_counts,
        }
        total_stale += token_counts["stale"] + verify_counts["stale"]

    detail = f"{total_stale} stale marker(s) found across both state dirs"
    return CheckResult(
        "C6_stale_stats",
        True,  # informational — never fails on its own
        detail,
        {"state_dirs": stats, "total_stale": total_stale},
    )


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

_CHECKS = [
    check_gitignore_registered,
    check_no_git_tracked_state,
    check_stop_hook_schema,
    check_marker_glob_coverage,
    check_hook_interpreter,
    check_stale_stats,
]


def run_all(root: Path = PROJECT_ROOT) -> list[CheckResult]:
    return [fn(root) for fn in _CHECKS]


def main() -> int:
    args = sys.argv[1:]
    text_mode = "--text" in args

    results = run_all()
    all_ok = all(r.ok for r in results)

    output = {
        "project_root": str(PROJECT_ROOT),
        "all_ok": all_ok,
        "checks": [asdict(r) for r in results],
    }

    if text_mode:
        for r in results:
            status = "PASS" if r.ok else "FAIL"
            print(f"[{status}] {r.name}: {r.detail}")
        if not all_ok:
            failed = [r.name for r in results if not r.ok]
            print(f"\nFailed checks: {', '.join(failed)}")
    else:
        print(json.dumps(output, indent=2))

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
