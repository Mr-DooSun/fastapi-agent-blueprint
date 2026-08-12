"""Guard the pyright gate against silently shrinking.

`[tool.pyright] include` is now `["src"]` — the whole tree, 0 errors. It got there
as an allow-list of clean packages (#333, widened through #381), and that list
turned out to be a drift generator in its own right: `project-dna.md` still named
five packages after four PRs had added six more, and nothing failed, because a
stale allow-list fails nothing.

Whole-tree coverage removes that particular trap but adds two of its own, both
silent:

- **Narrowing.** Someone hits a wall of errors in one package and replaces `src`
  with a subset. pyright does not error on a smaller scope — it just checks less,
  exits 0, and the gate shrinks with CI still green.
- **Suppression creep.** `# pyright: ignore` is the other way to keep the tree at
  0 errors without fixing anything. Nine exist today, all in two bootstrap
  modules, all for framework contracts this repo cannot annotate its way out of.
  That is a defensible number *because* it is pinned; unpinned, it is a trend.

These tests fail loudly in both cases.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_PYPROJECT = _REPO_ROOT / "pyproject.toml"
_SRC = _REPO_ROOT / "src"

# Where suppressions are allowed, and how many. Each is a framework contract with
# its cause written at the call site: dependency-injector's dynamic provider
# attributes and module-attribute injection (admin), Starlette's
# `add_exception_handler` handler signature (server), and a deliberately widened
# `on_send` parameter that taskiq's own base middleware does not declare.
#
# Adding an entry here is allowed — silently adding one to a file that is not
# listed is what this pins. If a genuine third-party limitation needs a new
# suppression, add the file and say why in the same commit.
_ALLOWED_SUPPRESSIONS = {
    "_apps/admin/bootstrap.py": 6,
    "_apps/server/bootstrap.py": 3,
    "_core/infrastructure/logging/taskiq_middleware.py": 1,
}

# Matches a real directive, not a mention of one in prose. Pyright itself is this
# permissive — it reads a directive inside a comment even when it is only being
# quoted as an example, which is why the explanation in `admin/bootstrap.py` is
# worded to avoid containing one.
_SUPPRESSION = re.compile(r"#\s*pyright:\s*ignore")


def _pyright_config() -> dict:
    with _PYPROJECT.open("rb") as handle:
        return tomllib.load(handle)["tool"]["pyright"]


def _include_paths() -> list[str]:
    return list(_pyright_config()["include"])


def _src_packages() -> list[str]:
    """Top-level importable packages under `src/`."""
    return sorted(
        child.name
        for child in _SRC.iterdir()
        if child.is_dir() and (child / "__init__.py").exists()
    )


def test_pyright_is_configured() -> None:
    config = _pyright_config()

    assert config["include"], "an empty include list checks the whole repo by accident"
    assert config["pythonVersion"] == "3.12"


@pytest.mark.parametrize("path", _include_paths())
def test_every_include_path_exists(path: str) -> None:
    resolved = _REPO_ROOT / path

    assert resolved.is_dir(), (
        f"[tool.pyright] include lists {path!r}, which no longer exists. "
        "pyright does not error on a missing include — it just checks less, "
        "so the CI type gate would shrink without anything going red."
    )


@pytest.mark.parametrize("package", _src_packages())
def test_every_src_package_is_covered(package: str) -> None:
    """Narrowing `["src"]` to a subset has to fail here.

    Asserted per package rather than as `include == ["src"]` so that splitting the
    list for an unrelated reason (a second root, an explicit exclude) stays legal
    as long as nothing under `src/` falls out of scope.
    """
    covered = [
        path
        for path in _include_paths()
        if path == "src" or path.split("/")[:2] == ["src", package]
    ]

    assert covered, (
        f"src/{package} is not covered by [tool.pyright] include "
        f"{_include_paths()!r}. The type gate reached 0 errors across all of "
        "src/; excluding a package to get past its errors gives that up "
        "silently, because pyright exits 0 on a narrower scope."
    )


def test_suppressions_stay_where_they_are_accounted_for() -> None:
    found: dict[str, int] = {}
    for path in sorted(_SRC.rglob("*.py")):
        count = len(_SUPPRESSION.findall(path.read_text(encoding="utf-8")))
        if count:
            found[str(path.relative_to(_SRC))] = count

    assert found == _ALLOWED_SUPPRESSIONS, (
        f"pyright suppressions in src/ changed: expected {_ALLOWED_SUPPRESSIONS}, "
        f"found {found}. A suppression is the other way to keep the tree at 0 "
        "errors without fixing anything, so each one is accounted for by file and "
        "count. If the new one is a genuine framework limitation, add it here with "
        "its reason; if it is not, fix the finding instead."
    )
