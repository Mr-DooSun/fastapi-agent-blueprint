"""Per-user rate limiting for the LLM-invoking routes (#197 Phase 4 / #210).

A single shared slowapi ``Limiter`` keyed by the authenticated ``sub`` (set on
``request.state.user_id`` by :class:`UserIdentityMiddleware`), falling back to
the client IP for unauthenticated/invalid tokens. Applied via the
``@limiter.limit`` decorator on only the two AI routes (``/v1/docs/query``,
``/v1/classify``) — NOT globally, so admin UI / Swagger / login / health are
unaffected.

In-memory storage only (single-process). A Redis backend is a future addition
when a multi-replica deployment needs shared counters.
"""

from __future__ import annotations

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src._core.application.dtos.base_response import ErrorResponse
from src._core.config import settings


def _user_or_ip_key(request: Request) -> str:
    """Rate-limit bucket key: the authenticated user when known, else the IP.

    ``request.state.user_id`` is populated by ``UserIdentityMiddleware`` from a
    best-effort JWT decode. Authenticated traffic (the main path) keys by user;
    unauthenticated/invalid tokens collapse to an IP bucket.
    """
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return f"user:{user_id}"
    return f"ip:{get_remote_address(request)}"


def rate_limit_value() -> str:
    """Dynamic limit string read from settings at call time (so tests / env can
    override ``RATE_LIMIT_PER_MINUTE`` without re-importing)."""
    return f"{settings.rate_limit_per_minute}/minute"


# Shared singleton. ``enabled`` mirrors the kill-switch so the decorator no-ops
# when rate limiting is disabled even if a route is decorated.
limiter = Limiter(key_func=_user_or_ip_key, enabled=settings.rate_limit_enabled)


async def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """Map slowapi's ``RateLimitExceeded`` to the project's error envelope.

    Generic message + ``errorDetails=null`` (no limit internals leaked); the
    429 still flows through CorrelationId/RequestLog middleware (outermost).
    """
    content = jsonable_encoder(
        ErrorResponse(
            message="Rate limit exceeded. Please retry later.",
            error_code="RATE_LIMITED",
            error_details=None,
        )
    )
    return JSONResponse(status_code=429, content=content)
