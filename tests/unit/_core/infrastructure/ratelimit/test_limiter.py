"""Unit tests for the rate-limit key function + limit value (#197 Phase 4 / #210)."""

from __future__ import annotations

from types import SimpleNamespace

from src._core.infrastructure.ratelimit.limiter import (
    _user_or_ip_key,
    rate_limit_value,
)


def _fake_request(*, user_id=None, client_host="1.2.3.4"):
    # slowapi's get_remote_address reads request.client.host
    return SimpleNamespace(
        state=SimpleNamespace(user_id=user_id)
        if user_id is not None
        else SimpleNamespace(),
        client=SimpleNamespace(host=client_host),
        headers={},
    )


def test_key_uses_user_id_when_present():
    req = _fake_request(user_id="42")
    assert _user_or_ip_key(req) == "user:42"


def test_key_falls_back_to_ip_when_no_user():
    req = _fake_request(client_host="9.9.9.9")
    assert _user_or_ip_key(req) == "ip:9.9.9.9"


def test_rate_limit_value_reads_settings(monkeypatch):
    from src._core import config

    monkeypatch.setattr(config.settings, "rate_limit_per_minute", 123)
    assert rate_limit_value() == "123/minute"


def test_limiter_enabled_mirrors_setting():
    # The shared limiter is constructed with enabled=settings.rate_limit_enabled
    # (default True). When disabled, slowapi's @limiter.limit decorator no-ops.
    from src._core.infrastructure.ratelimit.limiter import limiter

    assert limiter.enabled is True
