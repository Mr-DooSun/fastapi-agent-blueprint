"""E2E coverage for the `/docs` selector and OpenAPI handoff routes.

The selector page and `/openapi-download.json` route are dev-only. They support
the frontend handoff flow described in `docs/frontend-handoff.md`. Regressions
here would silently break the spec download button or expose the selector
outside dev — both surfaces other tooling depends on.
"""

import re

import pytest
from httpx import ASGITransport, AsyncClient

from src._apps.server.app import app


def _client() -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost")


@pytest.mark.asyncio
async def test_docs_selector_returns_html():
    async with _client() as client:
        response = await client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    body = response.text
    assert "API Documentation" in body
    assert "Stoplight Elements" in body
    assert "Scalar API Reference" in body
    assert "Recommended" in body
    assert "Share with Frontend" in body
    # The download card must point at the dedicated attachment route, not the
    # bare /openapi.json (which would render inline). Match the href tail to
    # stay agnostic to root_path prefixing.
    download_match = re.search(
        r'<a\s+href="([^"]*)"\s+class="docs-card"\s+download', body
    )
    assert download_match is not None
    assert download_match.group(1).endswith("/openapi-download.json")
    # Handoff guide link goes out to GitHub main; protect the path against
    # silent renames.
    assert "/docs/frontend-handoff.md" in body


@pytest.mark.asyncio
async def test_openapi_download_serves_attachment():
    async with _client() as client:
        response = await client.get("/openapi-download.json")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert response.headers["content-disposition"].startswith("attachment")
    assert "openapi.json" in response.headers["content-disposition"]
    spec = response.json()
    assert "openapi" in spec
    assert "paths" in spec
    assert spec["paths"], "OpenAPI paths block must not be empty"


@pytest.mark.asyncio
async def test_openapi_download_matches_openapi_json():
    async with _client() as client:
        baseline = await client.get("/openapi.json")
        download = await client.get("/openapi-download.json")
    assert baseline.status_code == 200
    assert download.status_code == 200
    assert baseline.json() == download.json()
