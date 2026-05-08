"""ChatbotService — Ollama integration with graceful fallback.

Talks to a local Ollama server using the **/api/generate** endpoint with
the **llama3.2** model. If Ollama isn't running, returns a clean,
helpful fallback message so the UI never crashes.

Every request and response is persisted to the ``chatbot_logs`` MySQL
table via the injected ``ChatbotLogRepository``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable, Iterator, Optional

import httpx

from app.config.ai_config import AIConfig
from app.requests.chat_request import ChatRequest
from app.utils.logger import get_logger

if TYPE_CHECKING:
    from app.repositories.chatbot_log_repository import ChatbotLogRepository

log = get_logger(__name__)

GENERATE_PATH = "/api/generate"
TAGS_PATH = "/api/tags"


@dataclass
class ChatTurn:
    role: str  # 'user' | 'assistant' | 'system'
    content: str


@dataclass
class ChatResponse:
    content: str
    model: str
    used_fallback: bool


class ChatbotService:
    def __init__(self, config: AIConfig, log_repository: "ChatbotLogRepository") -> None:
        self.config = config
        self.repo = log_repository

    # ---------- health ----------

    def is_available(self) -> bool:
        """Quick health check against Ollama's /api/tags."""
        try:
            with httpx.Client(timeout=2.0) as client:
                r = client.get(f"{self.config.base_url}{TAGS_PATH}")
                return r.status_code == 200
        except Exception:
            return False

    # ---------- chat (non-streaming) ----------

    def respond(
        self,
        user_id: int,
        request: ChatRequest,
        history: Optional[Iterable[ChatTurn]] = None,
    ) -> ChatResponse:
        if not request.is_valid():
            return ChatResponse(
                content="I couldn't read that. " + (request.first_error() or ""),
                model=self.config.model,
                used_fallback=True,
            )

        # Persist the user message before calling Ollama so it's logged
        # even if the model call fails.
        self.repo.append(user_id, "user", request.message)

        prompt = self._build_prompt(history, request.message)
        reply, used_fallback = self._call_generate(prompt)

        self.repo.append(user_id, "assistant", reply, model=self.config.model)
        return ChatResponse(content=reply, model=self.config.model, used_fallback=used_fallback)

    # ---------- chat (streaming) ----------

    def stream(
        self,
        user_id: int,
        request: ChatRequest,
        history: Optional[Iterable[ChatTurn]] = None,
    ) -> Iterator[str]:
        if not request.is_valid():
            yield "I couldn't read that. " + (request.first_error() or "")
            return

        self.repo.append(user_id, "user", request.message)
        prompt = self._build_prompt(history, request.message)

        collected: list[str] = []
        try:
            with httpx.stream(
                "POST",
                f"{self.config.base_url}{GENERATE_PATH}",
                json={
                    "model": self.config.model,
                    "prompt": prompt,
                    "system": self.config.system_prompt,
                    "stream": True,
                },
                timeout=self.config.request_timeout_seconds,
            ) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if not line:
                        continue
                    chunk = self._parse_generate_line(line)
                    if chunk:
                        collected.append(chunk)
                        yield chunk
        except Exception as exc:
            log.warning("Ollama stream failed: %s — using fallback.", exc)
            fb = self._fallback_reply(request.message)
            collected.append(fb)
            yield fb
        finally:
            full = "".join(collected).strip()
            if full:
                self.repo.append(user_id, "assistant", full, model=self.config.model)

    # ---------- recommendation explanation enrichment ----------

    def enrich_explanation(self, base_explanation: dict) -> str:
        """Optional: ask Ollama to rewrite a structured explanation in friendlier prose.

        Returns an empty string if Ollama is unavailable. The recommendation
        page falls back to the structured rule-based explanation in that case.
        """
        if not self.config.enable_llm_explanations:
            return ""
        if not self.is_available():
            return ""
        prompt = (
            "Rewrite this recommendation rationale as a clear, friendly paragraph for a "
            "developer. Keep it under 120 words. Do not add new claims. Structured input:\n\n"
            f"{base_explanation}"
        )
        reply, _ = self._call_generate(prompt)
        return reply.strip()

    # ---------- internals ----------

    def _build_prompt(
        self,
        history: Optional[Iterable[ChatTurn]],
        current_message: str,
    ) -> str:
        """Convert role-tagged history + current message into a single Ollama prompt."""
        pieces: list[str] = []
        if history:
            for turn in history:
                if turn.role == "user":
                    pieces.append(f"User: {turn.content}")
                elif turn.role == "assistant":
                    pieces.append(f"Assistant: {turn.content}")
        pieces.append(f"User: {current_message}")
        pieces.append("Assistant:")
        return "\n\n".join(pieces)

    def _call_generate(self, prompt: str) -> tuple[str, bool]:
        try:
            with httpx.Client(timeout=self.config.request_timeout_seconds) as client:
                resp = client.post(
                    f"{self.config.base_url}{GENERATE_PATH}",
                    json={
                        "model": self.config.model,
                        "prompt": prompt,
                        "system": self.config.system_prompt,
                        "stream": False,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                content = (data.get("response") or "").strip()
                if not content:
                    return self._fallback_reply(prompt), True
                return content, False
        except Exception as exc:
            log.info("Ollama unavailable (%s) — using deterministic fallback.", exc)
            return self._fallback_reply(prompt), True

    @staticmethod
    def _parse_generate_line(line: str) -> str:
        """Parse a single line from Ollama's streaming /api/generate endpoint.

        Each line is a JSON object like: ``{"response": "...", "done": false}``.
        """
        try:
            payload = json.loads(line)
        except Exception:
            return ""
        return payload.get("response", "") or ""

    @staticmethod
    def _fallback_reply(prompt: str) -> str:
        prompt_lower = (prompt or "").lower()

        if "language" in prompt_lower:
            return (
                "Choosing a programming language depends on what you're building, your team's "
                "experience, and the platform you're targeting.\n\n"
                "- For **web apps**, TypeScript with Next.js is a great default.\n"
                "- For **AI / data science**, Python is the standard.\n"
                "- For **mobile**, Flutter (Dart) covers iOS + Android in one codebase.\n"
                "- For **cloud back-ends at scale**, Go or Java/Kotlin are excellent.\n\n"
                "Tell me your project type, and I can be much more specific!"
            )
        if "framework" in prompt_lower:
            return (
                "Frameworks should match your language and goals. A few defaults I'd suggest:\n\n"
                "- **Next.js** for web apps and full-stack SaaS.\n"
                "- **FastAPI** for Python APIs (especially around AI/ML).\n"
                "- **Spring Boot** for enterprise Java back-ends.\n"
                "- **Flutter** for cross-platform mobile.\n\n"
                "Share the language you're using and I'll tailor this for your project."
            )
        if any(k in prompt_lower for k in ("agile", "waterfall", "kanban", "sdlc")):
            return (
                "Quick tour:\n\n"
                "- **Agile / Scrum** — sprints, ceremonies, evolving requirements.\n"
                "- **Kanban** — continuous flow with WIP limits, great for ops/support.\n"
                "- **Waterfall** — phase-gated, fixed-scope, document-heavy.\n"
                "- **DevOps / CD** — automated pipelines, ship often.\n\n"
                "Tell me about your team size, timeline, and how stable your requirements are, "
                "and I can recommend a model."
            )
        return (
            "I'm running in offline mode right now (Ollama not detected), so my answers are "
            "limited. Try starting Ollama with `ollama serve` and `ollama pull llama3.2`, "
            "or use the **Recommendation Generator** and **Learning Hub** — those work fully offline."
        )
