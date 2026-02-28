"""
Factory for creating LLM instances.
Centralizes model construction to avoid duplication across agents.
"""

from langchain_google_genai import ChatGoogleGenerativeAI

from config.settings import LLMSettings


def create_llm(
    settings: LLMSettings,
    *,
    streaming: bool = False,
    max_tokens: int | None = None,
) -> ChatGoogleGenerativeAI:
    """Create a configured ChatGoogleGenerativeAI instance.

    Args:
        settings: LLM configuration.
        streaming: Whether to enable token-level streaming.
        max_tokens: Override for max output tokens. Falls back to settings default.
    """
    return ChatGoogleGenerativeAI(
        model=settings.model_name,
        api_key=settings.api_key,
        temperature=settings.temperature,
        top_p=settings.top_p,
        max_output_tokens=max_tokens or settings.default_max_tokens,
        streaming=streaming,
    )
