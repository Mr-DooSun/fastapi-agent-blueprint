"""The *enabled* half of every optional-infra Selector (#330).

`test_optional_infra.py` covers the disabled half. Nothing covered the enabled
half, because the only technique available — monkeypatching `settings` after
import — cannot set provider kwargs: they are captured when the class body runs.
Worse, it *can* flip the branch, so a test written that way returns the right
adapter type wired with `None` and passes.

Every assertion here therefore checks the **configured value reached the object**,
not just its type. See `tests/support/container_env.py`.

These spawn a subprocess each. That is the cost of asking a question the
in-process suite structurally cannot answer, and it is why this file is scoped to
wiring contracts rather than behaviour.
"""

from __future__ import annotations

import pytest

from tests.support.container_env import boot_fails, resolve_in_env

pytestmark = pytest.mark.slow

SLACK = "https://hooks.slack.com/services/T/B/BASE"
ALERTS = "https://hooks.slack.com/services/T/B/ALERTS"
MONITORING = "https://hooks.slack.com/services/T/B/MONITORING"
DISCORD = "https://discord.com/api/webhooks/123456789012345678/abcdefgh"

_ADAPTER_URL = """
client = container.notification_client()
result = {"type": type(client).__name__, "url": getattr(client, "_webhook_url", None)}
"""


class TestNotificationClientEnabled:
    def test_slack_adapter_receives_the_configured_url(self):
        out = resolve_in_env(
            {"NOTIFICATION_PROVIDER": "slack", "SLACK_WEBHOOK_URL": SLACK},
            _ADAPTER_URL,
        )
        assert out["type"] == "SlackNotificationAdapter"
        # The assertion that a monkeypatch-based test cannot make: the *value*.
        assert out["url"] == SLACK

    def test_discord_adapter_receives_the_configured_url(self):
        out = resolve_in_env(
            {"NOTIFICATION_PROVIDER": "discord", "DISCORD_WEBHOOK_URL": DISCORD},
            _ADAPTER_URL,
        )
        assert out["type"] == "DiscordNotificationAdapter"
        assert out["url"] == DISCORD


class TestNotificationRoutingEnabled:
    """#286's routing graph, resolved for real for the first time."""

    def test_router_is_none_without_the_threshold(self):
        out = resolve_in_env(
            {"NOTIFICATION_PROVIDER": "slack", "SLACK_WEBHOOK_URL": SLACK},
            'result = {"router": repr(container.notification_router())}',
        )
        assert out["router"] == "None"

    def test_each_tier_receives_its_own_url(self):
        out = resolve_in_env(
            {
                "NOTIFICATION_PROVIDER": "slack",
                "SLACK_WEBHOOK_URL": SLACK,
                "NOTIFICATION_WARNING_THRESHOLD": "400",
                "NOTIFICATION_CRITICAL_WEBHOOK_URL": ALERTS,
                "NOTIFICATION_WARNING_WEBHOOK_URL": MONITORING,
            },
            """
router = container.notification_router()
result = {
    "critical": getattr(router.resolve(500), "_webhook_url", None),
    "warning": getattr(router.resolve(404), "_webhook_url", None),
    "below": router.resolve(399),
}
""",
        )
        assert out["critical"] == ALERTS
        assert out["warning"] == MONITORING
        assert out["below"] is None, "below the warning band must not dispatch"

    def test_unset_tier_url_falls_back_to_the_single_target(self):
        out = resolve_in_env(
            {
                "NOTIFICATION_PROVIDER": "slack",
                "SLACK_WEBHOOK_URL": SLACK,
                "NOTIFICATION_WARNING_THRESHOLD": "400",
                "NOTIFICATION_CRITICAL_WEBHOOK_URL": ALERTS,
            },
            """
router = container.notification_router()
result = {
    "critical": getattr(router.resolve(500), "_webhook_url", None),
    "warning": getattr(router.resolve(404), "_webhook_url", None),
}
""",
        )
        assert out["critical"] == ALERTS
        assert out["warning"] == SLACK, "an unset tier degrades to the single target"

    def test_disabled_path_emits_one_disabled_warning(self):
        """Three client Selectors share one Noop Singleton, so the warning is
        logged once regardless of tier count. Pinned in-process elsewhere; pinned
        here against a real container resolve."""
        out = resolve_in_env(
            {},
            """
from structlog.testing import capture_logs
import structlog
structlog.reset_defaults()
with capture_logs() as logs:
    container.error_notifier()
result = {"warnings": sum(
    1 for r in logs if r.get("event") == "notification_client_disabled")}
""",
        )
        assert out["warnings"] == 1


