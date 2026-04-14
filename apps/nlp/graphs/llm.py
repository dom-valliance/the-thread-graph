from __future__ import annotations

import logging
from typing import Awaitable, Callable, TypeVar

from anthropic import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    InternalServerError,
    RateLimitError,
)
from langchain_anthropic import ChatAnthropic
from tenacity import (
    AsyncRetrying,
    retry_if_exception,
    stop_after_attempt,
    wait_random_exponential,
)

logger = logging.getLogger(__name__)

MODEL = "claude-sonnet-4-20250514"

# Status codes worth retrying. 529 (Overloaded) is not a dedicated SDK exception
# class in this version, so we match by status_code on APIStatusError instead.
_RETRYABLE_STATUS_CODES = {429, 502, 503, 504, 529}
_ALWAYS_RETRY_TYPES = (
    RateLimitError,
    InternalServerError,
    APITimeoutError,
    APIConnectionError,
)


def _is_transient_llm_error(exc: BaseException) -> bool:
    if isinstance(exc, _ALWAYS_RETRY_TYPES):
        return True
    if isinstance(exc, APIStatusError):
        return getattr(exc, "status_code", None) in _RETRYABLE_STATUS_CODES
    return False

T = TypeVar("T")


def get_llm(max_tokens: int = 4096, **kwargs: object) -> ChatAnthropic:
    """Create a ChatAnthropic instance with standard settings.

    Reads ANTHROPIC_API_KEY from the environment by default.
    Pass ``anthropic_api_key`` to override.
    """
    return ChatAnthropic(
        model=MODEL,
        max_tokens=max_tokens,
        max_retries=10,
        **kwargs,
    )


async def with_llm_retry(
    call: Callable[[], Awaitable[T]],
    *,
    max_attempts: int = 6,
    multiplier: float = 4.0,
    max_wait: float = 60.0,
) -> T:
    """Wrap an async LLM call with overload-aware retry.

    The Anthropic SDK already retries internally with short waits (capped near
    8s). When the API is sustainedly overloaded, those retries exhaust before
    the API recovers. This helper sits outside the SDK and waits longer between
    attempts (jittered exponential, capped at ``max_wait`` seconds), so a brief
    overload window does not abort a long-running batch.
    """
    async for attempt in AsyncRetrying(
        retry=retry_if_exception(_is_transient_llm_error),
        stop=stop_after_attempt(max_attempts),
        wait=wait_random_exponential(multiplier=multiplier, max=max_wait),
        reraise=True,
        before_sleep=lambda rs: logger.warning(
            "LLM transient error (%s) — retrying in ~%.1fs (attempt %d/%d)",
            type(rs.outcome.exception()).__name__ if rs.outcome else "unknown",
            rs.next_action.sleep if rs.next_action else 0.0,
            rs.attempt_number,
            max_attempts,
        ),
    ):
        with attempt:
            return await call()
    raise RuntimeError("with_llm_retry exited without returning")  # unreachable
