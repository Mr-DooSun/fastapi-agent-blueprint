"""Kill-switch gating for rate limiting (#197 Phase 4 / #210).

Verifies RATE_LIMIT_ENABLED gates BOTH the limiter registration (app.state +
exception handler) and the UserIdentityMiddleware, so disabling it fully
bypasses rate limiting without touching the @limiter.limit decorator (which
also no-ops via Limiter(enabled=...)).
"""

from __future__ import annotations

from fastapi import FastAPI

from src._apps.server import bootstrap
from src._core import config
from src._core.infrastructure.ratelimit.middleware import UserIdentityMiddleware


def _middleware_classes(app: FastAPI) -> list[type]:
    return [m.cls for m in app.user_middleware]


def test_enabled_registers_limiter_and_identity_middleware(monkeypatch):
    monkeypatch.setattr(config.settings, "rate_limit_enabled", True)
    app = FastAPI()
    bootstrap._install_exception_handlers(app)
    bootstrap._install_middleware(app)

    assert getattr(app.state, "limiter", None) is not None
    assert UserIdentityMiddleware in _middleware_classes(app)


def test_disabled_skips_limiter_and_identity_middleware(monkeypatch):
    monkeypatch.setattr(config.settings, "rate_limit_enabled", False)
    app = FastAPI()
    bootstrap._install_exception_handlers(app)
    bootstrap._install_middleware(app)

    assert getattr(app.state, "limiter", None) is None
    assert UserIdentityMiddleware not in _middleware_classes(app)
