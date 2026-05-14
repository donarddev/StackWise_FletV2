"""ExplanationService.

Builds the human-readable rationale shown on the recommendation page:

  - Why this language / framework / SDLC was chosen
  - Why the runners-up are less suited *for this specific project profile*
  - Trade-offs the user should be aware of
  - A friendly summary

Result is a structured dict so the UI can render sections separately and
the LLM (when available) can rewrite/enrich without losing structure.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.requests.recommendation_request import RecommendationRequest
    from app.services.recommendation_service import ScoredCandidate


class ExplanationService:
    def build(
        self,
        request: "RecommendationRequest",
        top_language: "ScoredCandidate",
        top_framework: "ScoredCandidate",
        top_sdlc: "ScoredCandidate",
        language_runners_up: list["ScoredCandidate"],
        framework_runners_up: list["ScoredCandidate"],
        sdlc_runners_up: list["ScoredCandidate"],
        confidence: int,
    ) -> dict:
        return {
            "summary": self._summary(request, top_language, top_framework, top_sdlc, confidence),
            "why_language": self._why(top_language, "language"),
            "why_framework": self._why(top_framework, "framework"),
            "why_sdlc": self._why(top_sdlc, "SDLC model"),
            "why_not_languages": self._why_not(top_language, language_runners_up, "language"),
            "why_not_frameworks": self._why_not(top_framework, framework_runners_up, "framework"),
            "why_not_sdlc": self._why_not(top_sdlc, sdlc_runners_up, "SDLC model"),
            "trade_offs": self._trade_offs(request, top_language, top_framework, top_sdlc),
        }

    # ---------- sections ----------

    @staticmethod
    def _summary(
        request: "RecommendationRequest",
        lang: "ScoredCandidate",
        fw: "ScoredCandidate",
        sdlc: "ScoredCandidate",
        confidence: int,
    ) -> str:
        return (
            f"For your {request.complexity.lower()} {request.project_type.lower()} "
            f"targeting {request.preferred_platform}, with a team of {request.team_size} and a "
            f"{request.timeline.lower()} timeline, StackWise recommends "
            f"{lang.name} + {fw.name}, delivered using {sdlc.name}. "
            f"This combination scored highest against your scalability, security, and experience "
            f"requirements (confidence: {confidence}/100)."
        )

    @staticmethod
    def _why(candidate: "ScoredCandidate", label: str) -> dict:
        return {
            "title": f"Why {candidate.name} as your {label}",
            "points": list(candidate.rationale) or [
                f"Top match across the weighted criteria for your project profile."
            ],
        }

    @staticmethod
    def _why_not(top: "ScoredCandidate", runners_up: list["ScoredCandidate"], label: str) -> list[dict]:
        items: list[dict] = []
        for ru in runners_up:
            items.append({
                "name": ru.name,
                "reason": (
                    f"{ru.name} is a strong {label}, but for *this* profile it scored "
                    f"{ru.score} vs {top.score} for {top.name}. "
                    + ("It's a great runner-up if you prefer it." if not ru.rationale
                       else "Highlights: " + "; ".join(ru.rationale[:2]))
                ),
            })
        return items

    @staticmethod
    def _trade_offs(
        request: "RecommendationRequest",
        lang: "ScoredCandidate",
        fw: "ScoredCandidate",
        sdlc: "ScoredCandidate",
    ) -> list[str]:
        notes: list[str] = []
        if request.development_experience == "Beginner":
            notes.append(
                f"{lang.name} was tuned for accessibility — but plan a learning ramp for any "
                f"production deployment (CI/CD, observability, security)."
            )
        if request.scalability_needs in {"Large user base", "Expected to grow fast"}:
            notes.append(
                "At your scalability target, invest in caching, async I/O, and a horizontal "
                "deployment story (containers + orchestration) early."
            )
        if request.security_requirements in {"High", "Sensitive user data", "Payment or financial data"}:
            notes.append(
                "Pair the framework's defaults with a dedicated threat model, dependency "
                "scanning, and secrets management — defaults alone aren't enough at this tier."
            )
        if request.timeline == "Less than 1 month":
            notes.append(
                f"With a sub-month timeline, lean on {fw.name}'s built-ins; resist custom "
                f"infra. Ship the boring path first."
            )
        if request.team_size.isdigit() and int(request.team_size) <= 4 and sdlc.name in {"Waterfall", "Spiral"}:
            notes.append(
                f"{sdlc.name} can feel heavy for a small team — keep ceremonies minimal and "
                f"focus on the planning artifacts that actually inform decisions."
            )
        if not notes:
            notes.append(
                "No major trade-offs detected for this configuration — proceed with confidence "
                "and revisit as the project evolves."
            )
        return notes
