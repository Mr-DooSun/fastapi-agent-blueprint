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


async def _register(client: AsyncClient, suffix: str) -> str:
    resp = await client.post(
        "/v1/auth/register",
        json={
            "username": f"rl{suffix}",
            "fullName": "RL User",
            "email": f"rl{suffix}@example.com",
            "password": "secret",
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["data"]["accessToken"]


@pytest.mark.asyncio
async def test_rate_limit_is_per_user_not_shared():
    """User A exhausting their bucket must NOT throttle user B. The limiter keys
    off the real Bearer token's `sub` via UserIdentityMiddleware (independent of
    the get_current_user override), so two real tokens get two buckets."""
    async with _client() as client:
        token_a = await _register(client, "aaa")
        token_b = await _register(client, "bbb")
        headers_a = {"Authorization": f"Bearer {token_a}"}
        headers_b = {"Authorization": f"Bearer {token_b}"}

        body = {"text": "hello", "categories": ["a", "b"]}
        # Exhaust user A (limit = 3).
        a_statuses = [
            (
                await client.post("/v1/classify", json=body, headers=headers_a)
            ).status_code
            for _ in range(4)
        ]
        # User B's first call must still succeed.
        b_first = await client.post("/v1/classify", json=body, headers=headers_b)

    assert a_statuses[3] == 429, a_statuses
    assert b_first.status_code == 200, b_first.text
