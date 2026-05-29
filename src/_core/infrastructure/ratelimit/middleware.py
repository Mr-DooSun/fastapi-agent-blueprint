"""Identity middleware for per-user rate limiting (#197 Phase 4 / #210).

Sets ``request.state.user_id`` from a best-effort, DB-free JWT decode so the
slowapi ``key_func`` can bucket per authenticated user. This is NOT an auth
gate — it never rejects a request; the route's ``Depends(get_current_user)``
remains the real authentication. An absent/invalid token simply leaves
``user_id`` unset, and the limiter falls back to IP keying.
"""

from __future__ import annotations

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp

_logger = structlog.stdlib.get_logger(__name__)


class UserIdentityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self._auth_service = None  # resolved lazily from app.state.container

    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("authorization", "")
        if auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1]
            service = self._resolve_auth_service(request)
            if service is not None:
                sub = service.extract_subject(token)
                if sub:
                    request.state.user_id = sub
        return await call_next(request)

    def _resolve_auth_service(self, request: Request):
        """Resolve AuthService once from the wired container on app.state.

        Cached on the instance after first resolution. Returns None (→ IP
        keying) if the container/provider is unavailable, so the middleware
        never breaks the request path.
        """
        if self._auth_service is not None:
            return self._auth_service
        try:
            container = request.app.state.container
            self._auth_service = container.auth_container.auth_service()
        except Exception:  # noqa: BLE001 - identity is best-effort; never raise
            _logger.debug("rate_limit_identity_unavailable")
            return None
        return self._auth_service