class TestBootValidationRunsForReal:
    """`model_validator` fires at construction, so a post-import monkeypatch never
    re-runs it. These are the rejections `config.py` promises."""

    @pytest.mark.parametrize(
        "env,expected",
        [
            (
                {"NOTIFICATION_PROVIDER": "slack"},
                "slack_webhook_url",
            ),
            (
                {"NOTIFICATION_PROVIDER": "nope", "SLACK_WEBHOOK_URL": SLACK},
                "notification_provider",
            ),
            (
                {
                    "NOTIFICATION_PROVIDER": "slack",
                    "SLACK_WEBHOOK_URL": SLACK,
                    "NOTIFICATION_WARNING_THRESHOLD": "500",
                },
                "NOTIFICATION_WARNING_THRESHOLD",
            ),
            (
                {
                    "NOTIFICATION_PROVIDER": "slack",
                    "SLACK_WEBHOOK_URL": SLACK,
                    "NOTIFICATION_CRITICAL_WEBHOOK_URL": ALERTS,
                },
                "NOTIFICATION_WARNING_THRESHOLD",
            ),
            (
                {"NOTIFICATION_CRITICAL_WEBHOOK_URL": ALERTS},
                "NOTIFICATION_PROVIDER",
            ),
        ],
        ids=[
            "provider-without-url",
            "unknown-provider",
            "threshold-overlap",
            "tier-url-without-threshold",
            "tier-url-without-provider",
        ],
    )
    def test_rejected_at_boot(self, env, expected):
        err = boot_fails(env)
        assert err is not None, f"expected boot to fail for {env}"
        assert expected in err, f"error did not mention {expected}:\n{err}"

    def test_a_complete_routing_config_boots(self):
        assert (
            boot_fails(
                {
                    "NOTIFICATION_PROVIDER": "slack",
                    "SLACK_WEBHOOK_URL": SLACK,
                    "NOTIFICATION_WARNING_THRESHOLD": "400",
                    "NOTIFICATION_CRITICAL_WEBHOOK_URL": ALERTS,
                    "NOTIFICATION_WARNING_WEBHOOK_URL": MONITORING,
                }
            )
            is None
        )


class TestTheHarnessItself:
    """If this regresses, every assertion above silently becomes a type check."""

    def test_kwargs_track_the_environment(self):
        """The exact false-green the harness exists to prevent: a post-import
        monkeypatch yields the right adapter type with a None URL."""
        a = resolve_in_env(
            {"NOTIFICATION_PROVIDER": "slack", "SLACK_WEBHOOK_URL": ALERTS},
            _ADAPTER_URL,
        )
        b = resolve_in_env(
            {"NOTIFICATION_PROVIDER": "slack", "SLACK_WEBHOOK_URL": MONITORING},
            _ADAPTER_URL,
        )
        assert a["url"] == ALERTS
        assert b["url"] == MONITORING
        assert a["url"] != b["url"], "kwargs are not tracking the environment"

    def test_parent_environment_does_not_leak(self, monkeypatch):
        monkeypatch.setenv("NOTIFICATION_PROVIDER", "discord")
        monkeypatch.setenv("DISCORD_WEBHOOK_URL", DISCORD)
        out = resolve_in_env(
            {}, 'result = {"t": type(container.notification_client()).__name__}'
        )
        assert out["t"] == "NoopNotificationClient", (
            "the parent process env leaked into the probe"
        )
