"""Reject oversized request bodies before the app parses them (#322).

Nothing bounded request bodies. FastAPI reads and JSON-parses the whole body
before validation — or even authentication — can reject it, so an unauthenticated
caller could make the process allocate and parse an arbitrarily large document.
Measured against `POST /v1/user`, which requires an admin token:

    1MB  -> 401 in 0.05s
    16MB -> 401 in 0.07s
    64MB -> 401 in 0.28s      <- the body was read before the 401

The collection bounds from the same issue cap how much *work* a valid body can
trigger (`Field(max_length=100)` on the batch endpoints). This caps how much
*body* the process will hold at all.

Two enforcement points, and the second is the one that matters
--------------------------------------------------------------
A `Content-Length` check alone is not a control: HTTP/1.1 chunked transfer
encoding sends no `Content-Length`, and a caller who omits it skips a
header-only check entirely. Verified that httpx builds exactly such a request
against this app:

    64MB (chunked) -> Content-Length present: False

So this middleware also counts bytes as they stream and aborts mid-body. The
header check is kept because it is free and fails fast, before a single byte of
an over-long body is accepted.

What this does NOT guarantee
---------------------------
Two gaps, both measured, both deliberate. Neither re-introduces the parse-cost
problem above — in both the body is never read by anything — but a claim of
"every request is bounded" would be false, so:

- **The byte counter only runs when the app calls ``receive()``.** An endpoint
  that returns without reading the body is not bounded by it (the header check
  still applies). Nothing parses those bytes, so there is no allocation to
  prevent; they are simply discarded by the protocol server.
- **A CORS preflight never reaches this middleware.** ``CORSMiddleware`` sits
  outside it and answers ``OPTIONS`` + ``Access-Control-Request-Method`` itself.
  Measured against the shipped order: preflight with an 11-byte body against a
  10-byte limit returns 200, while a non-preflight ``OPTIONS`` returns 413. The
  placement is still the right trade: moving this middleware outside CORS would
  bound preflight bodies nobody reads, at the cost of the 413 losing the CORS
  headers a browser needs in order to read it.

If a deployment needs "no request over N bytes reaches the process at all", that
belongs at the ingress proxy. This middleware bounds what the *application* will
hold and parse.
"""

from __future__ import annotations

import structlog
from starlette.datastructures import Headers
from starlette.types import ASGIApp, Message, Receive, Scope, Send

_logger = structlog.stdlib.get_logger(__name__)

_HTTP_REQUEST_ENTITY_TOO_LARGE = 413


class _RejectionState:
    """Shared between the wrapped ``receive`` and ``send`` for one request.

    A plain object rather than a dict so the two closures cannot disagree about
    key names, and so `rejected` reads as the latch it is.
    """

    __slots__ = ("received", "rejected", "rejection_sent", "response_started")

    def __init__(self) -> None:
        self.received = 0
        self.rejected = False
        self.response_started = False
        # Distinct from `rejected`: when the app had already committed a
        # response we stop the body WITHOUT sending our own 413. Only a
        # response we actually sent licenses swallowing the app's exception.
        self.rejection_sent = False


