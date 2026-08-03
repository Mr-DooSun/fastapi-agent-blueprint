"""Request bodies are bounded, on both paths a caller can use (#322).

Nothing bounded them before. FastAPI reads and JSON-parses the whole body before
validation — or even authentication — can reject it. Measured against
`POST /v1/user`, which requires an admin token:

    1MB  -> 401 in 0.05s
    16MB -> 401 in 0.07s
    64MB -> 401 in 0.28s      <- the body was read before the 401

The `Field(max_length=100)` bounds that shipped earlier in #322 cap how much
*work* a valid body triggers. This caps how much *body* the process holds.

Why the chunked case gets its own tests
--------------------------------------
A `Content-Length` check alone is not a control. HTTP/1.1 chunked encoding sends
no `Content-Length`, so a header-only check is skipped entirely by a caller who
omits it — verified against this app, `Content-Length present: False`. The
middleware therefore also counts streamed bytes.

Rejecting mid-stream is where the first implementation was wrong: responding from
the receive side while the app still intends to respond produces two
`http.response.start` messages. httpx's transport fails on
`assert not response_started`; uvicorn raises "Unexpected message". `send` is
wrapped so the app's late response is genuinely dropped, which the tests below
pin from both directions.
"""

from __future__ import annotations

import json

import pytest
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from src._core.infrastructure.http.body_size_middleware import BodySizeLimitMiddleware

LIMIT = 1024


def _build_app(*, max_bytes: int = LIMIT) -> Starlette:
    """A minimal app that reads the whole body, like a FastAPI route would."""

    async def echo(request: Request) -> JSONResponse:
        body = await request.body()
        return JSONResponse({"read": len(body)})

    app = Starlette(routes=[Route("/echo", echo, methods=["POST", "PUT", "GET"])])
    app.add_middleware(BodySizeLimitMiddleware, max_bytes=max_bytes)
    return app


@pytest.fixture
def client() -> TestClient:
    return TestClient(_build_app())


class TestTheContentLengthPath:
    def test_a_body_under_the_limit_passes_through(self, client):
        resp = client.post("/echo", content=b"x" * (LIMIT - 1))
        assert resp.status_code == 200
        assert resp.json()["read"] == LIMIT - 1

    def test_a_body_exactly_at_the_limit_passes(self, client):
        """The limit is a maximum, not a strict bound. Pinned because an
        off-by-one here silently rejects a documented-legal payload."""
        resp = client.post("/echo", content=b"x" * LIMIT)
        assert resp.status_code == 200

    def test_a_body_over_the_limit_is_rejected(self, client):
        resp = client.post("/echo", content=b"x" * (LIMIT + 1))
        assert resp.status_code == 413

    def test_the_rejection_body_matches_the_error_response_shape(self, client):
        """Clients parse every other error through `ErrorResponse`. This runs
        outside the exception handlers, so the shape is hand-rolled and worth
        pinning."""
        resp = client.post("/echo", content=b"x" * (LIMIT * 4))
        payload = json.loads(resp.text)
        assert payload["success"] is False
        assert payload["errorCode"] == "REQUEST_BODY_TOO_LARGE"
        assert payload["errorDetails"] is None
        assert str(LIMIT) in payload["message"]
        assert resp.headers["content-type"] == "application/json"

    def test_the_app_never_sees_an_oversized_body(self):
        """The point of the middleware: not just the status code, but that the
        handler was never invoked with the payload."""
        seen: list[int] = []

        async def record(request: Request) -> JSONResponse:
            body = await request.body()
            seen.append(len(body))
            return JSONResponse({"read": len(body)})

        app = Starlette(routes=[Route("/r", record, methods=["POST"])])
        app.add_middleware(BodySizeLimitMiddleware, max_bytes=LIMIT)

        resp = TestClient(app).post("/r", content=b"x" * (LIMIT * 8))
        assert resp.status_code == 413
        assert seen == [], f"the handler read {seen} bytes of a rejected body"


