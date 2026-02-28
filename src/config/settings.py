"""
Application settings loaded from environment variables.
Centralized configuration for the AI Debate System.
"""

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv


@dataclass(frozen=True)
class LLMSettings:
    """Configuration for the LLM provider."""

    api_key: str
    model_name: str = "gemini-2.5-flash"
    temperature: float = 0.7
    top_p: float = 0.95
    default_max_tokens: int = 2048
    judge_max_tokens: int = 2560


@dataclass(frozen=True)
class DebateSettings:
    """Configuration for debate session parameters."""

    max_rounds: int = 3
    enable_streaming: bool = True
    enable_neutral_agent: bool = True
    language: str = "vi"


@dataclass(frozen=True)
class AppSettings:
    """Root configuration container."""

    llm: LLMSettings
    debate: DebateSettings = field(default_factory=DebateSettings)


def load_settings(env_path: str | None = None) -> AppSettings:
    """Load settings from environment variables.

    Raises:
        ValueError: If required environment variables are missing.
    """
    load_dotenv(dotenv_path=env_path)

    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in the environment.")

    model_name = os.getenv("MODEL_NAME", "gemini-2.5-flash")
    temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    top_p = float(os.getenv("LLM_TOP_P", "0.95"))
    default_max_tokens = int(os.getenv("LLM_MAX_TOKENS", "4096"))

    max_rounds = int(os.getenv("DEBATE_MAX_ROUNDS", "3"))
    enable_streaming = os.getenv("DEBATE_STREAMING", "true").lower() == "true"
    enable_neutral = os.getenv("DEBATE_ENABLE_NEUTRAL", "true").lower() == "true"

    llm_settings = LLMSettings(
        api_key=api_key,
        model_name=model_name,
        temperature=temperature,
        top_p=top_p,
        default_max_tokens=default_max_tokens,
    )

    debate_settings = DebateSettings(
        max_rounds=max_rounds,
        enable_streaming=enable_streaming,
        enable_neutral_agent=enable_neutral,
    )

    return AppSettings(llm=llm_settings, debate=debate_settings)
