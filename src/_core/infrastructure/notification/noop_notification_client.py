from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class NoopNotificationClient:
    """No-op fallback used when no NOTIFICATION_PROVIDER is configured.

    Lets ``ErrorNotifier`` run unconditionally regardless of whether Slack/
    Discord is wired up. Logs once at construction so operators know error
    alerts are not actually being delivered.
    """

    def __init__(self) -> None:
        logger.warning(
            "Error notification client disabled — set NOTIFICATION_PROVIDER + "
            "SLACK_WEBHOOK_URL/DISCORD_WEBHOOK_URL to enable Slack/Discord alerts."
        )

    async def send(self, message: str) -> None:
        logger.info("notification_suppressed message=%r", message)