class TestTheChunkedPathWithNoContentLength:
    """The bypass a header-only check would leave open."""

    @staticmethod
    def _chunks(total: int, size: int = 256):
        sent = 0
        while sent < total:
            n = min(size, total - sent)
            yield b"x" * n
            sent += n

    def test_a_streamed_oversized_body_is_rejected(self, client):
        resp = client.post("/echo", content=self._chunks(LIMIT * 6))
        assert resp.status_code == 413

    def test_a_streamed_body_under_the_limit_passes(self, client):
        resp = client.post("/echo", content=self._chunks(LIMIT // 2))
        assert resp.status_code == 200
        assert resp.json()["read"] == LIMIT // 2

    def test_the_request_carried_no_content_length(self, client):
        """Precondition for the two tests above. If httpx ever starts buffering
        and setting Content-Length, they would silently stop covering the chunked
        path and only re-test the header check."""
        request = client.build_request("POST", "/echo", content=self._chunks(LIMIT * 6))
        assert not any(k.lower() == "content-length" for k in request.headers)

    def test_only_one_response_is_produced(self, client):
        """A regression guard for the actual bug in the first implementation.

        Rejecting from the receive side while the app is still going to respond
        sent two `http.response.start` messages. Starlette does not discard the
        second — httpx asserted `not response_started` and the request blew up
        rather than returning 413. A single clean 413 here IS that assertion.
        """
        resp = client.post("/echo", content=self._chunks(LIMIT * 6))
        assert resp.status_code == 413
        assert json.loads(resp.text)["errorCode"] == "REQUEST_BODY_TOO_LARGE"


class TestWhatIsDeliberatelyNotChecked:
    def test_zero_disables_enforcement(self):
        client = TestClient(_build_app(max_bytes=0))
        resp = client.post("/echo", content=b"x" * (LIMIT * 100))
        assert resp.status_code == 200, (
            "max_bytes=0 must disable the limit — it is the documented escape "
            "hatch for deployments where a reverse proxy already bounds bodies"
        )

    def test_bodyless_methods_skip_the_wrapper(self, client):
        """GET may legally carry a body but never meaningfully does here, and
        skipping those methods keeps the hot path free of two closures."""
        assert client.get("/echo").status_code == 200

    def test_a_malformed_content_length_falls_back_to_counting(self):
        """A bogus header must not be usable to skip the limit. Sent at the raw
        ASGI level because an HTTP client will not emit an invalid header."""
        import anyio

        app = _build_app()
        stack = app.build_middleware_stack()
        sent: list[dict] = []
        chunks = [b"x" * 512, b"x" * 512, b"x" * 512]

        async def receive():
            if chunks:
                return {
                    "type": "http.request",
                    "body": chunks.pop(0),
                    "more_body": bool(chunks),
                }
            return {"type": "http.request", "body": b"", "more_body": False}

        async def send(message):
            sent.append(message)

        scope = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "POST",
            "path": "/echo",
            "raw_path": b"/echo",
            "query_string": b"",
            "root_path": "",
            "scheme": "http",
            "headers": [(b"content-length", b"not-a-number")],
            "client": ("127.0.0.1", 1234),
            "server": ("testserver", 80),
        }
        anyio.run(stack, scope, receive, send)

        start = next(m for m in sent if m["type"] == "http.response.start")
        assert start["status"] == 413, (
            "a malformed Content-Length let an oversized body through"
        )


class TestTheExceptionGuardIsNarrow:
    """The reject path swallows the app's unwind exception. That suppression must
    apply ONLY after a rejection, or the middleware would hide every real error
    behind a 200-shaped silence."""

    def test_an_app_error_still_propagates_when_nothing_was_rejected(self):
        async def boom(request: Request) -> JSONResponse:
            raise RuntimeError("deliberate")

        app = Starlette(routes=[Route("/boom", boom, methods=["POST"])])
        app.add_middleware(BodySizeLimitMiddleware, max_bytes=LIMIT)

        with pytest.raises(RuntimeError, match="deliberate"):
            TestClient(app, raise_server_exceptions=True).post("/boom", content=b"ok")

    def test_an_app_error_on_a_small_body_is_not_turned_into_a_413(self):
        async def boom(request: Request) -> JSONResponse:
            await request.body()
            raise RuntimeError("deliberate")

        app = Starlette(routes=[Route("/boom", boom, methods=["POST"])])
        app.add_middleware(BodySizeLimitMiddleware, max_bytes=LIMIT)

        resp = TestClient(app, raise_server_exceptions=False).post(
            "/boom", content=b"x" * (LIMIT - 1)
        )
        assert resp.status_code == 500, (
            "a genuine handler error was masked; the exception guard is only "
            "meant to apply once a 413 has already been sent"
        )
