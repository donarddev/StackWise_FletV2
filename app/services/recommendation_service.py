"""Recommendation engine.

Pure-Python, deterministic scoring engine that ranks programming languages,
frameworks, and SDLC models against a project request. Uses the
``knowledge_base`` profiles, applies dimension weights derived from the
request, and selects the top candidate plus alternatives for each
category.

This service composes specialized services (confidence, alternatives,
explanation) so each stays small and testable.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from app.models.recommendation import Recommendation
from app.requests.recommendation_request import RecommendationRequest
from app.services.knowledge_base import (
    FRAMEWORKS,
    LANGUAGES,
    SDLC_MODELS,
    FrameworkProfile,
    LanguageProfile,
    SDLCProfile,
)
from app.utils.logger import get_logger

if TYPE_CHECKING:
    from app.repositories.recommendation_repository import RecommendationRepository
    from app.services.alternative_recommendation_service import (
        AlternativeRecommendationService,
    )
    from app.services.chatbot_service import ChatbotService
    from app.services.confidence_score_service import ConfidenceScoreService
    from app.services.explanation_service import ExplanationService

log = get_logger(__name__)


# ---------- request weights ----------

_COMPLEXITY_WEIGHTS = {"Simple": 0.4, "Moderate": 0.7, "Complex": 1.0, "Highly Complex": 1.3}
_TEAM_WEIGHTS = {
    "Solo (1)": 0.4, "Small (2–4)": 0.6, "Medium (5–10)": 0.85,
    "Large (11–25)": 1.1, "Enterprise (25+)": 1.3,
}
_TIMELINE_WEIGHTS = {
    "Less than 1 month": 1.4, "1–3 months": 1.1, "3–6 months": 0.9,
    "6–12 months": 0.75, "More than 12 months": 0.6,
}
_SCALABILITY_WEIGHTS = {"Low": 0.4, "Medium": 0.7, "High": 1.1, "Massive": 1.4}
_SECURITY_WEIGHTS = {"Standard": 0.4, "Elevated": 0.7, "High": 1.1, "Critical": 1.4}
_EXPERIENCE_WEIGHTS = {"Beginner": 1.4, "Intermediate": 1.0, "Advanced": 0.7, "Expert": 0.5}


@dataclass
class ScoredCandidate:
    name: str
    score: float
    rationale: list[str]


@dataclass
class RecommendationOutcome:
    """The full recommendation result, post-engine."""

    recommended_language: str
    recommended_framework: str
    recommended_sdlc: str
    confidence_score: int

    language_candidates: list[ScoredCandidate]
    framework_candidates: list[ScoredCandidate]
    sdlc_candidates: list[ScoredCandidate]

    explanation: dict
    alternatives: dict

    def to_storage(self) -> dict:
        return {
            "recommended_language": self.recommended_language,
            "recommended_framework": self.recommended_framework,
            "recommended_sdlc": self.recommended_sdlc,
            "confidence_score": int(self.confidence_score),
            "explanation": self.explanation,
            "alternatives": self.alternatives,
        }


class RecommendationService:
    def __init__(
        self,
        recommendation_repository: "RecommendationRepository",
        confidence_score_service: "ConfidenceScoreService",
        alternative_service: "AlternativeRecommendationService",
        explanation_service: "ExplanationService",
        chatbot_service: "ChatbotService",
    ) -> None:
        self.repo = recommendation_repository
        self.confidence = confidence_score_service
        self.alternatives = alternative_service
        self.explanation = explanation_service
        self.chatbot = chatbot_service

    # ---------- public API ----------

    def generate(self, request: RecommendationRequest) -> RecommendationOutcome:
        languages = self._score_languages(request)
        frameworks = self._score_frameworks(request, top_language=languages[0].name)
        sdlc = self._score_sdlc(request)

        confidence = self.confidence.compute(languages, frameworks, sdlc, request)

        explanation = self.explanation.build(
            request=request,
            top_language=languages[0],
            top_framework=frameworks[0],
            top_sdlc=sdlc[0],
            language_runners_up=languages[1:3],
            framework_runners_up=frameworks[1:3],
            sdlc_runners_up=sdlc[1:3],
            confidence=confidence,
        )

        alternatives = self.alternatives.build(
            language_candidates=languages,
            framework_candidates=frameworks,
            sdlc_candidates=sdlc,
        )

        return RecommendationOutcome(
            recommended_language=languages[0].name,
            recommended_framework=frameworks[0].name,
            recommended_sdlc=sdlc[0].name,
            confidence_score=confidence,
            language_candidates=languages,
            framework_candidates=frameworks,
            sdlc_candidates=sdlc,
            explanation=explanation,
            alternatives=alternatives,
        )

    def save(self, user_id: int, request: RecommendationRequest, outcome: RecommendationOutcome) -> Recommendation:
        return self.repo.create(
            user_id=user_id,
            request=request.to_dict(),
            result=outcome.to_storage(),
        )

    def regenerate(self, user_id: int, recommendation_id: int) -> Optional[Recommendation]:
        prev = self.repo.find_by_id(recommendation_id)
        if not prev or prev.user_id != user_id:
            return None
        request = RecommendationRequest(
            project_name=prev.project_name,
            project_type=prev.project_type,
            project_goal=prev.project_goal,
            complexity=prev.complexity,
            team_size=prev.team_size,
            timeline=prev.timeline,
            scalability=prev.scalability,
            security=prev.security,
            platform=prev.platform,
            experience=prev.experience,
        )
        outcome = self.generate(request)
        new_rec = self.save(user_id, request, outcome)
        self.repo.add_history(user_id, new_rec.id, "regenerated")
        return new_rec

    # ---------- scoring (languages) ----------

    def _score_languages(self, req: RecommendationRequest) -> list[ScoredCandidate]:
        complexity = _COMPLEXITY_WEIGHTS.get(req.complexity, 1.0)
        team = _TEAM_WEIGHTS.get(req.team_size, 1.0)
        timeline = _TIMELINE_WEIGHTS.get(req.timeline, 1.0)
        scalability = _SCALABILITY_WEIGHTS.get(req.scalability, 1.0)
        security = _SECURITY_WEIGHTS.get(req.security, 1.0)
        experience = _EXPERIENCE_WEIGHTS.get(req.experience, 1.0)

        out: list[ScoredCandidate] = []
        for lp in LANGUAGES:
            score = 0.0
            rationale: list[str] = []

            # project type fit
            if req.project_type in lp.great_for_project_types:
                score += 25
                rationale.append(f"Strong fit for {req.project_type}.")
            else:
                score += 5

            # platform fit
            if req.platform in lp.great_for_platforms:
                score += 12
                rationale.append(f"Targets your {req.platform} platform natively.")
            else:
                score += 3

            # weighted dimension scores
            score += lp.runtime_performance * scalability * 1.2
            score += lp.scalability_ceiling * scalability * 1.0
            score += lp.security_maturity * security * 1.2
            score += lp.development_speed * timeline * 1.1
            score += lp.learning_curve_friendliness * experience * 1.0
            score += lp.type_safety * complexity * 0.8
            score += lp.ecosystem_breadth * 0.5
            score += min(team, 1.2) * lp.scalability_ceiling * 0.4

            # rationale highlights
            if lp.development_speed >= 9 and timeline >= 1.0:
                rationale.append("Excellent development speed for a tight timeline.")
            if lp.scalability_ceiling >= 9 and scalability >= 1.0:
                rationale.append("Scales comfortably for high-throughput workloads.")
            if lp.security_maturity >= 9 and security >= 1.0:
                rationale.append("Mature security posture suited to elevated requirements.")
            if lp.learning_curve_friendliness >= 8 and experience >= 1.0:
                rationale.append("Beginner-friendly enough for your team's experience.")

            out.append(ScoredCandidate(name=lp.name, score=round(score, 2), rationale=rationale))

        out.sort(key=lambda c: c.score, reverse=True)
        return out

    # ---------- scoring (frameworks) ----------

    def _score_frameworks(
        self,
        req: RecommendationRequest,
        top_language: str,
    ) -> list[ScoredCandidate]:
        timeline = _TIMELINE_WEIGHTS.get(req.timeline, 1.0)
        scalability = _SCALABILITY_WEIGHTS.get(req.scalability, 1.0)
        security = _SECURITY_WEIGHTS.get(req.security, 1.0)
        experience = _EXPERIENCE_WEIGHTS.get(req.experience, 1.0)

        out: list[ScoredCandidate] = []
        for fp in FRAMEWORKS:
            score = 0.0
            rationale: list[str] = []

            if fp.language == top_language:
                score += 25
                rationale.append(f"Pairs naturally with the recommended language ({top_language}).")
            else:
                score += 4

            if req.project_type in fp.great_for_project_types:
                score += 22
                rationale.append(f"Designed for {req.project_type} projects.")
            else:
                score += 4

            if req.platform in fp.great_for_platforms:
                score += 12
                rationale.append(f"Runs on your target platform ({req.platform}).")
            else:
                score += 3

            score += fp.development_speed * timeline * 1.2
            score += fp.scalability_ceiling * scalability * 1.0
            score += fp.security_maturity * security * 1.2
            score += fp.learning_curve_friendliness * experience * 0.9
            score += fp.ecosystem_breadth * 0.6

            if fp.development_speed >= 9 and timeline >= 1.0:
                rationale.append("Optimized for fast time-to-market.")
            if fp.security_maturity >= 9 and security >= 1.0:
                rationale.append("Battle-tested security defaults.")

            out.append(ScoredCandidate(name=fp.name, score=round(score, 2), rationale=rationale))

        out.sort(key=lambda c: c.score, reverse=True)
        return out

    # ---------- scoring (SDLC) ----------

    def _score_sdlc(self, req: RecommendationRequest) -> list[ScoredCandidate]:
        team = req.team_size
        timeline = _TIMELINE_WEIGHTS.get(req.timeline, 1.0)
        complexity = _COMPLEXITY_WEIGHTS.get(req.complexity, 1.0)
        security = _SECURITY_WEIGHTS.get(req.security, 1.0)

        small = team in {"Solo (1)", "Small (2–4)"}
        large = team in {"Large (11–25)", "Enterprise (25+)"}

        out: list[ScoredCandidate] = []
        for sp in SDLC_MODELS:
            score = 0.0
            rationale: list[str] = []

            if small:
                score += sp.suits_small_team * 1.4
                if sp.suits_small_team >= 9:
                    rationale.append("Lightweight enough for a small team to adopt fast.")
            elif large:
                score += sp.suits_large_team * 1.4
                if sp.suits_large_team >= 9:
                    rationale.append("Designed to coordinate large, distributed teams.")
            else:
                score += (sp.suits_small_team + sp.suits_large_team) * 0.6

            if req.project_goal in sp.great_for_goals:
                score += 18
                rationale.append(f"Aligned with your goal: {req.project_goal}.")
            else:
                score += 4

            if timeline >= 1.1:
                score += sp.suits_fast_timeline * 1.1
                if sp.suits_fast_timeline >= 9:
                    rationale.append("Optimized for tight timelines.")
            score += sp.suits_changing_reqs * (1.2 if req.project_goal in {"MVP / Prototype", "Startup Launch"} else 0.7)
            score += sp.suits_fixed_scope * (1.2 if req.project_goal == "Client Project" else 0.4)
            score += sp.risk_management * security * 0.8
            score -= sp.overhead * complexity * 0.4

            if sp.risk_management >= 9 and security >= 1.0:
                rationale.append("Strong risk-management practices for high-security work.")

            out.append(ScoredCandidate(name=sp.name, score=round(score, 2), rationale=rationale))

        out.sort(key=lambda c: c.score, reverse=True)
        return out


# ---------- profile lookup helpers (used by explanation service) ----------

def find_language_profile(name: str) -> Optional[LanguageProfile]:
    return next((lp for lp in LANGUAGES if lp.name == name), None)


def find_framework_profile(name: str) -> Optional[FrameworkProfile]:
    return next((fp for fp in FRAMEWORKS if fp.name == name), None)


def find_sdlc_profile(name: str) -> Optional[SDLCProfile]:
    return next((sp for sp in SDLC_MODELS if sp.name == name), None)
