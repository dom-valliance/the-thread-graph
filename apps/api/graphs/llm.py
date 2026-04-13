from __future__ import annotations

from langchain_anthropic import ChatAnthropic

MODEL = "claude-sonnet-4-20250514"


def get_llm(max_tokens: int = 4096, **kwargs: object) -> ChatAnthropic:
    """Create a ChatAnthropic instance with standard settings.

    Pass ``anthropic_api_key`` to provide the key explicitly rather
    than reading from the environment.
    """
    return ChatAnthropic(
        model=MODEL,
        max_tokens=max_tokens,
        max_retries=5,
        **kwargs,
    )
