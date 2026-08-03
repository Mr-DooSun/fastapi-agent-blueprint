"""The full notification routing behaviour matrix (#327).

#286's channel routing went through four review rounds and was declared clean by
an 8-permutation × 7-status-code matrix — but that matrix lived in a review
comment, not in the suite. So the semantics the rounds established were protected
by nothing, which is a bad position from which to refactor the provider graph.

This file is that matrix, shipped. For every supported `NOTIFICATION_*`
combination it records, per status code, **which webhook URL** would receive the
alert (or that none would). URLs rather than object types: the type only says
"a Slack adapter", while the URL says *which channel*, which is the entire point
of routing.

Each row needs its own process. `CoreContainer`'s Selector branches capture
`settings.*` at class-body evaluation time, so post-import monkeypatching cannot
flip them — `tests/support/container_env.py` (built for exactly this in #330) runs
each permutation in a subprocess with the env applied before any project import.

These are `slow`: one subprocess per permutation.
"""

from __future__ import annotations

import pytest

from tests.support.container_env import boot_fails, resolve_in_env

pytestmark = pytest.mark.slow

BASE = "https://hooks.slack.com/services/T/B/BASE"
CRITICAL = "https://hooks.slack.com/services/T/B/CRIT"
WARNING = "https://hooks.slack.com/services/T/B/WARN"

# Chosen to straddle every boundary the router can have: below both tiers, at and
# above a 400 warning threshold, just under the 500 severity threshold, and at and
# above it.
STATUS_CODES = [200, 399, 400, 404, 499, 500, 502]

# What the router/notifier pair resolves for each status code, reported as the
# tail of the receiving webhook URL. `None` means "would not dispatch".
_RESOLVE_BODY_TEMPLATE = """
    notifier = container.error_notifier()
    router = container.notification_router()

    def target(status):
        client = router.resolve(status) if router is not None else notifier._client
        return getattr(client, "_webhook_url", None)

    codes = __CODES__
    result = {
        "floor": notifier._effective_min_threshold(),
        "router": type(router).__name__,
        "client_type": type(notifier._client).__name__
        if hasattr(notifier, "_client")
        else None,
        "targets": {
            str(status): (target(status) or "").rsplit("/", 1)[-1] or None
            for status in codes
        },
        "dispatches": {
            str(status): notifier._should_notify(status, "E_" + str(status))
            for status in codes
        },
    }
"""

_RESOLVE_BODY = _RESOLVE_BODY_TEMPLATE.replace("__CODES__", repr(STATUS_CODES))


def _matrix(env: dict[str, str]) -> dict:
    return resolve_in_env(env, _RESOLVE_BODY)


# --- permutations that boot -------------------------------------------------

ENABLED_NO_ROUTING = {
    "NOTIFICATION_PROVIDER": "slack",
    "SLACK_WEBHOOK_URL": BASE,
}
ROUTING_SHARED_TARGET = {**ENABLED_NO_ROUTING, "NOTIFICATION_WARNING_THRESHOLD": "400"}
ROUTING_CRITICAL_ONLY = {
    **ROUTING_SHARED_TARGET,
    "NOTIFICATION_CRITICAL_WEBHOOK_URL": CRITICAL,
}
ROUTING_WARNING_ONLY = {
    **ROUTING_SHARED_TARGET,
    "NOTIFICATION_WARNING_WEBHOOK_URL": WARNING,
}
ROUTING_BOTH_TARGETS = {
    **ROUTING_SHARED_TARGET,
    "NOTIFICATION_CRITICAL_WEBHOOK_URL": CRITICAL,
    "NOTIFICATION_WARNING_WEBHOOK_URL": WARNING,
}
DISABLED = {}


class TestTheSingleTargetPathIsUnchanged:
    """#17 behaviour: only `>= severity_threshold` dispatches, all to one URL.

    This is the row a provider-graph refactor is most likely to break, because it
    is the row that does NOT go through the router today.
    """

    def test_only_5xx_dispatches_and_always_to_the_base_url(self):
        out = _matrix(ENABLED_NO_ROUTING)
        assert out["floor"] == 500
        assert out["dispatches"] == {
            "200": False,
            "399": False,
            "400": False,
            "404": False,
            "499": False,
            "500": True,
            "502": True,
        }
        for status in ("500", "502"):
            assert out["targets"][status] == "BASE"


class TestRoutingWithNoPerTierOverrides:
    """`NOTIFICATION_WARNING_THRESHOLD` alone lowers the floor and splits the band,
    with both tiers landing on the single configured webhook."""

    def test_the_floor_drops_to_the_warning_threshold(self):
        out = _matrix(ROUTING_SHARED_TARGET)
        assert out["floor"] == 400
        assert out["dispatches"] == {
            "200": False,
            "399": False,
            "400": True,
            "404": True,
            "499": True,
            "500": True,
            "502": True,
        }

    def test_both_tiers_share_the_base_url(self):
        out = _matrix(ROUTING_SHARED_TARGET)
        for status in ("400", "404", "499", "500", "502"):
            assert out["targets"][status] == "BASE", status


class TestRoutingWithPerTierOverrides:
    @pytest.mark.parametrize(
        "env,expected",
        [
            (
                ROUTING_CRITICAL_ONLY,
                {"400": "BASE", "499": "BASE", "500": "CRIT", "502": "CRIT"},
            ),
            (
                ROUTING_WARNING_ONLY,
                {"400": "WARN", "499": "WARN", "500": "BASE", "502": "BASE"},
            ),
            (
                ROUTING_BOTH_TARGETS,
                {"400": "WARN", "499": "WARN", "500": "CRIT", "502": "CRIT"},
            ),
        ],
        ids=["critical-override", "warning-override", "both-overrides"],
    )
    def test_each_tier_resolves_to_its_own_channel(self, env, expected):
        out = _matrix(env)
        for status, tail in expected.items():
            assert out["targets"][status] == tail, (
                f"status {status} routed to {out['targets'][status]}, expected {tail}"
            )

    def test_below_both_tiers_never_dispatches(self):
        out = _matrix(ROUTING_BOTH_TARGETS)
        assert out["dispatches"]["200"] is False
        assert out["dispatches"]["399"] is False
        assert out["targets"]["200"] is None
        assert out["targets"]["399"] is None


class TestTheDisabledPath:
    def test_nothing_is_delivered_and_the_floor_is_the_default(self):
        out = _matrix(DISABLED)
        assert out["floor"] == 500
        # The Noop client has no webhook URL, which is what "delivered nowhere"
        # looks like from the outside.
        assert out["targets"]["500"] is None
        assert out["targets"]["502"] is None


class TestTheCombinationsThatMustNotBoot:
    """#315: a per-tier URL without the threshold used to boot and silently send
    everything to the base webhook. Pinned here so the collapse cannot relax it."""

    @pytest.mark.parametrize(
        "env",
        [
            {**ENABLED_NO_ROUTING, "NOTIFICATION_CRITICAL_WEBHOOK_URL": CRITICAL},
            {**ENABLED_NO_ROUTING, "NOTIFICATION_WARNING_WEBHOOK_URL": WARNING},
        ],
        ids=["critical-url-without-threshold", "warning-url-without-threshold"],
    )
    def test_a_per_tier_url_without_the_threshold_is_rejected(self, env):
        error = boot_fails(env)
        assert error is not None, "the combination booted; #315 has regressed"
        assert "NOTIFICATION_WARNING_THRESHOLD" in error or "Routing" in error
