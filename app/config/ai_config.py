"""AI / Ollama configuration.

These options control how the ChatbotService talks to Ollama. The system
gracefully degrades to deterministic, rule-based explanations when Ollama
is unreachable, so these values are advisory.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AIConfig:
    base_url: str = os.getenv("STACKWISE_OLLAMA_URL", "http://localhost:11434")
    model: str = os.getenv("STACKWISE_OLLAMA_MODEL", "llama3.2")
    request_timeout_seconds: float = float(os.getenv("STACKWISE_OLLAMA_TIMEOUT", "30"))
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
