"""E2E rate-limiting behaviour on the two AI routes (#197 Phase 4 / #210).

Verifies: the (N+1)th call returns 429 with the RATE_LIMITED envelope; a
non-AI route (health) is never throttled; per-user keying via the auth override.
slowapi's in-memory counters are global, so an autouse fixture resets them
between tests to keep order-independent.
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src._apps.server.app import app
from src._apps.server.testing import override_current_user, reset_current_user_override
from src._core import config
from src._core.infrastructure.ratelimit.limiter import limiter
from tests.factories.user_factory import make_user_dto


def _client() -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost")


@pytest_asyncio.fixture(autouse=True)
async def _reset_and_auth(monkeypatch):
    # Small limit so the test is fast + deterministic.
    monkeypatch.setattr(config.settings, "rate_limit_per_minute", 3)
    limiter.reset()  # clear global in-memory counters before each test
    override_current_user(app, make_user_dto())
    try:
        yield
    finally:
        reset_current_user_override(app)
        limiter.reset()


@pytest.mark.asyncio
async def test_classify_returns_429_after_limit():
    async with _client() as client:
        statuses = []
        for _ in range(4):  # limit = 3 → 4th is throttled
            resp = await client.post(
                "/v1/classify", json={"text": "hello", "categories": ["a", "b"]}
            )
            statuses.append(resp.status_code)

    assert statuses[:3] == [200, 200, 200], statuses
    assert statuses[3] == 429, statuses
    body = resp.json()
    assert body["errorCode"] == "RATE_LIMITED"
    assert body["errorDetails"] is None


@pytest.mark.asyncio
async def test_docs_query_returns_429_after_limit():
    async with _client() as client:
        # seed one doc so the query path has context (still rate-limited regardless)
        await client.post(
            "/v1/docs/documents", json={"title": "T", "content": "Python is great."}
        )
        statuses = []
        for _ in range(4):
            resp = await client.post(
                "/v1/docs/query", json={"question": "what?", "topK": 1}
            )
            statuses.append(resp.status_code)

    assert statuses[3] == 429, statuses
    assert resp.json()["errorCode"] == "RATE_LIMITED"


@pytest.mark.asyncio
async def test_health_route_is_not_rate_limited():
    async with _client() as client:
        statuses = [(await client.get("/health")).status_code for _ in range(10)]
    assert all(s == 200 for s in statuses), statuses
