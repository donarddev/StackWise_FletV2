"""Recommendation scoring schemas — request/result data structures.

Phase 1 weighted scoring engine contract. Independent of Flet, database, and the
legacy form request class in ``app.requests.recommendation_request``.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

_EMPTY_PREFERRED = frozenset(
    {
        "",
        "none",
        "none / not sure",
        "not sure",
        "null",
    }
)


def _clean_preferred(value: Any) -> str:
    text = str(value or "").strip()
    if text.lower() in _EMPTY_PREFERRED:
        return ""
    return text


@dataclass
class RecommendationRequest:
    """User project profile used by the weighted scoring engine."""

    project_name: str = ""
    project_type: str = ""
    selected_features: list[str] = field(default_factory=list)
    project_goal: str = ""
    team_size: int = 1
    complexity: str = "Medium"
    timeline: str = "Medium"
    requirements_stability: str = "Mostly Stable"
    stakeholder_involvement: str = "Medium"
    preferred_platform: str = "Web"
    development_experience: str = "Intermediate"
    scalability_needs: str = "Medium"
    performance_requirements: str = "Medium"
    security_requirements: str = "Medium"
    budget_constraints: str = "Medium"
    maintenance_expectations: str = "Medium"
    deployment_preference: str = "Cloud"
    user_preferred_language: str = ""
    user_preferred_framework: str = ""
    user_preferred_sdlc: str = ""
    user_preferred_reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RecommendationRequest:
        features = data.get("selected_features", [])
        if isinstance(features, str):
            features = [
                f.strip() for f in features.replace("|", ",").split(",") if f.strip()
            ]
        elif isinstance(features, (tuple, set)):
            features = [str(f).strip() for f in features if str(f).strip()]
        elif not isinstance(features, list):
            features = []

        team_raw = data.get("team_size", 1)
        try:
            team_size = max(1, int(team_raw))
        except (TypeError, ValueError):
            team_size = 1

        lang = _clean_preferred(
            data.get("user_preferred_language")
            or data.get("preferred_language_optional")
        )
        fw = _clean_preferred(
            data.get("user_preferred_framework")
            or data.get("preferred_framework_optional")
        )
        sdlc = _clean_preferred(
            data.get("user_preferred_sdlc") or data.get("preferred_sdlc_optional")
        )
        reason = str(
            data.get("user_preferred_reason")
            or data.get("preferred_stack_reason_optional")
            or ""
        ).strip()

        return cls(
            project_name=str(data.get("project_name", "") or "").strip(),
            project_type=str(data.get("project_type", "") or "").strip(),
            selected_features=[str(f).strip() for f in features if str(f).strip()],
            project_goal=str(data.get("project_goal", "") or "").strip(),
            team_size=team_size,
            complexity=str(data.get("complexity", "Medium") or "Medium").strip(),
            timeline=str(data.get("timeline", "Medium") or "Medium").strip(),
            requirements_stability=str(
                data.get("requirements_stability", "Mostly Stable") or "Mostly Stable"
            ).strip(),
            stakeholder_involvement=str(
                data.get("stakeholder_involvement", "Medium") or "Medium"
            ).strip(),
            preferred_platform=str(data.get("preferred_platform", "Web") or "Web").strip(),
            development_experience=str(
                data.get("development_experience", "Intermediate") or "Intermediate"
            ).strip(),
            scalability_needs=str(data.get("scalability_needs", "Medium") or "Medium").strip(),
            performance_requirements=str(
                data.get("performance_requirements", "Medium") or "Medium"
            ).strip(),
            security_requirements=str(
                data.get("security_requirements", "Medium") or "Medium"
            ).strip(),
            budget_constraints=str(data.get("budget_constraints", "Medium") or "Medium").strip(),
            maintenance_expectations=str(
                data.get("maintenance_expectations", "Medium") or "Medium"
            ).strip(),
            deployment_preference=str(
                data.get("deployment_preference", "Cloud") or "Cloud"
            ).strip(),
            user_preferred_language=lang,
            user_preferred_framework=fw,
            user_preferred_sdlc=sdlc,
            user_preferred_reason=reason,
        )


@dataclass
class RecommendationResult:
    """Structured output from the weighted recommendation engine (legacy dataclass)."""

    recommended_language: str = ""
    recommended_framework: str = ""
    recommended_sdlc: str = ""
    confidence_score: float = 0.0
    confidence_label: str = ""
    language_scores: dict[str, float] = field(default_factory=dict)
    framework_scores: dict[str, float] = field(default_factory=dict)
    sdlc_scores: dict[str, float] = field(default_factory=dict)
    alternative_languages: list[dict[str, Any]] = field(default_factory=list)
    alternative_frameworks: list[dict[str, Any]] = field(default_factory=list)
    alternative_sdlc_models: list[dict[str, Any]] = field(default_factory=list)
    explanation: str = ""
    risks: list[str] = field(default_factory=list)
    skill_gaps: list[str] = field(default_factory=list)
    roadmap: list[dict[str, str]] = field(default_factory=list)
    scoring_basis: str = ""
    defense_explanation: str = ""
    validation_note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RecommendationResult:
        return cls(
            recommended_language=str(data.get("recommended_language", "")),
            recommended_framework=str(data.get("recommended_framework", "")),
            recommended_sdlc=str(data.get("recommended_sdlc", "")),
            confidence_score=float(data.get("confidence_score", 0)),
            confidence_label=str(data.get("confidence_label", "")),
            language_scores=dict(data.get("language_scores", {})),
            framework_scores=dict(data.get("framework_scores", {})),
            sdlc_scores=dict(data.get("sdlc_scores", {})),
            alternative_languages=list(data.get("alternative_languages", [])),
            alternative_frameworks=list(data.get("alternative_frameworks", [])),
            alternative_sdlc_models=list(data.get("alternative_sdlc_models", [])),
            explanation=str(data.get("explanation", "")),
            risks=list(data.get("risks", [])),
            skill_gaps=list(data.get("skill_gaps", [])),
            roadmap=list(data.get("roadmap", [])),
            scoring_basis=str(data.get("scoring_basis", "")),
            defense_explanation=str(data.get("defense_explanation", "")),
            validation_note=str(data.get("validation_note", "")),
        )
