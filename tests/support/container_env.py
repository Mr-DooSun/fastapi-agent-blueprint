"""Resolve a `CoreContainer` under an arbitrary environment (#330).

`CoreContainer` is a `DeclarativeContainer`, so every provider's kwargs are
evaluated **once, when the class body runs at import time**. A selector
*function* re-reads `settings` on each resolve, but the values already baked
into the `enabled` branch never change again.

That split is the trap this module exists to close. Monkeypatching `settings`
after import flips the branch but not the kwargs:

    settings.notification_provider = "slack"
    settings.slack_webhook_url     = "https://hooks.slack.com/services/T/B/REAL"

    CoreContainer().notification_client()
      -> SlackNotificationAdapter      # the branch moved
      -> webhook_url is None           # the kwarg did not

A test written that way asserts `isinstance(..., SlackNotificationAdapter)`,
passes, and has verified nothing about the configuration. A green test proving
the wrong thing is worse than a missing one — which is why no test in this repo
had ever resolved the enabled half of an optional-infra Selector before now.

The only way to get a truthful answer is to set the environment **before**
`src._core.config` is imported. Doing that in-process would mean reimporting a
module graph the rest of the suite already holds references to, so this runs in
a subprocess instead: cheap enough for the handful of wiring assertions that
need it, and it cannot leak state into any other test.

`tests/unit/_core/test_config.py::_create_settings` uses the same
patch-then-import idea for `Settings` alone; this generalises it to the
container graph.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# The minimum an arbitrary env needs to satisfy Settings validation. Individual
# probes override these freely; they exist so callers only have to name the
# variables their own scenario is about.
BASE_ENV: dict[str, str] = {
    "ENV": "local",
    "ADMIN_STORAGE_SECRET": "a-real-admin-storage-secret-value-x",
    "DATABASE_ENGINE": "sqlite",
    "DATABASE_USER": "app",
    "DATABASE_PASSWORD": "db-s3cure-value",
    "DATABASE_HOST": "localhost",
    "DATABASE_PORT": "5432",
    "DATABASE_NAME": ":memory:",
}

# Anything the parent process exports would otherwise bleed into the child and
# silently change what a probe resolves. The child starts from BASE_ENV plus the
# caller's overrides only — never the developer's shell or `_env/.env`.
_PASSTHROUGH = ("PATH", "HOME", "LANG", "LC_ALL", "VIRTUAL_ENV", "PYTHONHASHSEED")


class ContainerProbeError(RuntimeError):
    """The probe process failed. Carries the child's stderr, which is where the
    real cause (a boot-validation rejection, an import error) actually is."""


def resolve_in_env(env: dict[str, str], body: str) -> dict:
    """Run `body` in a fresh process with `env` applied before any project import.

    `body` is Python source. It receives a module-level name `container`
    (a freshly built `CoreContainer`) and must assign a JSON-serialisable dict
    to `result`. Whatever it assigns is returned.

    Example — prove the *value* reached the adapter, not just its type::

        out = resolve_in_env(
            {"NOTIFICATION_PROVIDER": "slack",
             "SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/T/B/REAL"},
            '''
            client = container.notification_client()
            result = {"type": type(client).__name__,
                      "url": getattr(client, "_webhook_url", None)}
            ''',
        )
        assert out["url"].endswith("/REAL")   # the assertion that actually matters
    """
    script = (
        textwrap.dedent("""
        import json, sys
        from src._core.infrastructure.di.core_container import CoreContainer
        container = CoreContainer()
        result = None
    """)
        + textwrap.dedent(body)
        + textwrap.dedent("""
        sys.stdout.write("---PROBE---" + json.dumps(result))
    """)
    )

    child_env = {k: os.environ[k] for k in _PASSTHROUGH if k in os.environ}
    child_env["PYTHONPATH"] = str(REPO_ROOT)
    child_env.update(BASE_ENV)
    child_env.update(env)

    proc = subprocess.run(
        [sys.executable, "-c", script],
        cwd=REPO_ROOT,
        env=child_env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if proc.returncode != 0:
        raise ContainerProbeError(
            f"probe exited {proc.returncode}\n--- stderr ---\n{proc.stderr}"
        )
    marker = "---PROBE---"
    if marker not in proc.stdout:
        raise ContainerProbeError(
            f"probe produced no result\n--- stdout ---\n{proc.stdout}"
            f"\n--- stderr ---\n{proc.stderr}"
        )
    return json.loads(proc.stdout.split(marker, 1)[1])


def boot_fails(env: dict[str, str]) -> str | None:
    """Return the boot-validation error for `env`, or None if it boots.

    Settings validation is the other thing a post-import monkeypatch cannot
    exercise: `model_validator` runs at construction, so patching attributes
    afterwards never re-runs it.
    """
    child_env = {k: os.environ[k] for k in _PASSTHROUGH if k in os.environ}
    child_env["PYTHONPATH"] = str(REPO_ROOT)
    child_env.update(BASE_ENV)
    child_env.update(env)

    proc = subprocess.run(
        [sys.executable, "-c", "import src._core.config"],
        cwd=REPO_ROOT,
        env=child_env,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return None if proc.returncode == 0 else proc.stderr
