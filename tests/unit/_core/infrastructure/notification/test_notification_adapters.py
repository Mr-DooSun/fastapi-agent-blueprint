"""Unit tests for the Slack/Discord notification adapters (#17): pins the
exact webhook payload shape each provider expects."""

from __future__ import annotations

from contextlib import asynccontextmanager
from unittest.mock import MagicMock

from src._core.infrastructure.notification.discord_notification_adapter import (
    DiscordNotificationAdapter,
)
from src._core.infrastructure.notification.slack_notification_adapter import (
    SlackNotificationAdapter,
)


class _FakeResponse:
    def __init__(self) -> None:
        self.raise_for_status = MagicMock()

    async def json(self):
        return {"ok": True}

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class _FakeSession:
    def __init__(self) -> None:
        self.post_calls: list[dict] = []

    def post(self, url, json=None, data=None, headers=None):
        self.post_calls.append(
            {"url": url, "json": json, "data": data, "headers": headers}
        )
        return _FakeResponse()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False


class _FakeHttpClient:
    def __init__(self) -> None:
        self.fake_session = _FakeSession()

    @asynccontextmanager
    async def session(self):
        yield self.fake_session


class TestSlackNotificationAdapter:
    async def test_send_posts_slack_text_payload(self):
        http_client = _FakeHttpClient()
        webhook_url = "https://hooks.slack.com/services/T/B/X"
        adapter = SlackNotificationAdapter(
            http_client=http_client, webhook_url=webhook_url
        )

        await adapter.send("boom")

        assert http_client.fake_session.post_calls == [
            {"url": webhook_url, "json": {"text": "boom"}, "data": None, "headers": {}}
        ]


class TestDiscordNotificationAdapter:
    async def test_send_posts_discord_content_payload(self):
        http_client = _FakeHttpClient()
        webhook_url = "https://discord.com/api/webhooks/1/token"
        adapter = DiscordNotificationAdapter(
            http_client=http_client, webhook_url=webhook_url
        )

        await adapter.send("boom")

        assert http_client.fake_session.post_calls == [
            {
                "url": webhook_url,
                "json": {"content": "boom"},
                "data": None,
                "headers": {},
            }
        ]
