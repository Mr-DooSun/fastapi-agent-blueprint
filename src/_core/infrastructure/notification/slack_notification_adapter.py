from src._core.infrastructure.http.base_http_gateway import BaseHttpGateway
from src._core.infrastructure.http.http_client import HttpClient


class SlackNotificationAdapter(BaseHttpGateway):
    """Sends error alerts to a Slack Incoming Webhook.

    ``webhook_url`` is the full per-workspace webhook URL, so it is used
    directly as ``base_url`` and every send posts to the empty endpoint.
    """

    def __init__(self, http_client: HttpClient, webhook_url: str) -> None:
        super().__init__(http_client=http_client, base_url=webhook_url)

    async def send(self, message: str) -> None:
        await self._post("", json={"text": message})
