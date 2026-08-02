"""Contract tests for the LLM provider exception mapper (#323).

This module had **no tests**, and it is reached from
`generic_exception_handler` for *every* unhandled application exception. Its
message-substring heuristics therefore classified exceptions that have nothing
to do with an LLM provider. Probed at `d5c2a1d`:

    KeyError("unauthorized")                        -> 401 LLM_AUTH_FAILED
    RuntimeError("S3 bucket model-artifacts not found") -> 404 LLM_MODEL_NOT_FOUND
    TimeoutError("... after rate limit backoff")     -> 429 LLM_RATE_LIMITED

Each of those is a genuine 5xx returned to the client as a 4xx, which also
skips both `_logger.exception` and the error notification — so the
misclassification leaves no trace anywhere.

The fix gates classification on the exception actually originating from a
provider SDK. These tests pin both directions: provider errors still map, and
nothing else does.
"""

from __future__ import annotations

import pytest

from src._core.exceptions.llm_exceptions import (
    LLMAuthenticationException,
    LLMContextLengthExceededException,
    LLMModelNotFoundException,
    LLMRateLimitException,
)
from src._core.infrastructure.llm.error_mapper import try_map_llm_error


def _provider_exc(name: str, message: str, module: str = "openai"):
    """Build an exception that looks like it came from a provider SDK.

    Real provider classes are not importable here (`openai`, `anthropic` and
    `pydantic_ai` are optional extras), so the module is set explicitly — which
    is exactly the attribute the mapper gates on.
    """
    cls = type(name, (Exception,), {})
    cls.__module__ = module
    return cls(message)


class TestNonProviderExceptionsAreNeverMapped:
    """The regression this file exists for. Every case here reached a 4xx before."""

    @pytest.mark.parametrize(
        "exc",
        [
            KeyError("unauthorized"),
            RuntimeError("S3 bucket model-artifacts not found"),
            TimeoutError("connection timed out after rate limit backoff"),
            ValueError("throttling the ingest queue"),
            OSError("authentication database unreachable"),
            RuntimeError("context length of the audit log window exceeded"),
        ],
        ids=[
            "keyerror-unauthorized",
            "runtimeerror-model-not-found",
            "timeouterror-rate-limit",
            "valueerror-throttling",
            "oserror-authentication",
            "runtimeerror-context-length",
        ],
    )
    def test_builtin_exception_is_not_an_llm_error(self, exc):
        assert try_map_llm_error(exc) is None, (
            f"{type(exc).__name__}({exc!r}) was classified as an LLM error — it "
            "would be returned to the client as a 4xx, unlogged and unalerted"
        )

    def test_application_exception_is_not_mapped(self):
        from src._core.exceptions.base_exception import BaseCustomException

        exc = BaseCustomException(
            status_code=500, message="rate limit on the audit writer"
        )
        assert try_map_llm_error(exc) is None


class TestProviderExceptionsStillMap:
    """Precision must not cost the coverage the mapper exists for."""

    @pytest.mark.parametrize(
        "name,expected",
        [
            ("RateLimitError", LLMRateLimitException),
            ("ThrottlingException", LLMRateLimitException),
            ("AuthenticationError", LLMAuthenticationException),
            ("PermissionDeniedError", LLMAuthenticationException),
            ("ContextLengthExceeded", LLMContextLengthExceededException),
            ("ModelNotFoundError", LLMModelNotFoundException),
        ],
    )
    def test_provider_class_name_maps(self, name, expected):
        mapped = try_map_llm_error(_provider_exc(name, "upstream said no"))
        assert isinstance(mapped, expected)

    @pytest.mark.parametrize(
        "message,expected",
        [
            ("Rate limit reached for gpt-4o", LLMRateLimitException),
            ("ThrottlingException: too fast", LLMRateLimitException),
            ("invalid authentication credentials", LLMAuthenticationException),
            ("unauthorized: bad key", LLMAuthenticationException),
            (
                "This model's maximum context length is 8192",
                LLMContextLengthExceededException,
            ),
            (
                "The model gpt-9 does not exist / model not found",
                LLMModelNotFoundException,
            ),
        ],
    )
    def test_provider_message_still_maps(self, message, expected):
        """A provider error whose class name is not in the known sets is still
        classified from its message — that is the heuristic's purpose. It is now
        scoped to provider exceptions instead of applying to everything."""
        mapped = try_map_llm_error(_provider_exc("APIStatusError", message))
        assert isinstance(mapped, expected)

    @pytest.mark.parametrize(
        "module",
        ["openai", "anthropic", "botocore.errorfactory", "pydantic_ai.exceptions"],
    )
    def test_every_supported_provider_module_is_recognised(self, module):
        mapped = try_map_llm_error(
            _provider_exc("APIError", "Rate limit exceeded", module=module)
        )
        assert isinstance(mapped, LLMRateLimitException), (
            f"exceptions from {module} are not recognised as provider errors"
        )

    def test_bedrock_dynamic_exception_is_recognised(self):
        """Bedrock errors are generated at runtime by botocore, so they carry
        `__module__ == 'botocore.errorfactory'` and `ClientError` in their MRO.

        This is the case that decided the fix's shape: an earlier probe read the
        *metaclass* module and reported `builtins`, which would have made module
        gating look unusable for the one provider that matters most here.
        """
        botocore = pytest.importorskip("botocore")
        from botocore.session import get_session

        client = get_session().create_client(
            "bedrock-runtime",
            region_name="us-east-1",
            aws_access_key_id="x",
            aws_secret_access_key="y",
        )
        throttling = client.exceptions.ThrottlingException
        assert throttling.__module__.startswith("botocore")
        assert issubclass(throttling, botocore.exceptions.ClientError)

        exc = throttling(
            {"Error": {"Code": "ThrottlingException", "Message": "slow down"}},
            "InvokeModel",
        )
        assert isinstance(try_map_llm_error(exc), LLMRateLimitException)


class TestUnrecognisedProviderErrorFallsThrough:
    def test_provider_exception_with_no_signal_returns_none(self):
        """A provider error the mapper cannot classify must return None so the
        caller produces a logged, alerted 500 — not a guessed 4xx."""
        assert try_map_llm_error(_provider_exc("APIError", "internal error")) is None
