"""AI / Ollama configuration.

These options control how the ChatbotService talks to Ollama. The system
gracefully degrades to deterministic, rule-based explanations when Ollama
is unreachable, so these values are advisory.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


def _env_or_default(name: str, default: str) -> str:
    value = os.getenv(name)
    return value.strip() if isinstance(value, str) and value.strip() else default


def _env_or_fallback(*names: str, default: str) -> str:
    for name in names:
        value = os.getenv(name)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return default


@dataclass(frozen=True)
class AIConfig:
    base_url: str = _env_or_fallback("OLLAMA_BASE_URL", "STACKWISE_OLLAMA_URL", default="http://localhost:11434")
    model: str = _env_or_fallback("OLLAMA_MODEL", "STACKWISE_OLLAMA_MODEL", default="llama3.2")
    request_timeout_seconds: float = float(
        _env_or_fallback("OLLAMA_TIMEOUT", "STACKWISE_OLLAMA_TIMEOUT", default="180")
    )
    num_ctx: int = int(_env_or_fallback("OLLAMA_NUM_CTX", "STACKWISE_OLLAMA_NUM_CTX", default="8192"))
    num_predict: int = int(
        _env_or_fallback("OLLAMA_NUM_PREDICT", "STACKWISE_OLLAMA_NUM_PREDICT", default="4096")
    )
    enable_streaming: bool = os.getenv("STACKWISE_OLLAMA_STREAM", "true").lower() == "true"
    enable_llm_explanations: bool = (
        os.getenv("STACKWISE_LLM_EXPLAIN", "true").lower() == "true"
    )

    system_prompt: str = (
        "You are StackWise AI, a senior software architect and educator. "
        "You help students and developers choose programming languages, frameworks, "
        "and SDLC models for their projects. You explain concepts clearly, in a "
        "friendly, beginner-aware tone, with concrete examples and actionable advice. "
        "You never invent libraries or frameworks. You are concise, structured, and warm."
    )


def get_ai_config() -> AIConfig:
    return AIConfig()
