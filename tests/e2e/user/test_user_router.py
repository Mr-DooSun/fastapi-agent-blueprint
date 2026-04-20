import pytest
from httpx import ASGITransport, AsyncClient

from src._apps.server.app import app


@pytest.mark.asyncio
async def test_create_user():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost"
    ) as client:
        response = await client.post(
            "/v1/user",
            json={
                "username": "e2euser",
                "fullName": "E2E User",
                "email": "e2e@example.com",
                "password": "secret",
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["username"] == "e2euser"
    assert "password" not in data["data"]


@pytest.mark.asyncio
async def test_get_users():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost"
    ) as client:
        response = await client.get("/v1/users")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)
