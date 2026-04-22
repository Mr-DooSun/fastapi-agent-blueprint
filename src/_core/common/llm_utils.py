from __future__ import annotations

from typing import NoReturn

from src._core.exceptions.llm_exceptions import (
    LLMAuthenticationException,
    LLMContextLengthExceededException,
    LLMException,
    LLMModelNotFoundException,
    LLMRateLimitException,
)

_RATE_LIMIT_NAMES = frozenset(
    {
        "ratelimiterror",
        "ratelimitexception",
        "throttlingexception",
        "toomanyrequestsexception",
        "throttlederror",
        "quotaexceeded",
    }
)
_AUTH_NAMES = frozenset(
    {
        "authenticationerror",
        "unauthorizederror",
        "permissiondeniederror",
        "invalidapikeyerror",
        "authorizationerror",
    }
)
_CONTEXT_NAMES = frozenset(
    {
        "contextlengtherror",
        "contextlengthexceeded",
        "maxtokensexceeded",
    }
)
_NOT_FOUND_NAMES = frozenset(
    {
        "modelnotfounderror",
        "modelnotfoundexception",
    }
)


def map_llm_error(exc: Exception) -> NoReturn:
    """Map PydanticAI/provider LLM exceptions to domain LLM exceptions.

    Inspects exception class name first (provider SDK class names are stable),
    then falls back to string matching for wrapped exceptions.
    Always raises — return type is NoReturn.
    """
    type_name = type(exc).__name__.lower().replace("_", "")
    error_str = str(exc).lower()

    if (
        type_name in _RATE_LIMIT_NAMES
        or "throttl" in error_str
        or ("rate" in error_str and "limit" in error_str)
    ):
        raise LLMRateLimitException() from exc
    if (
        type_name in _AUTH_NAMES
        or "authentication" in error_str
        or "unauthorized" in error_str
    ):
        raise LLMAuthenticationException() from exc
    if type_name in _CONTEXT_NAMES or (
        "context" in error_str and ("length" in error_str or "window" in error_str)
    ):
        raise LLMContextLengthExceededException() from exc
    if type_name in _NOT_FOUND_NAMES or (
        "model" in error_str and "not found" in error_str
    ):
        raise LLMModelNotFoundException() from exc

    raise LLMException(
        status_code=502,
        message="LLM operation failed",
        error_code="LLM_OPERATION_FAILED",
    ) from exc