class BodySizeLimitMiddleware:
    """Pure-ASGI middleware bounding the request body.

    Deliberately not a ``BaseHTTPMiddleware`` subclass: that base buffers the
    whole request into a ``Request`` object to hand a body to the endpoint, which
    is the exact allocation this exists to prevent. Working at the ASGI level lets
    the byte counter run against the raw ``receive`` stream and stop it partway.
    """

    def __init__(self, app: ASGIApp, *, max_bytes: int) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or self.max_bytes <= 0:
            await self.app(scope, receive, send)
            return

        state = _RejectionState()
        declared = self._declared_length(scope)
        if declared is not None and declared > self.max_bytes:
            await self._reject(
                scope, send, declared=declared, received=None, state=state
            )
            return

        # Both sides are wrapped. Rejecting mid-stream means responding from the
        # receive side while the app still intends to respond, and an ASGI server
        # rejects the second `http.response.start` — httpx's transport fails on
        # `assert not response_started`, and uvicorn raises "Unexpected message".
        # Guarding `send` is what actually makes "the app's response is
        # discarded" true; an earlier version only claimed it and crashed.
        try:
            await self.app(
                scope,
                self._counting_receive(scope, send, receive, state),
                self._guarded_send(send, state),
            )
        except Exception:
            # Only after we have already responded. Cutting the body off makes the
            # app unwind — Starlette turns our `http.disconnect` into
            # `ClientDisconnect` inside `await request.body()` — and that
            # exception has nowhere useful to go: the 413 is on the wire, so
            # letting it propagate would surface as a server error for a request
            # that was correctly rejected. If we have NOT rejected, the exception
            # is a real one and must keep propagating.
            if not state.rejection_sent:
                raise

    def _declared_length(self, scope: Scope) -> int | None:
        raw = Headers(scope=scope).get("content-length")
        if raw is None:
            return None
        try:
            return int(raw)
        except ValueError:
            # A malformed Content-Length is not ours to adjudicate; the protocol
            # layer or the app will reject it. Fall through to byte counting so a
            # bogus header cannot be used to skip the limit.
            return None

    def _counting_receive(
        self, scope: Scope, send: Send, receive: Receive, state: _RejectionState
    ) -> Receive:
        async def counting_receive() -> Message:
            if state.rejected:
                # The app is still reading. Keep telling it the client is gone so
                # it unwinds instead of blocking on a stream we stopped serving.
                return {"type": "http.disconnect"}

            message = await receive()
            if message["type"] != "http.request":
                return message

            state.received += len(message.get("body", b""))
            if state.received > self.max_bytes:
                state.rejected = True
                if state.response_started:
                    # A streaming endpoint can start responding while it is still
                    # reading. Its `http.response.start` is already on the wire, so
                    # emitting a 413 start here would be a *second* one, which ASGI
                    # servers refuse ("Unexpected message" on uvicorn). The status
                    # is no longer ours to set; all we can still do is stop feeding
                    # the body and let the response it already began finish.
                    _logger.warning(
                        "request_body_too_large_after_response_started",
                        http_method=scope.get("method"),
                        http_path=scope.get("path"),
                        limit_bytes=self.max_bytes,
                        received_bytes=state.received,
                    )
                    return {"type": "http.disconnect"}
                await self._reject(
                    scope, send, declared=None, received=state.received, state=state
                )
                return {"type": "http.disconnect"}
            return message

        return counting_receive

    def _guarded_send(self, send: Send, state: _RejectionState) -> Send:
        async def guarded_send(message: Message) -> None:
            if state.rejected:
                if state.response_started and message["type"] == "http.response.body":
                    # The app committed a response before we cut the body off, so
                    # its status is already on the wire and ours never went out.
                    # Its body frames must still flow or the client is left with
                    # headers and no body — a hung connection, which is a worse
                    # outcome than the oversized body. Only `http.response.start`
                    # is suppressed here, and only because a second one is an ASGI
                    # protocol violation.
                    await send(message)
                    return
                # We sent the 413. Whatever the app produces from a truncated
                # body — a 422, a 500 — must not become a second response.
                return
            if message["type"] == "http.response.start":
                state.response_started = True
            await send(message)

        return guarded_send

    async def _reject(
        self,
        scope: Scope,
        send: Send,
        *,
        declared: int | None,
        received: int | None,
        state: _RejectionState,
    ) -> None:
        _logger.warning(
            "request_body_too_large",
            http_method=scope.get("method"),
            http_path=scope.get("path"),
            limit_bytes=self.max_bytes,
            declared_bytes=declared,
            received_bytes=received,
        )
        # Hand-rolled rather than a JSONResponse: this runs outside the exception
        # handlers, and the payload deliberately mirrors ``ErrorResponse`` so a
        # client parses a 413 the same way it parses every other error. The limit
        # is included because it is configuration, not internal detail.
        body = (
            b'{"success":false,'
            b'"message":"Request body exceeds the maximum of '
            + str(self.max_bytes).encode()
            + b' bytes",'
            b'"errorCode":"REQUEST_BODY_TOO_LARGE",'
            b'"errorDetails":null}'
        )
        await send(
            {
                "type": "http.response.start",
                "status": _HTTP_REQUEST_ENTITY_TOO_LARGE,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode()),
                ],
            }
        )
        await send({"type": "http.response.body", "body": body, "more_body": False})
        state.rejection_sent = True
