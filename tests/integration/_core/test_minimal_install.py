"""Minimal-install boot regression (#104, extends #101 acceptance criterion).

This test is meant to run in a CI environment that has done ``uv sync``
**without** any optional extras (no ``--extra admin``, no
``--extra pydantic-ai``, no ``--extra sqs``). The local dev machine
typically has extras installed and will simply not hit the "admin not
mounted" branch; the assertions in that case are relaxed accordingly.

Acceptance criterion (the load-bearing one for #104 Part 1):

- With ``nicegui`` uninstalled, the FastAPI app still imports cleanly,
  ``bootstrap_app`` logs an INFO message explaining the missing extra,
  and ``/api/health`` continues to serve. No admin routes are mounted.
"""

from __future__ import annotations

import importlib.util
import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src._core.config import settings

_has_nicegui = importlib.util.find_spec("nicegui") is not None


@pytest.fixture
def clean_optional_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Force every optional-infra Settings field to its ``disabled`` value."""
    for field in (
        "storage_type",
        "dynamodb_access_key",
        "s3vectors_access_key",
        "embedding_provider",
        "embedding_model",
        "llm_provider",
        "llm_model",
    ):
        monkeypatch.setattr(settings, field, None)
    monkeypatch.setattr(settings, "broker_type", None)


class TestMinimalInstall:
    def test_app_imports_without_admin_extra(self, clean_optional_env: None):
        """App imports regardless of whether ``nicegui`` is installed."""
        from src._apps.server.app import app

        assert app is not None

    def test_health_endpoint_serves(self, clean_optional_env: None):
        """The always-on health endpoint returns 200 with minimal infra.

        ``TrustedHostMiddleware`` is wired at app-import time with
        ``settings.allowed_hosts`` (default ``["localhost", "127.0.0.1"]``),
        so ``TestClient`` must be pointed at one of those hosts — its
        default ``testserver`` would be rejected with 400.
        """
        from src._apps.server.app import app

        with TestClient(app, base_url="http://localhost") as client:
            response = client.get("/api/health")
            assert response.status_code == 200

    @pytest.mark.skipif(_has_nicegui, reason="nicegui is installed locally")
    def test_admin_routes_absent_when_nicegui_missing(self, clean_optional_env: None):
        """When nicegui is not installed, admin routes are not mounted.

        This is the load-bearing assertion for #104 Part 1. On dev machines
        that have nicegui installed it is skipped — the CI minimal-install
        job is the authoritative runner.
        """
        from src._apps.server.app import app

        admin_paths = [
            str(route.path)  # type: ignore[attr-defined]
            for route in app.routes
            if hasattr(route, "path") and "/admin" in str(route.path)  # type: ignore[attr-defined]
        ]
        assert not admin_paths, f"Expected no /admin routes, found: {admin_paths}"

    @pytest.mark.skipif(_has_nicegui, reason="nicegui is installed locally")
    def test_maybe_bootstrap_admin_emits_skip_log(
        self, clean_optional_env: None, caplog: pytest.LogCaptureFixture
    ):
        """``_maybe_bootstrap_admin`` emits an INFO log when skipping.

        Users running ``uv sync`` without ``--extra admin`` should see the
        install hint in logs so the missing dashboard is not silent. Tests
        the helper directly rather than via the module-level ``app`` import
        so the log fires inside this test's ``caplog`` window regardless of
        which test ran first and whether ``src._apps.server.app`` is already
        cached in ``sys.modules``.
        """
        from src._apps.server.bootstrap import _maybe_bootstrap_admin

        caplog.set_level(logging.INFO, logger="src._apps.server.bootstrap")
        _maybe_bootstrap_admin(FastAPI())

        assert any(
            "Admin dashboard not mounted" in record.message
            and "uv sync --extra admin" in record.message
            for record in caplog.records
        )
