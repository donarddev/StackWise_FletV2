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

_COMPLEXITY_WEIGHTS = {"Low": 0.5, "Medium": 0.8, "High": 1.05, "Very High": 1.25}
_TIMELINE_WEIGHTS = {
    "Less than 1 month": 1.35,
    "1–2 months": 1.15,
    "3–4 months": 0.95,
    "5–6 months": 0.8,
    "More than 6 months": 0.7,
}
_SCALABILITY_WEIGHTS = {
    "Small user base": 0.5,
    "Medium user base": 0.8,
    "Large user base": 1.05,
    "Expected to grow fast": 1.25,
    "Not sure": 0.75,
}
_SECURITY_WEIGHTS = {
    "Basic": 0.55,
    "Moderate": 0.8,
    "High": 1.05,
    "Sensitive user data": 1.2,
    "Payment or financial data": 1.35,
}
_EXPERIENCE_WEIGHTS = {
    "Beginner": 1.35,
    "Intermediate": 1.0,
    "Advanced": 0.78,
    "Team has mixed experience": 1.05,
}
_PERFORMANCE_WEIGHTS = {
    "Basic": 0.6,
    "Moderate": 0.85,
    "High": 1.1,
    "Real-time / Low latency": 1.3,
    "Not sure": 0.8,
}
_STABILITY_WEIGHTS = {
    "Very Stable": 0.65,
    "Mostly Stable": 0.8,
    "Somewhat Changing": 1.0,
    "Frequently Changing": 1.2,
    "Unknown / Experimental": 1.25,
}
_STAKEHOLDER_WEIGHTS = {"Low": 0.7, "Medium": 0.9, "High": 1.1, "Frequent Review Needed": 1.25}


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

    @staticmethod
    def _team_weight(team_size: str) -> float:
        try:
            team_n = max(1, int(team_size))
        except (TypeError, ValueError):
            team_n = 1
        if team_n <= 2:
            return 0.5
        if team_n <= 5:
            return 0.7
        if team_n <= 10:
            return 0.9
        if team_n <= 25:
            return 1.1
        return 1.25

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
        explanation["risk_analysis"] = self._build_risk_analysis(request)
        explanation["skill_gap_analysis"] = self._build_skill_gap_analysis(request, languages[0].name, frameworks[0].name)
        explanation["roadmap"] = self._build_roadmap(request)
        explanation["presentation_summary"] = (
            f"{request.project_name}: {languages[0].name} + {frameworks[0].name} with {sdlc[0].name}. "
            f"Designed for {request.timeline.lower()} delivery with confidence {confidence}/100."
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
        profile = prev.project_profile or {}
        request = RecommendationRequest(
            project_name=prev.project_name,
            project_type=prev.project_type,
            selected_features="|".join(profile.get("selected_features", [])),
            project_goal=profile.get("project_goal", prev.project_goal),
            team_size=prev.team_size,
            complexity=prev.complexity,
            timeline=prev.timeline,
            requirements_stability=profile.get("requirements_stability", "Mostly Stable"),
            stakeholder_involvement=profile.get("stakeholder_involvement", "Medium"),
            preferred_platform=prev.platform,
            development_experience=prev.experience,
            scalability_needs=prev.scalability,
            performance_requirements=profile.get("performance_requirements", "Moderate"),
            security_requirements=prev.security,
            budget_constraints=profile.get("budget_constraints", "Limited"),
            maintenance_expectations=profile.get("maintenance_expectations", "Long-term maintainable project"),
            deployment_preference=profile.get("deployment_preference", "Not sure"),
        )
        outcome = self.generate(request)
        new_rec = self.save(user_id, request, outcome)
        self.repo.add_history(user_id, new_rec.id, "regenerated")
        return new_rec

    def _build_risk_analysis(self, request: RecommendationRequest) -> list[str]:
        risks: list[str] = []
        if request.timeline in {"Less than 1 month", "1–2 months"}:
            risks.append("Short delivery window may limit testing depth and integration hardening.")
        if request.requirements_stability in {"Frequently Changing", "Unknown / Experimental"}:
            risks.append("Changing requirements can trigger scope creep without strict backlog control.")
        if request.security_requirements in {"Sensitive user data", "Payment or financial data"}:
            risks.append("Security/compliance controls must be planned from sprint zero.")
        if request.team_size.isdigit() and int(request.team_size) <= 2:
            risks.append("Small team capacity can become a bottleneck for parallel feature delivery.")
        return risks or ["No major delivery risks detected; maintain disciplined testing and documentation."]

    def _build_skill_gap_analysis(
        self,
        request: RecommendationRequest,
        language: str,
        framework: str,
    ) -> list[str]:
        gaps: list[str] = []
        if request.development_experience in {"Beginner", "Team has mixed experience"}:
            gaps.append(f"Team may need onboarding on {language} fundamentals and tooling.")
            gaps.append(f"Prioritize guided templates for {framework} project structure and deployment.")
        if "Real-time Updates" in request.selected_features_list():
            gaps.append("Real-time architecture patterns (queues/websockets) should be practiced early.")
        return gaps or ["Current experience appears sufficient; focus on architecture consistency and QA."]

    def _build_roadmap(self, request: RecommendationRequest) -> list[str]:
        return [
            "Week 1: finalize scope, architecture boundaries, and data model.",
            "Week 2: implement core feature workflow and authentication.",
            "Week 3: add non-functional requirements (security, performance, scalability).",
            "Week 4+: polish UX, testing, documentation, and deployment readiness.",
        ]

    # ---------- scoring (languages) ----------

    def _score_languages(self, req: RecommendationRequest) -> list[ScoredCandidate]:
        complexity = _COMPLEXITY_WEIGHTS.get(req.complexity, 1.0)
        team = self._team_weight(req.team_size)
        timeline = _TIMELINE_WEIGHTS.get(req.timeline, 1.0)
        scalability = _SCALABILITY_WEIGHTS.get(req.scalability_needs, 1.0)
        security = _SECURITY_WEIGHTS.get(req.security_requirements, 1.0)
        experience = _EXPERIENCE_WEIGHTS.get(req.development_experience, 1.0)
        performance = _PERFORMANCE_WEIGHTS.get(req.performance_requirements, 1.0)

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
            if req.preferred_platform in lp.great_for_platforms:
                score += 12
                rationale.append(f"Targets your {req.preferred_platform} platform natively.")
            else:
                score += 3

            # weighted dimension scores
            score += lp.runtime_performance * performance * 1.0
            score += lp.scalability_ceiling * scalability * 1.0
            score += lp.security_maturity * security * 1.2
            score += lp.development_speed * timeline * 1.1
            score += lp.learning_curve_friendliness * experience * 1.0
            score += lp.type_safety * complexity * 0.8
            score += lp.ecosystem_breadth * 0.5
            score += min(team, 1.2) * lp.scalability_ceiling * 0.4
            if "AI / ML Features" in req.selected_features_list():
                score += lp.ecosystem_breadth * 0.9
            if "Real-time Updates" in req.selected_features_list():
                score += lp.runtime_performance * 0.7

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
        scalability = _SCALABILITY_WEIGHTS.get(req.scalability_needs, 1.0)
        security = _SECURITY_WEIGHTS.get(req.security_requirements, 1.0)
        experience = _EXPERIENCE_WEIGHTS.get(req.development_experience, 1.0)
        performance = _PERFORMANCE_WEIGHTS.get(req.performance_requirements, 1.0)

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

            if req.preferred_platform in fp.great_for_platforms:
                score += 12
                rationale.append(f"Runs on your target platform ({req.preferred_platform}).")
            else:
                score += 3

            score += fp.development_speed * timeline * 1.2
            score += fp.scalability_ceiling * scalability * 1.0
            score += fp.scalability_ceiling * performance * 0.55
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
        team_weight = self._team_weight(req.team_size)
        timeline = _TIMELINE_WEIGHTS.get(req.timeline, 1.0)
        complexity = _COMPLEXITY_WEIGHTS.get(req.complexity, 1.0)
        security = _SECURITY_WEIGHTS.get(req.security_requirements, 1.0)
        stability = _STABILITY_WEIGHTS.get(req.requirements_stability, 1.0)
        stakeholder = _STAKEHOLDER_WEIGHTS.get(req.stakeholder_involvement, 1.0)
        small = team_weight <= 0.7
        large = team_weight >= 1.1

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

            goal_text = req.project_goal.lower()
            goal_hit = any(goal.lower().split()[0] in goal_text for goal in sp.great_for_goals)
            if goal_hit:
                score += 18
                rationale.append("Aligned with your project goal keywords.")
            else:
                score += 4

            if timeline >= 1.1:
                score += sp.suits_fast_timeline * 1.1
                if sp.suits_fast_timeline >= 9:
                    rationale.append("Optimized for tight timelines.")
            score += sp.suits_changing_reqs * stability
            score += sp.suits_fixed_scope * (1.1 if stability <= 0.8 else 0.5)
            score += stakeholder * 4.2
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
