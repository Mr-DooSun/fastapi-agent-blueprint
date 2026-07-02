"""E2E: HTTP middleware contract (issue #2).

Covers the app-level middleware wired in ``src/_apps/server/bootstrap.py``:
CORS, X-Request-ID (asgi-correlation-id), and registration order. Regressions
here would silently break cross-origin requests, request tracing, or the
exception-handling/logging order the rest of the app depends on.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from src._apps.server.app import app


def _client() -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost")


# --- CORS ------------------------------------------------------------------
@pytest.mark.asyncio
async def test_cors_preflight_returns_allow_origin():
    async with _client() as client:
        response = await client.options(
            "/health",
            headers={
                "Origin": "http://example.com",
                "Access-Control-Request-Method": "GET",
            },
        )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://example.com"


@pytest.mark.asyncio
async def test_cors_headers_on_simple_request():
    async with _client() as client:
        response = await client.get("/health", headers={"Origin": "http://example.com"})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "*"


# --- X-Request-ID (asgi-correlation-id) ------------------------------------
@pytest.mark.asyncio
async def test_request_id_generated_when_absent():
    async with _client() as client:
        response = await client.get("/health")
    assert response.headers.get("X-Request-ID")  # a UUID4 hex is generated


@pytest.mark.asyncio
async def test_request_id_echoed_when_valid_uuid():
    # asgi-correlation-id's default validator requires a valid UUID4 hex;
    # a non-UUID incoming value is replaced with a freshly generated one,
    # so send a real UUID4 hex here to exercise the echo path.
    incoming = "0af7651916cd43dd8448eb211c80319c"
    async with _client() as client:
        response = await client.get("/health", headers={"X-Request-ID": incoming})
    assert response.headers.get("X-Request-ID") == incoming


# --- Registration order ----------------------------------------------------
def test_middleware_registration_order():
    # add_middleware() stores outermost-first (last added = index 0), matching
    # the bootstrap.py contract:
    #   Request -> CorrelationId -> RequestLog -> CORS -> TrustedHost -> App
    from asgi_correlation_id import CorrelationIdMiddleware
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.trustedhost import TrustedHostMiddleware

    from src._core.infrastructure.logging.request_log_middleware import (
        RequestLogMiddleware,
    )

    assert [m.cls for m in app.user_middleware] == [
        CorrelationIdMiddleware,
        RequestLogMiddleware,
        CORSMiddleware,
        TrustedHostMiddleware,
    ]
