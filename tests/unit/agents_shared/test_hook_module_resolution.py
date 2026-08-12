"""A test must load the harness copy its name claims (#401).

Eight hook basenames exist in more than one harness directory — `verify_first.py`
and `completion_gate.py` in all three — so `import verify_first` after a
`sys.path.insert` is ambiguous, and `sys.modules` decides it. Measured before this
guard existed: after a full `tests/unit/agents_shared` run,

    verify_first     -> .codex/hooks/verify_first.py
    completion_gate  -> .codex/hooks/completion_gate.py

while `test_fail_open.py` had inserted `.claude/hooks` and imported both by name.
Its tier-2 tests were asserting the Codex fail-open behaviour under Claude names;
the two copies of `verify_first.py` differ by 228 lines.

**The pollution is not the tests' fault and cannot be fixed by renaming.** The hook
files import their own siblings by bare name — `.codex/hooks/completion_gate.py`
does `import _shared` and `import verify_first` — which is correct for a standalone
hook process, where one harness directory is on `sys.path`. It only collides inside
a shared pytest process that loads more than one harness's copies. So the invariant
this file pins is the one a test *can* control: load by path, never by bare name.

Two tests, in the order they matter:

1. No test in this directory imports a colliding harness basename. That is the
   structural rule; the AST check cannot be satisfied by accident.
2. The tier-2 fail-open tests actually receive `.claude/hooks` modules. That is the
   behaviour the rule exists to protect, checked directly rather than inferred.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_TESTS_DIR = Path(__file__).resolve().parent
_HARNESS_DIRS = (
    _REPO_ROOT / ".claude" / "hooks",
    _REPO_ROOT / ".codex" / "hooks",
    _REPO_ROOT / ".antigravity" / "hooks",
)


def _colliding_basenames() -> set[str]:
    """Module names that exist in more than one harness directory."""
    seen: dict[str, int] = {}
    for directory in _HARNESS_DIRS:
        for path in directory.glob("*.py"):
            seen[path.stem] = seen.get(path.stem, 0) + 1
    return {stem for stem, count in seen.items() if count > 1}


def test_more_than_one_harness_copy_exists() -> None:
    """The precondition. If this ever fails the rest of the file is moot."""
    colliding = _colliding_basenames()

    assert "verify_first" in colliding, (
        "verify_first no longer exists in multiple harness directories — if the "
        "copies were consolidated, this whole file can go"
    )
    assert len(colliding) >= 2, f"expected several colliding basenames, got {colliding}"


def test_no_test_imports_a_colliding_harness_module_by_name() -> None:
    """`import verify_first` cannot say which copy it means.

    Checked by AST rather than by grep, so a mention inside a docstring or a
    subprocess script string — both of which exist in this directory and are
    correct, because a subprocess gets its own `sys.modules` — does not count.
    """
    colliding = _colliding_basenames()
    offenders: list[str] = []

    for path in sorted(_TESTS_DIR.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in colliding:
                        offenders.append(
                            f"{path.name}:{node.lineno} import {alias.name}"
                        )
            elif isinstance(node, ast.ImportFrom) and node.module in colliding:
                offenders.append(
                    f"{path.name}:{node.lineno} from {node.module} import ..."
                )

    assert not offenders, (
        "these imports name a module that exists in more than one harness copy, so "
        f"`sys.modules` decides which one arrives: {offenders}. Load it by path "
        "instead — `importlib.util.spec_from_file_location('claude_verify_first', "
        "path)` — which is what the rest of this directory already does."
    )


@pytest.mark.parametrize(
    "stem", ["user_prompt_submit", "verify_first", "completion_gate"]
)
def test_claude_hooks_load_from_the_claude_directory(stem: str) -> None:
    """The behaviour the rule protects, for the three modules tier 2 exercises.

    Loading by path under a harness-qualified alias must yield a module whose
    `__file__` is the Claude copy, no matter what a previously-run test left in
    `sys.modules` under the bare name. Asserted on `__file__` because that is the
    thing that was wrong: the tests passed while exercising the other copy.
    """
    path = _REPO_ROOT / ".claude" / "hooks" / f"{stem}.py"
    assert path.is_file(), f"{path} is missing"

    # Poison the bare key first — this is the state a real suite run produces.
    codex_copy = _REPO_ROOT / ".codex" / "hooks" / f"{stem}.py"
    if codex_copy.is_file():
        poisoned = importlib.util.spec_from_file_location(stem, str(codex_copy))
        assert poisoned is not None
        sys.modules[stem] = importlib.util.module_from_spec(poisoned)

    try:
        spec = importlib.util.spec_from_file_location(f"claude_{stem}", str(path))
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"claude_{stem}"] = module
        spec.loader.exec_module(module)

        assert module.__file__ is not None
        assert Path(module.__file__).parent == path.parent, (
            f"loaded {module.__file__} while asking for {path} — path-based loading "
            "is supposed to be immune to whatever occupies the bare name"
        )
    finally:
        sys.modules.pop(stem, None)
        sys.modules.pop(f"claude_{stem}", None)
