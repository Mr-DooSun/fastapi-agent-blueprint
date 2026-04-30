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


@pytest.mark.asyncio
async def test_create_user_duplicate_returns_field_errors():
    payload = {
        "username": "e2edup",
        "fullName": "E2E Duplicate",
        "email": "e2edup@example.com",
        "password": "secret",
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost"
    ) as client:
        first = await client.post("/v1/user", json=payload)
        second = await client.post("/v1/user", json=payload)

    assert first.status_code == 200
    assert second.status_code == 409
    body = second.json()
    assert body["success"] is False
    assert body["errorCode"] == "USER_ALREADY_EXISTS"
    assert body["errorDetails"]["errors"] == [
        {
            "field": "username",
            "message": "username already exists",
            "type": "unique",
        },
        {
            "field": "email",
            "message": "email already exists",
            "type": "unique",
        },
    ]


@pytest.mark.asyncio
async def test_create_users_duplicate_payload_is_all_or_nothing():
    payload = [
        {
            "username": "e2ebatchdup",
            "fullName": "E2E Batch One",
            "email": "e2ebatch-one@example.com",
            "password": "secret",
        },
        {
            "username": "e2ebatchdup",
            "fullName": "E2E Batch Two",
            "email": "e2ebatch-two@example.com",
            "password": "secret",
        },
    ]

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost"
    ) as client:
        response = await client.post("/v1/users", json=payload)
        list_response = await client.get("/v1/users?pageSize=100")

    assert response.status_code == 422
    body = response.json()
    assert body["errorCode"] == "BUSINESS_VALIDATION_ERROR"
    assert body["errorDetails"]["errors"] == [
        {
            "field": "username",
            "message": "Duplicate username in request payload",
            "type": "duplicate",
        }
    ]
    usernames = {item["username"] for item in list_response.json()["data"]}
    assert "e2ebatchdup" not in usernames


@pytest.mark.asyncio
async def test_update_user_allows_own_email_and_rejects_another_users_email():
    first_payload = {
        "username": "e2eupdateone",
        "fullName": "E2E Update One",
        "email": "e2eupdateone@example.com",
        "password": "secret",
    }
    second_payload = {
        "username": "e2eupdatetwo",
        "fullName": "E2E Update Two",
        "email": "e2eupdatetwo@example.com",
        "password": "secret",
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost"
    ) as client:
        first = await client.post("/v1/user", json=first_payload)
        second = await client.post("/v1/user", json=second_payload)
        first_id = first.json()["data"]["id"]
        second_id = second.json()["data"]["id"]

        own_email = await client.put(
            f"/v1/user/{first_id}",
            json={"email": first_payload["email"]},
        )
        conflicting_email = await client.put(
            f"/v1/user/{second_id}",
            json={"email": first_payload["email"]},
        )

    assert first.status_code == 200
    assert second.status_code == 200
    assert own_email.status_code == 200
    assert conflicting_email.status_code == 409
    assert conflicting_email.json()["errorDetails"]["errors"] == [
        {
            "field": "email",
            "message": "email already exists",
            "type": "unique",
        }
    ]
