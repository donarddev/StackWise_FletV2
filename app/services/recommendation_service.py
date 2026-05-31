"""Rule-based weighted recommendation engine (Phase 1 — Laravel-style extended).

No Flet, database, or ML dependencies. Testable in isolation.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.schemas.recommendation_schema import RecommendationRequest
from app.utils.logger import get_logger

log = get_logger(__name__)

# Set STACKWISE_DEBUG_SCORING=1 to log scoring breakdown (logger only).
DEBUG_RECOMMENDATION = False

# ---------------------------------------------------------------------------
# Candidate lists (exactly 15 each)
# ---------------------------------------------------------------------------

LANGUAGES: tuple[str, ...] = (
    "Python",
    "PHP",
    "JavaScript",
    "TypeScript",
    "Java",
    "C#",
    "C++",
    "C",
    "Dart",
    "Kotlin",
    "Swift",
    "Ruby",
    "Go",
    "Rust",
    "SQL",
)

FRAMEWORKS: tuple[str, ...] = (
    "Laravel",
    "FastAPI",
    "Django",
    "Flask",
    "React",
    "Vue",
    "Angular",
    "Next.js",
    "NestJS",
    "Express.js",
    "Flutter",
    "Spring Boot",
    "ASP.NET Core",
    "Ruby on Rails",
    "Tauri",
    "Flet",
)

SDLC_MODELS: tuple[str, ...] = (
    "Agile",
    "Waterfall",
    "Iterative",
    "Incremental",
    "Spiral",
    "V-Model",
    "RAD",
    "Prototype Model",
    "Scrum",
    "Kanban",
    "DevOps",
    "Lean",
    "Big Bang Model",
    "Feature-Driven Development (FDD)",
    "Extreme Programming (XP)",
)

FRAMEWORK_LANGUAGES: dict[str, tuple[str, ...]] = {
    "Laravel": ("PHP",),
    "FastAPI": ("Python",),
    "Django": ("Python",),
    "Flask": ("Python",),
    "React": ("JavaScript", "TypeScript"),
    "Vue": ("JavaScript", "TypeScript"),
    "Angular": ("TypeScript",),
    "Next.js": ("JavaScript", "TypeScript"),
    "NestJS": ("TypeScript", "JavaScript"),
    "Express.js": ("JavaScript", "TypeScript"),
    "Flutter": ("Dart",),
    "Spring Boot": ("Java",),
    "ASP.NET Core": ("C#",),
    "Ruby on Rails": ("Ruby",),
    "Tauri": ("Rust", "TypeScript", "JavaScript"),
    "Flet": ("Python",),
}

LANGUAGE_FRAMEWORKS: dict[str, tuple[str, ...]] = {
    lang: tuple(fw for fw, langs in FRAMEWORK_LANGUAGES.items() if lang in langs)
    for lang in LANGUAGES
    if lang != "SQL"
}

BASE_STACK_CANDIDATES: tuple[tuple[str, str, str], ...] = (
    ("PHP", "Laravel", "Agile"),
    ("PHP", "Laravel", "RAD"),
    ("PHP", "Laravel", "Waterfall"),
    ("Python", "FastAPI", "Iterative"),
    ("Python", "FastAPI", "Agile"),
    ("Python", "Django", "Agile"),
    ("Python", "Django", "Waterfall"),
    ("Python", "Flask", "Prototype Model"),
    ("JavaScript", "React", "Agile"),
    ("TypeScript", "React", "Agile"),
    ("JavaScript", "Vue", "Agile"),
    ("TypeScript", "Angular", "Scrum"),
    ("TypeScript", "Next.js", "Agile"),
    ("JavaScript", "Express.js", "Iterative"),
    ("TypeScript", "NestJS", "Scrum"),
    ("Java", "Spring Boot", "Waterfall"),
    ("Java", "Spring Boot", "Spiral"),
    ("Java", "Spring Boot", "Scrum"),
    ("C#", "ASP.NET Core", "Waterfall"),
    ("C#", "ASP.NET Core", "Spiral"),
    ("Dart", "Flutter", "Agile"),
    ("Dart", "Flutter", "Prototype Model"),
    ("Ruby", "Ruby on Rails", "Agile"),
    ("Rust", "Tauri", "Iterative"),
    ("Rust", "Tauri", "Spiral"),
    ("TypeScript", "Tauri", "Iterative"),
    ("Python", "Flet", "Agile"),
    ("Python", "Flet", "Prototype Model"),
    ("Python", "Flet", "RAD"),
)

WEB_CRUD_STACK_CANDIDATES: tuple[tuple[str, str, str], ...] = (
    ("PHP", "Laravel", "Agile"),
    ("PHP", "Laravel", "RAD"),
    ("PHP", "Laravel", "Waterfall"),
    ("Python", "Django", "Agile"),
    ("Python", "Django", "Waterfall"),
    ("Ruby", "Ruby on Rails", "Agile"),
    ("C#", "ASP.NET Core", "Waterfall"),
    ("C#", "ASP.NET Core", "Spiral"),
    ("Java", "Spring Boot", "Waterfall"),
    ("Java", "Spring Boot", "Spiral"),
    ("TypeScript", "Next.js", "Agile"),
    ("TypeScript", "Angular", "Scrum"),
)

MOBILE_STACK_CANDIDATES: tuple[tuple[str, str, str], ...] = (
    ("Dart", "Flutter", "Agile"),
    ("Dart", "Flutter", "Prototype Model"),
    ("Dart", "Flutter", "RAD"),
)

BACKEND_API_STACK_CANDIDATES: tuple[tuple[str, str, str], ...] = (
    ("Python", "FastAPI", "Iterative"),
    ("Python", "FastAPI", "Agile"),
    ("JavaScript", "Express.js", "Iterative"),
    ("TypeScript", "NestJS", "Scrum"),
    ("Java", "Spring Boot", "Spiral"),
    ("Java", "Spring Boot", "Scrum"),
    ("C#", "ASP.NET Core", "Spiral"),
    ("PHP", "Laravel", "Agile"),
)

DESKTOP_STACK_CANDIDATES: tuple[tuple[str, str, str], ...] = (
    ("Rust", "Tauri", "Iterative"),
    ("Rust", "Tauri", "Spiral"),
    ("TypeScript", "Tauri", "Iterative"),
    ("Dart", "Flutter", "Agile"),
    ("Python", "Flet", "Agile"),
    ("Python", "Flet", "Prototype Model"),
    ("C#", "ASP.NET Core", "Waterfall"),
)

EMBEDDED_STACK_CANDIDATES: tuple[tuple[str, str, str], ...] = (
    ("C", "No framework required", "V-Model"),
    ("C++", "No framework required", "Spiral"),
    ("Rust", "No framework required", "Spiral"),
)

AI_ML_STACK_CANDIDATES: tuple[tuple[str, str, str], ...] = (
    ("Python", "FastAPI", "Iterative"),
    ("Python", "FastAPI", "Agile"),
    ("Python", "Django", "Agile"),
    ("Python", "Flask", "Prototype Model"),
    ("Python", "Flet", "Iterative"),
    ("Python", "Flet", "Agile"),
)

WEB_ONLY_FRAMEWORKS: frozenset[str] = frozenset(
    {"Laravel", "Django", "Ruby on Rails", "Angular", "React", "Vue", "Next.js"}
)
FRONTEND_ONLY_FRAMEWORKS: frozenset[str] = frozenset({"React", "Vue", "Angular"})
MOBILE_PRIMARY_FRAMEWORKS: frozenset[str] = frozenset({"Flutter"})
DESKTOP_PRIMARY_FRAMEWORKS: frozenset[str] = frozenset({"Tauri", "Flutter", "Flet"})
PYTHON_UI_FRAMEWORKS: frozenset[str] = frozenset({"Flet"})

FRAMEWORKLESS_LANGUAGES: frozenset[str] = frozenset(
    {"Kotlin", "Swift", "C", "C++", "Go", "SQL"}
)
NO_FRAMEWORK_LABEL = "No framework required"
SQL_FRAMEWORK_LABEL = "Database-focused stack"

DATABASE_CENTERED_TYPES: frozenset[str] = frozenset(
    {
        "database system",
        "data warehouse",
        "reporting system",
        "analytics system",
        "records management system",
        "data management system",
    }
)

SCORING_BASIS = (
    "The recommendation uses a rule-based weighted scoring model. Project inputs are "
    "mapped to technology and SDLC suitability criteria such as project type, platform, "
    "features, security, performance, scalability, budget, timeline, team size, complexity, "
    "experience level, maintainability, deployment, requirement stability, and stakeholder "
    "involvement."
)

DEFENSE_EXPLANATION = (
    "The system is a decision-support tool, not a machine-learning model. It assigns weighted "
    "points to candidate programming languages, frameworks, and SDLC models based on project "
    "requirements. Compatibility rules prevent invalid language-framework pairings. The "
    "highest-scoring compatible stack is selected, while alternatives, why-not-this "
    "explanations, risks, skill gaps, roadmap items, and user preference comparison make the "
    "result explainable."
)

VALIDATION_NOTE = (
    "The scoring rules are researcher-defined and source-informed. They are designed to be "
    "explainable and consistent, but they do not guarantee an absolute best technology. The "
    "recommendation should be interpreted as a structured decision-support result."
)


@dataclass
class NormalizedRequest:
    project_name: str
    project_type: str
    project_type_norm: str
    selected_features: list[str]
    features_text: str
    project_goal: str
    goal_text: str
    combined_text: str
    team_size: int
    complexity: str
    timeline: str
    requirements_stability: str
    stakeholder_involvement: str
    preferred_platform: str
    platform_text: str
    development_experience: str
    scalability_needs: str
    performance_requirements: str
    security_requirements: str
    budget_constraints: str
    maintenance_expectations: str
    deployment_preference: str
    user_preferred_language: str
    user_preferred_framework: str
    user_preferred_sdlc: str
    user_preferred_reason: str
    is_web: bool
    is_mobile: bool
    is_desktop: bool
    is_api_backend: bool
    is_ai: bool
    is_reporting_analytics: bool
    is_crud_admin: bool
    is_web_admin_portal: bool
    is_auth: bool
    is_realtime: bool
    is_database_heavy: bool
    is_embedded: bool
    is_cross_platform_desktop: bool
    is_database_centered: bool
    project_context: dict[str, Any] = field(default_factory=dict)


def classify_project_context(data: dict[str, Any]) -> dict[str, Any]:
    """Classify project context from raw or partial request data (Phase 2.3)."""
    svc = RecommendationService()
    if "project_context" in data and "primary_context" in data.get("project_context", {}):
        return data["project_context"]
    if "combined_text" in data and "primary_context" in data:
        return data
    req = RecommendationRequest.from_dict(data)
    features = [svc._normalize_feature_token(f) for f in req.selected_features]
    features_text = " ".join(features)
    goal_text = svc._norm_token(req.project_goal)
    project_type_norm = svc._norm_token(req.project_type)
    platform_text = svc._norm_platform(req.preferred_platform)
    combined = " ".join(
        filter(
            None,
            [project_type_norm, platform_text, goal_text, features_text],
        )
    )
    return svc._build_project_context(
        {
            "project_type_norm": project_type_norm,
            "platform_text": platform_text,
            "goal_text": goal_text,
            "features": features,
            "features_text": features_text,
            "combined_text": combined,
            "timeline": svc._norm_timeline(req.timeline),
            "requirements_stability": svc._norm_stability(req.requirements_stability),
            "security_requirements": svc._norm_level(
                req.security_requirements,
                high_tokens=("high", "sensitive", "payment", "financial"),
            ),
            "performance_requirements": svc._norm_level(
                req.performance_requirements,
                high_tokens=("high", "real-time", "realtime", "low latency"),
            ),
            "budget_constraints": svc._norm_budget(req.budget_constraints),
        }
    )


class _ScoringContext:
    def __init__(self) -> None:
        self.language_scores: dict[str, int] = {name: 0 for name in LANGUAGES}
        self.framework_scores: dict[str, int] = {name: 0 for name in FRAMEWORKS}
        self.sdlc_scores: dict[str, int] = {name: 0 for name in SDLC_MODELS}
        self.language_reasons: dict[str, list[str]] = {name: [] for name in LANGUAGES}
        self.framework_reasons: dict[str, list[str]] = {name: [] for name in FRAMEWORKS}
        self.sdlc_reasons: dict[str, list[str]] = {name: [] for name in SDLC_MODELS}

    def add_language_score(self, name: str, points: int, reason: str) -> None:
        if name in self.language_scores:
            self.language_scores[name] += points
            self.language_reasons[name].append(reason)

    def add_framework_score(self, name: str, points: int, reason: str) -> None:
        if name in self.framework_scores:
            self.framework_scores[name] += points
            self.framework_reasons[name].append(reason)

    def add_sdlc_score(self, name: str, points: int, reason: str) -> None:
        if name in self.sdlc_scores:
            self.sdlc_scores[name] += points
            self.sdlc_reasons[name].append(reason)


class RecommendationService:
    """Laravel-style weighted scoring engine extended to full Flet candidate lists."""

    def recommend(self, data: dict[str, Any] | RecommendationRequest) -> dict[str, Any]:
        if isinstance(data, RecommendationRequest):
            payload = data.to_dict()
        else:
            payload = dict(data)
        return self.generate_full_recommendation(payload)

    def generate_full_recommendation(self, data: dict[str, Any]) -> dict[str, Any]:
        norm = self.normalize_request(data)
        ctx = self.calculate_scores(norm)
        language_scores = dict(ctx.language_scores)
        framework_scores = dict(ctx.framework_scores)
        sdlc_scores = dict(ctx.sdlc_scores)

        if self._scoring_debug_enabled():
            self._log_scoring_debug(norm, ctx)

        best = self.select_best_recommendation(ctx, norm)
        alternatives = self._rank_stack_candidates(ctx, norm)

        confidence = self.calculate_confidence(
            best,
            alternatives,
            norm,
        )
        label = self._confidence_label(confidence)

        reasons = {
            "language": self._top_reason(ctx.language_reasons.get(best["language"], [])),
            "framework": self._top_reason(ctx.framework_reasons.get(best["framework"], [])),
            "sdlc": self._top_reason(ctx.sdlc_reasons.get(best["sdlc"], [])),
        }

        language_reason = reasons["language"] or (
            f"{best['language']} matched project type, platform, and feature profile."
        )
        framework_reason = reasons["framework"] or (
            f"{best['framework']} aligns with {best['language']} and project delivery needs."
        )
        sdlc_reason = reasons["sdlc"] or (
            f"{best['sdlc']} fits timeline, team size, and requirements stability."
        )

        explanation = self.generate_reasons(norm, best, reasons, confidence, label)
        alt_stacks = self.generate_alternative_stacks(
            ctx, norm, best, alternatives
        )
        user_pref = self.analyze_user_preferred_stack(
            norm, best, language_scores, framework_scores, sdlc_scores, ctx
        )
        alt_stacks = self._maybe_add_user_preferred_alternative(
            alt_stacks, user_pref, norm, ctx
        )
        self._normalize_alternative_fit_percents(
            alt_stacks, int(best.get("stack_score", 0))
        )
        why_not = self.generate_why_not_this(
            norm, best, alternatives, user_pref, ctx
        )
        risks = self.generate_risk_analysis(norm)
        skill_gaps = self.generate_skill_gap_analysis(norm, best)
        roadmap = self.generate_project_roadmap(norm, best["sdlc"], best["framework"])

        sql_note = self._sql_support_note(norm, best["language"])
        if sql_note:
            explanation = f"{explanation}\n\n{sql_note}"

        generated_at = datetime.now(timezone.utc).isoformat()
        saved = {
            "project_name": norm.project_name,
            "project_type": norm.project_type,
            "language": best["language"],
            "framework": best["framework"],
            "sdlc": best["sdlc"],
            "confidence": confidence,
            "confidence_label": label,
            "explanation": explanation,
            "generated_at": generated_at,
        }

        legacy_alt_lang = self._legacy_component_alternatives(
            language_scores, best["language"], ctx.language_reasons
        )
        legacy_alt_fw = self._legacy_component_alternatives(
            framework_scores, best["framework"], ctx.framework_reasons
        )
        legacy_alt_sdlc = self._legacy_component_alternatives(
            sdlc_scores, best["sdlc"], ctx.sdlc_reasons
        )

        result: dict[str, Any] = {
            "saved_recommendation": saved,
            "recommended_language": best["language"],
            "recommended_framework": best["framework"],
            "recommended_sdlc": best["sdlc"],
            "confidence_score": confidence,
            "confidence_label": label,
            "language_reason": language_reason,
            "framework_reason": framework_reason,
            "sdlc_reason": sdlc_reason,
            "explanation": explanation,
            "language_scores": language_scores,
            "framework_scores": framework_scores,
            "sdlc_scores": sdlc_scores,
            "alternative_technology_stacks": alt_stacks,
            "why_not_this": why_not,
            "risk_analysis": risks,
            "skill_gap_analysis": skill_gaps,
            "suggested_project_roadmap": roadmap,
            "user_preferred_stack": user_pref,
            "scoring_basis": SCORING_BASIS,
            "defense_explanation": DEFENSE_EXPLANATION,
            "validation_note": VALIDATION_NOTE,
            "alternatives": alt_stacks,
            "risks": [self._risk_to_string(r) for r in risks],
            "skill_gaps": [self._skill_gap_to_string(g) for g in skill_gaps],
            "roadmap": roadmap,
            "alternative_languages": legacy_alt_lang,
            "alternative_frameworks": legacy_alt_fw,
            "alternative_sdlc_models": legacy_alt_sdlc,
        }
        return result

    # ------------------------------------------------------------------
    # Normalization
    # ------------------------------------------------------------------

    def normalize_request(self, data: dict[str, Any]) -> NormalizedRequest:
        req = RecommendationRequest.from_dict(data)
        features = [self._normalize_feature_token(f) for f in req.selected_features]
        features_text = " ".join(features)
        goal_text = self._norm_token(req.project_goal)
        project_type_norm = self._norm_token(req.project_type)
        platform_text = self._norm_platform(req.preferred_platform)
        combined = " ".join(
            filter(
                None,
                [
                    project_type_norm,
                    platform_text,
                    goal_text,
                    features_text,
                ],
            )
        )

        timeline = self._norm_timeline(req.timeline)
        complexity = self._norm_complexity(req.complexity)
        stability = self._norm_stability(req.requirements_stability)
        stakeholder = self._norm_stakeholder(req.stakeholder_involvement)
        experience = self._norm_experience(req.development_experience)
        scalability = self._norm_level(
            req.scalability_needs,
            high_tokens=("large", "grow", "expected to grow fast"),
        )
        performance = self._norm_level(
            req.performance_requirements,
            high_tokens=("high", "real-time", "realtime", "low latency"),
        )
        security = self._norm_level(
            req.security_requirements,
            high_tokens=("high", "sensitive", "payment", "financial"),
        )
        budget = self._norm_budget(req.budget_constraints)
        maintenance = self._norm_maintenance(req.maintenance_expectations)
        deployment = self._norm_deployment(req.deployment_preference)

        project_context = self._build_project_context(
            {
                "project_type_norm": project_type_norm,
                "platform_text": platform_text,
                "goal_text": goal_text,
                "features": features,
                "features_text": features_text,
                "combined_text": combined,
                "timeline": timeline,
                "requirements_stability": stability,
                "security_requirements": security,
                "performance_requirements": performance,
                "budget_constraints": budget,
            }
        )

        is_web = project_context["is_web"]
        is_mobile = project_context["is_mobile"]
        is_desktop = project_context["is_desktop"]
        is_api_backend = project_context["is_backend_api"]
        is_ai = project_context["is_ai_ml"]
        is_reporting_analytics = project_context["is_reporting_basic"]
        is_crud_admin = project_context["is_crud_admin_system"]
        is_auth = self._contains_any(
            combined,
            ("authentication", "login", "register", "role-based access"),
        )
        is_realtime = project_context["is_realtime"]
        is_database_heavy = self._contains_any(
            combined,
            (
                "database",
                "records",
                "query",
                "sql",
                "reporting system",
                "data warehouse",
            ),
        )
        is_embedded = project_context["is_embedded_systems"]
        is_cross_platform_desktop = project_context["is_cross_platform_desktop"]
        is_database_centered = project_context["is_database_centered"]

        return NormalizedRequest(
            project_name=req.project_name,
            project_type=req.project_type,
            project_type_norm=project_type_norm,
            selected_features=req.selected_features,
            features_text=features_text,
            project_goal=req.project_goal,
            goal_text=goal_text,
            combined_text=combined,
            team_size=req.team_size,
            complexity=complexity,
            timeline=timeline,
            requirements_stability=stability,
            stakeholder_involvement=stakeholder,
            preferred_platform=req.preferred_platform,
            platform_text=platform_text,
            development_experience=experience,
            scalability_needs=scalability,
            performance_requirements=performance,
            security_requirements=security,
            budget_constraints=budget,
            maintenance_expectations=maintenance,
            deployment_preference=deployment,
            user_preferred_language=req.user_preferred_language,
            user_preferred_framework=req.user_preferred_framework,
            user_preferred_sdlc=req.user_preferred_sdlc,
            user_preferred_reason=req.user_preferred_reason,
            is_web=is_web,
            is_mobile=is_mobile,
            is_desktop=is_desktop,
            is_api_backend=is_api_backend,
            is_ai=is_ai,
            is_reporting_analytics=is_reporting_analytics,
            is_crud_admin=is_crud_admin,
            is_web_admin_portal=self._is_web_admin_portal(
                is_web, is_crud_admin, is_auth, is_ai, project_type_norm
            ),
            is_auth=is_auth,
            is_realtime=is_realtime,
            is_database_heavy=is_database_heavy,
            is_embedded=is_embedded,
            is_cross_platform_desktop=is_cross_platform_desktop,
            is_database_centered=is_database_centered,
            project_context=project_context,
        )

    def _build_project_context(self, data: dict[str, Any]) -> dict[str, Any]:
        """Build context flags and primary_context for scoring (Phase 2.3)."""
        project_type_norm = data.get("project_type_norm", "")
        platform_text = data.get("platform_text", "")
        goal_text = data.get("goal_text", "")
        features = data.get("features", [])
        features_text = data.get("features_text", "")
        combined = data.get("combined_text", "")
        timeline = data.get("timeline", "medium")
        stability = data.get("requirements_stability", "stable")
        security = data.get("security_requirements", "medium")
        performance = data.get("performance_requirements", "medium")
        budget = data.get("budget_constraints", "medium")

        is_ai_ml = self._is_ai_ml_project(
            project_type_norm, features, goal_text, combined
        )
        is_reporting_basic = self._is_reporting_analytics_profile(
            features, goal_text, combined, is_ai_ml
        )

        is_web = self._contains_any(
            combined,
            ("web", "web app", "web application", "web-based", "web application"),
        )
        is_mobile = self._contains_any(
            combined,
            (
                "mobile",
                "mobile app",
                "mobile application",
                "android",
                "ios",
            ),
        ) or "mobile application" in project_type_norm
        is_desktop = self._contains_any(
            combined, ("desktop", "desktop application")
        )
        is_backend_api = self._contains_any(
            combined,
            ("api", "backend", "backend system", "backend/api", "microservice"),
        )
        is_embedded_systems = self._contains_any(
            combined,
            (
                "embedded",
                "firmware",
                "operating system",
                "systems programming",
                "low-level",
                "hardware",
            ),
        ) or "embedded system" in project_type_norm
        is_cross_platform_desktop = self._contains_any(
            combined,
            (
                "cross-platform desktop",
                "lightweight desktop",
                "secure desktop",
                "cross-platform desktop",
            ),
        ) or (is_desktop and "cross" in combined)
        is_crud_admin_system = self._contains_any(
            combined,
            ("crud", "dashboard", "admin", "management system"),
        ) or "crud" in features_text
        is_realtime = self._contains_any(
            combined,
            ("real-time", "realtime", "notifications", "chat messaging", "chat"),
        )
        is_database_centered = (
            project_type_norm in DATABASE_CENTERED_TYPES
            or any(t in goal_text for t in DATABASE_CENTERED_TYPES)
            or self._contains_any(
                combined,
                ("data warehouse", "records management", "query-heavy"),
            )
        )

        primary_context = self._resolve_primary_context(
            is_embedded_systems=is_embedded_systems,
            is_ai_ml=is_ai_ml,
            is_database_centered=is_database_centered,
            is_mobile=is_mobile,
            is_desktop=is_desktop,
            is_cross_platform_desktop=is_cross_platform_desktop,
            is_backend_api=is_backend_api,
            is_web=is_web,
            is_crud_admin_system=is_crud_admin_system,
            project_type_norm=project_type_norm,
            platform_text=platform_text,
        )

        return {
            "is_web": is_web,
            "is_mobile": is_mobile,
            "is_desktop": is_desktop,
            "is_backend_api": is_backend_api,
            "is_ai_ml": is_ai_ml,
            "is_database_centered": is_database_centered,
            "is_embedded_systems": is_embedded_systems,
            "is_cross_platform_desktop": is_cross_platform_desktop,
            "is_crud_admin_system": is_crud_admin_system,
            "is_realtime": is_realtime,
            "is_reporting_basic": is_reporting_basic,
            "is_high_security": security == "high",
            "is_high_performance": performance == "high",
            "is_short_timeline": timeline == "short",
            "is_low_budget": budget == "low",
            "has_changing_requirements": stability == "changing",
            "primary_context": primary_context,
        }

    @staticmethod
    def _resolve_primary_context(
        *,
        is_embedded_systems: bool,
        is_ai_ml: bool,
        is_database_centered: bool,
        is_mobile: bool,
        is_desktop: bool,
        is_cross_platform_desktop: bool,
        is_backend_api: bool,
        is_web: bool,
        is_crud_admin_system: bool,
        project_type_norm: str,
        platform_text: str,
    ) -> str:
        if is_embedded_systems:
            return "embedded"
        if is_ai_ml:
            return "ai_ml"
        if is_mobile or "mobile application" in project_type_norm:
            if is_backend_api and "portal" in project_type_norm:
                return "web_crud"
            return "mobile_first"
        if is_cross_platform_desktop or (
            is_desktop and "web application" not in project_type_norm
        ):
            return "desktop"
        if is_backend_api and not is_web:
            return "backend_api"
        if is_database_centered and not is_web:
            return "database_centered"
        if is_web and is_crud_admin_system:
            return "web_crud"
        if is_web:
            return "web"
        if is_desktop:
            return "desktop"
        if is_backend_api:
            return "backend_api"
        if is_database_centered:
            return "database_centered"
        return "mixed"

    def calculate_scores(self, norm: NormalizedRequest) -> _ScoringContext:
        ctx = _ScoringContext()
        self._apply_all_scoring_rules(ctx, norm)
        if not norm.is_database_centered and ctx.language_scores.get("SQL", 0) > 0:
            non_sql = [s for n, s in ctx.language_scores.items() if n != "SQL"]
            if non_sql:
                cap = int(max(non_sql) * 0.85)
                ctx.language_scores["SQL"] = min(ctx.language_scores["SQL"], cap)
        return ctx

    def select_best_recommendation(
        self, ctx: _ScoringContext, norm: NormalizedRequest
    ) -> dict[str, Any]:
        stacks = self._rank_stack_candidates(ctx, norm, include_all=True)
        if not stacks:
            lang = max(ctx.language_scores, key=ctx.language_scores.get)
            fw = self._default_framework_for_language(lang, ctx, norm)
            sdlc = max(ctx.sdlc_scores, key=ctx.sdlc_scores.get)
            stack_score = self._compute_final_stack_score(
                lang, fw, sdlc, ctx, norm
            )
            return {
                "language": lang,
                "framework": fw,
                "sdlc": sdlc,
                "stack_score": stack_score,
            }
        best = dict(stacks[0])
        if best["language"] == "SQL" and not norm.is_database_centered:
            for candidate in stacks:
                if candidate["language"] != "SQL":
                    best = dict(candidate)
                    break
        corrected, reject_reason = self._apply_category_winner(best, stacks, norm)
        if reject_reason and self._scoring_debug_enabled():
            log.info(
                "Category winner rejected %s + %s: %s",
                best["language"],
                best["framework"],
                reject_reason,
            )
        return corrected

    def calculate_confidence(
        self,
        best: dict[str, Any],
        ranked_stacks: list[dict[str, Any]],
        norm: NormalizedRequest | None = None,
        user_pref: dict[str, Any] | None = None,
    ) -> int:
        """Relative confidence from stack ranking margin, context fit, and competition."""
        selected_score = int(best.get("stack_score", 0))
        second_score = self._second_best_stack_score(best, ranked_stacks)
        top5 = ranked_stacks[:5]
        avg_top5 = (
            sum(int(s.get("stack_score", 0)) for s in top5) / len(top5)
            if top5
            else float(selected_score)
        )

        margin = selected_score - second_score
        if margin >= 80:
            margin_points = 15
        elif margin >= 50:
            margin_points = 10
        elif margin >= 25:
            margin_points = 6
        elif margin >= 10:
            margin_points = 3
        else:
            margin_points = -5

        top_possible_reference = max(selected_score, int(avg_top5) + 60)
        fit_ratio = selected_score / max(top_possible_reference, 1)
        base_confidence = 60 + min(25, round(fit_ratio * 25))

        cluster_spread = selected_score - int(avg_top5)
        if cluster_spread < 15:
            cluster_penalty = -7
        elif cluster_spread < 30:
            cluster_penalty = -4
        else:
            cluster_penalty = 0

        tight_field_penalty = 0
        if len(top5) >= 3:
            top5_scores = [int(s.get("stack_score", 0)) for s in top5]
            if max(top5_scores) - min(top5_scores) < 45:
                tight_field_penalty = -5

        context_points = (
            self._confidence_context_points(best, norm) if norm else 0
        )

        lang = best.get("language", "")
        fw = best.get("framework", "")
        compatibility_points = (
            5
            if self.is_compatible_stack(lang, fw)
            else -20
        )

        if margin < 10:
            competition_penalty = -8
        elif margin < 25:
            competition_penalty = -5
        else:
            competition_penalty = 0

        ambiguity_penalty = 0
        if norm:
            if norm.project_context.get("primary_context") == "mixed":
                ambiguity_penalty -= 5
            if self._is_mixed_context(norm):
                ambiguity_penalty -= 3

        pref_adjustment = 0
        if user_pref and user_pref.get("is_provided") and user_pref.get("is_compatible"):
            pref_score = int(user_pref.get("score", 0))
            if (
                user_pref.get("alignment_status") in ("Partially aligned", "Not selected")
                and pref_score >= selected_score - 20
            ):
                pref_adjustment = -4

        confidence = (
            base_confidence
            + margin_points
            + context_points
            + compatibility_points
            + competition_penalty
            + ambiguity_penalty
            + cluster_penalty
            + tight_field_penalty
            + pref_adjustment
        )
        return max(60, min(95, int(confidence)))

    @staticmethod
    def _second_best_stack_score(
        best: dict[str, Any], ranked_stacks: list[dict[str, Any]]
    ) -> int:
        """Score of the best competing stack that is not the selected triple."""
        best_key = (
            best.get("language"),
            best.get("framework"),
            best.get("sdlc"),
        )
        for stack in ranked_stacks:
            key = (stack.get("language"), stack.get("framework"), stack.get("sdlc"))
            if key != best_key:
                return int(stack.get("stack_score", 0))
        for stack in ranked_stacks[1:]:
            return int(stack.get("stack_score", 0))
        return 0

    def _confidence_context_points(
        self, best: dict[str, Any], norm: NormalizedRequest
    ) -> int:
        primary = norm.project_context.get("primary_context", "mixed")
        lang = best.get("language", "")
        fw = best.get("framework", "")

        def matches_primary() -> bool:
            if primary == "mobile_first":
                return fw == "Flutter" and lang == "Dart"
            if primary == "web_crud":
                return fw in (
                    "Laravel",
                    "Django",
                    "Ruby on Rails",
                    "ASP.NET Core",
                    "Next.js",
                    "Spring Boot",
                )
            if primary == "backend_api":
                return fw in (
                    "FastAPI",
                    "Express.js",
                    "NestJS",
                    "Spring Boot",
                    "ASP.NET Core",
                    "Laravel",
                    "Django",
                    "Flask",
                )
            if primary == "desktop":
                return fw == "Tauri" or (fw == "Flutter" and lang == "Dart")
            if primary == "embedded":
                return lang in ("C", "C++", "Rust")
            if primary == "ai_ml":
                return lang == "Python" and fw in ("FastAPI", "Django", "Flask")
            if primary == "web":
                return norm.is_web
            return False

        def partial_match() -> bool:
            if primary == "mobile_first":
                return lang in ("Kotlin", "Swift") or fw == "Flutter"
            if primary in ("web_crud", "web"):
                return lang in ("PHP", "Python", "Ruby", "Java", "C#", "TypeScript")
            if primary == "backend_api":
                return lang in ("Python", "JavaScript", "TypeScript", "Java", "C#", "Go")
            return False

        if matches_primary():
            return 8
        if partial_match():
            return 3
        return -10

    def generate_reasons(
        self,
        norm: NormalizedRequest,
        best: dict[str, Any],
        reasons: dict[str, str],
        confidence: int,
        label: str,
    ) -> str:
        features = ", ".join(norm.selected_features) or "general application features"
        conf_text = {
            "Very High": "Several weighted criteria matched strongly with a clear margin.",
            "High": "Multiple project criteria aligned well with this stack.",
            "Moderate": "The stack fits, but close alternatives exist — review them.",
            "Low": "Inputs may be mixed; compare alternatives before committing.",
        }.get(label, "")
        return (
            f"For '{norm.project_name}' ({norm.project_type}), StackWise recommends "
            f"{best['language']} with {best['framework']} using {best['sdlc']} "
            f"(confidence {confidence}/100, {label}).\n\n"
            f"Project context: platform {norm.preferred_platform}, features ({features}), "
            f"timeline {norm.timeline}, team size {norm.team_size}, experience "
            f"{norm.development_experience}.\n\n"
            f"Language: {best['language']} — {reasons['language']}\n\n"
            f"Framework: {best['framework']} — {reasons['framework']}\n\n"
            f"SDLC: {best['sdlc']} — {reasons['sdlc']}\n\n"
            f"{conf_text} This is decision-support guidance, not an absolute best technology."
        )

    def generate_alternative_stacks(
        self,
        ctx: _ScoringContext,
        norm: NormalizedRequest,
        best: dict[str, Any],
        ranked: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        winner_score = int(best.get("stack_score", 0))
        resolved = self._resolve_alternative_stack_candidates(
            ctx, norm, best, ranked
        )
        alts: list[dict[str, Any]] = []
        seen_triples: set[tuple[str, str, str]] = set()
        for stack in resolved:
            triple = (stack["language"], stack["framework"], stack["sdlc"])
            if triple in seen_triples:
                continue
            if triple == (
                best["language"],
                best["framework"],
                best["sdlc"],
            ):
                continue
            seen_triples.add(triple)
            alts.append(self._stack_to_alternative(stack, norm, "System Alternative"))
            if len(alts) >= 5:
                break
        if len(alts) < 3:
            for stack in resolved:
                if len(alts) >= 3:
                    break
                triple = (stack["language"], stack["framework"], stack["sdlc"])
                if triple in seen_triples:
                    continue
                if (
                    stack["language"] == best["language"]
                    and stack["framework"] == best["framework"]
                    and stack["sdlc"] == best["sdlc"]
                ):
                    continue
                seen_triples.add(triple)
                alts.append(self._stack_to_alternative(stack, norm, "System Alternative"))
        self._normalize_alternative_fit_percents(alts, winner_score)
        return alts[:5]

    def generate_why_not_this(
        self,
        norm: NormalizedRequest,
        best: dict[str, Any],
        ranked: list[dict[str, Any]],
        user_pref: dict[str, Any],
        ctx: _ScoringContext,
    ) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        seen: set[str] = set()

        def add(
            stack_label: str,
            reason: str,
            when_better: str,
            source: str = "System Alternative",
        ) -> None:
            key = stack_label.lower()
            if key in seen:
                return
            seen.add(key)
            items.append(
                {
                    "technology_or_stack": stack_label,
                    "reason": reason,
                    "when_it_is_better": when_better,
                    "source": source,
                }
            )

        contextual = [
            (
                "Flutter + Agile",
                "Flutter is stronger for mobile and cross-platform UI than pure web admin systems.",
                "Choose Flutter when the primary deliverable is mobile or cross-platform client apps.",
            ),
            (
                "Spring Boot + Waterfall",
                "Spring Boot adds enterprise setup that may be heavy for beginner teams on short timelines.",
                "Choose Spring Boot for large teams, stable requirements, and long enterprise timelines.",
            ),
            (
                "FastAPI + Iterative",
                "FastAPI is API-first; CRUD/admin-heavy web portals may benefit more from full-stack web frameworks.",
                "Choose FastAPI when APIs, ML services, or microservices dominate the architecture.",
            ),
            (
                "Angular / NestJS",
                "Enterprise Angular/NestJS stacks need more structure and learning time than rapid MVP stacks.",
                "Choose them when the team is advanced and long-term maintainability outweighs speed-to-MVP.",
            ),
            (
                "Tauri + Iterative",
                "Tauri targets desktop shells; it is not ideal when the project is only a hosted web application.",
                "Choose Tauri for cross-platform desktop apps needing a lightweight secure shell.",
            ),
            (
                "Flet + Agile",
                "Flet is strongest for Python-centered UI development, internal tools, prototypes, dashboards, and local/cross-platform interfaces.",
                "Choose Flet when the team wants Python-based UI for dashboards, internal tools, or AI-assisted tools rather than a traditional web stack.",
            ),
            (
                "C / C++ / Rust (systems)",
                "Systems languages are unnecessary for ordinary web CRUD unless performance or firmware dominates.",
                "Choose them for embedded, firmware, or performance-critical native components.",
            ),
            (
                "Waterfall + V-Model",
                "Predictive models fit stable requirements; they struggle when requirements change frequently.",
                "Choose Waterfall/V-Model when scope, compliance, and documentation are fixed early.",
            ),
            (
                "Big Bang Model",
                "Big Bang lacks structured control for medium/high complexity delivery.",
                "Only consider for very small, low-risk experiments with minimal coordination needs.",
            ),
        ]
        for label, reason, when in contextual:
            if len(items) >= 3:
                break
            if label.split()[0] in best["language"]:
                continue
            add(label, reason, when)

        for stack in ranked[:4]:
            if len(items) >= 6:
                break
            label = f"{stack['language']} + {stack['framework']} + {stack['sdlc']}"
            if label.startswith(
                f"{best['language']} + {best['framework']}"
            ):
                continue
            add(
                label,
                (
                    f"This compatible stack scored {stack['stack_score']} points versus "
                    f"{best['stack_score']} for the selected recommendation given current inputs."
                ),
                (
                    "Prefer this stack when your team has stronger experience with it or when "
                    "project constraints align more closely with its strengths."
                ),
            )

        if (
            user_pref.get("is_provided")
            and user_pref.get("is_compatible")
            and user_pref.get("language") == best["language"]
            and user_pref.get("framework") == best["framework"]
            and user_pref.get("sdlc")
            and user_pref.get("sdlc") != best["sdlc"]
        ):
            pref_label = self._format_preferred_stack_label(user_pref)
            add(
                f"User Preferred Stack: {pref_label}",
                self._preferred_sdlc_mismatch_summary(
                    user_pref["language"],
                    user_pref["framework"],
                    user_pref["sdlc"],
                    best["sdlc"],
                    norm,
                ),
                (
                    f"{user_pref['sdlc']} is better when requirements are stable, "
                    "documentation-heavy governance is required, and scope is largely fixed."
                ),
                "User Preferred Stack",
            )

        if user_pref.get("is_provided") and user_pref.get("alignment_status") not in (
            "Aligned",
            "Partially aligned",
            None,
        ):
            pref_label = self._format_preferred_stack_label(user_pref)
            if not user_pref.get("is_compatible"):
                add(
                    f"User Preferred Stack: {pref_label}",
                    user_pref.get("comparison_summary", ""),
                    (
                        "Use a compatible language-framework pair if you want to follow your "
                        "preference while staying technically valid."
                    ),
                    "User Preferred Stack",
                )
            elif user_pref.get("alignment_status") != "Aligned":
                add(
                    f"User Preferred Stack: {pref_label}",
                    user_pref.get("comparison_summary", ""),
                    (
                        "Your preferred stack would be better if requirements stability, timeline, "
                        "or team experience align more with its strengths."
                    ),
                    "User Preferred Stack",
                )

        preferred_items = [i for i in items if i.get("source") == "User Preferred Stack"]
        other_items = [i for i in items if i.get("source") != "User Preferred Stack"]
        items = preferred_items + other_items

        return items[:8] if items else items

    def generate_risk_analysis(self, norm: NormalizedRequest) -> list[dict[str, Any]]:
        risks: list[dict[str, Any]] = []

        def push(risk: str, reason: str, impact: str, mitigation: str) -> None:
            risks.append(
                {
                    "risk": risk,
                    "reason": reason,
                    "impact": impact,
                    "mitigation": mitigation,
                }
            )

        if norm.timeline == "short":
            push(
                "Time constraint",
                "The timeline is short relative to typical delivery cycles.",
                "Incomplete features or reduced testing before release.",
                "Prioritize MVP scope, automate testing, and defer non-critical features.",
            )
        if norm.complexity == "high":
            push(
                "Development complexity",
                "High complexity increases coordination and defect risk.",
                "Schedule slips and harder debugging.",
                "Modularize work, document interfaces, and review architecture early.",
            )
        if norm.team_size <= 2:
            push(
                "Limited manpower",
                "A very small team must cover many roles.",
                "Bottlenecks on critical paths.",
                "Reduce parallel workstreams and keep scope narrow.",
            )
        if norm.security_requirements == "high":
            push(
                "Data security and privacy",
                "Elevated security requirements demand rigorous controls.",
                "Data breaches or compliance failures.",
                "Threat model early, enforce authZ/authN, and security-test each sprint.",
            )
        if norm.is_ai:
            push(
                "AI implementation uncertainty",
                "AI/ML features introduce model and data-quality unknowns.",
                "Unmet accuracy or latency expectations.",
                "Prototype models early, define metrics, and plan fallback behavior.",
            )
        if norm.deployment_preference == "shared hosting":
            push(
                "Deployment limitations",
                "Shared hosting restricts runtimes and background workers.",
                "Blocked features (queues, websockets, custom runtimes).",
                "Confirm host capabilities or plan a cloud/container path.",
            )
        if norm.performance_requirements == "high":
            push(
                "Performance optimization risk",
                "High performance needs may be discovered late.",
                "Slow response under load.",
                "Profile early, set benchmarks, and load-test before launch.",
            )
        if norm.requirements_stability == "changing":
            push(
                "Scope creep risk",
                "Requirements are expected to change during delivery.",
                "Rework and unstable priorities.",
                "Use iterative SDLC, short feedback loops, and visible backlogs.",
            )
        if norm.development_experience == "beginner" and norm.complexity == "high":
            push(
                "Learning curve risk",
                "Beginner experience paired with high complexity.",
                "Slower delivery and more defects.",
                "Add mentoring, training time, and simpler architectural choices.",
            )
        if norm.is_realtime:
            push(
                "Real-time complexity risk",
                "Real-time/chat/notification features need reliable event flows.",
                "Connection drops or inconsistent live updates.",
                "Choose proven real-time patterns, test under load, and monitor channels.",
            )
        if not risks:
            push(
                "General delivery risk",
                "No major risks were flagged from inputs alone.",
                "Unknown issues may still appear during implementation.",
                "Maintain code review, testing, and documentation discipline.",
            )
        return risks

    def generate_skill_gap_analysis(
        self, norm: NormalizedRequest, best: dict[str, Any]
    ) -> list[dict[str, Any]]:
        fw = best["framework"]
        profile = FRAMEWORK_SKILL_MAP.get(fw, {})
        user_level = norm.development_experience
        required = profile.get("required_level", "Intermediate")
        gap = self._gap_level(user_level, required)
        items: list[dict[str, Any]] = [
            {
                "skill": profile.get("skill", fw),
                "required_level": required,
                "user_level": user_level.title(),
                "gap_level": gap,
                "suggestion": profile.get(
                    "suggestion",
                    f"Study {fw} fundamentals and build a small practice module.",
                ),
            }
        ]
        if fw == "Flet":
            for extra in (
                {
                    "skill": "Flet controls and layout system",
                    "required_level": "Intermediate",
                    "user_level": user_level.title(),
                    "gap_level": gap,
                    "suggestion": "Practice Row, Column, Container, Card, ListView, and NavigationRail patterns.",
                },
                {
                    "skill": "Event handling and navigation in Flet",
                    "required_level": "Intermediate",
                    "user_level": user_level.title(),
                    "gap_level": gap,
                    "suggestion": "Learn click handlers, routing/navigation, and state updates across pages.",
                },
                {
                    "skill": "Database and Python service integration",
                    "required_level": "Intermediate",
                    "user_level": user_level.title(),
                    "gap_level": gap,
                    "suggestion": "Connect Flet UI to Python services, databases, and APIs used by the project.",
                },
                {
                    "skill": "Flet packaging and deployment",
                    "required_level": "Beginner",
                    "user_level": user_level.title(),
                    "gap_level": "Low" if user_level == "advanced" else "Moderate",
                    "suggestion": "Review flet build and platform packaging basics for your target platform.",
                },
            ):
                items.append(extra)
            if norm.is_ai or "chatbot" in norm.combined_text:
                items.append(
                    {
                        "skill": "API / Ollama integration",
                        "required_level": "Intermediate",
                        "user_level": user_level.title(),
                        "gap_level": gap,
                        "suggestion": "Wire AI/chatbot features to local or remote Python AI services from Flet.",
                    }
                )
        if norm.development_experience == "beginner":
            items.append(
                {
                    "skill": best["language"],
                    "required_level": "Intermediate",
                    "user_level": "Beginner",
                    "gap_level": "Moderate",
                    "suggestion": (
                        f"Learn core {best['language']} syntax, tooling, and debugging before "
                        f"scaling feature work."
                    ),
                }
            )
        return items

    def generate_project_roadmap(
        self, norm: NormalizedRequest, selected_sdlc: str, selected_framework: str = ""
    ) -> list[dict[str, Any]]:
        template = ROADMAP_TEMPLATES.get(selected_sdlc, ROADMAP_TEMPLATES["Agile"])
        phases = list(template)
        if norm.timeline == "short":
            phases = phases[: max(3, len(phases) - 1)]
        if norm.complexity == "high":
            for phase in phases:
                objs = list(phase.get("objectives", []))
                if "testing" not in " ".join(objs).lower():
                    phase["objectives"] = [*objs, "Testing and risk review"]
        if norm.team_size <= 2:
            for phase in phases:
                pri = list(phase.get("priorities", []))
                phase["priorities"] = [p for p in pri if "parallel" not in p.lower()][:3]
        if selected_framework == "Flet":
            phases = self._flet_roadmap_adjustments(phases)
        return phases

    def _flet_roadmap_adjustments(
        self, phases: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Append Flet-specific delivery objectives when Flet is recommended."""
        if not phases:
            return phases
        first = dict(phases[0])
        objectives = list(first.get("objectives", []))
        deliverables = list(first.get("deliverables", []))
        for item in (
            "UI layout planning using Flet controls",
            "Python service integration plan",
        ):
            if item not in objectives:
                objectives.append(item)
        for item in ("Database connection testing", "Flet navigation and state management"):
            if item not in deliverables:
                deliverables.append(item)
        first["objectives"] = objectives
        first["deliverables"] = deliverables
        phases[0] = first
        if len(phases) > 1:
            last = dict(phases[-1])
            deliverables = list(last.get("deliverables", []))
            if "Packaging or deployment testing" not in deliverables:
                deliverables.append("Packaging or deployment testing")
            last["deliverables"] = deliverables
            phases[-1] = last
        return phases

    def analyze_user_preferred_stack(
        self,
        norm: NormalizedRequest,
        best: dict[str, Any],
        language_scores: dict[str, int],
        framework_scores: dict[str, int],
        sdlc_scores: dict[str, int],
        ctx: _ScoringContext,
    ) -> dict[str, Any]:
        lang = norm.user_preferred_language
        fw = norm.user_preferred_framework
        sdlc = norm.user_preferred_sdlc
        reason = norm.user_preferred_reason
        provided = bool(lang or fw or sdlc)

        result: dict[str, Any] = {
            "language": lang,
            "framework": fw,
            "sdlc": sdlc,
            "reason": reason,
            "is_provided": provided,
            "is_compatible": True,
            "alignment_status": "",
            "score": 0,
            "comparison_summary": "",
        }

        if not provided:
            result["comparison_summary"] = "No user preferred stack was provided."
            return result

        compat_msg = self._compatibility_message(lang, fw)
        if compat_msg:
            result["is_compatible"] = False
            result["alignment_status"] = "Incompatible"
            result["comparison_summary"] = compat_msg
            return result

        if not lang and not fw and not sdlc:
            result["comparison_summary"] = "No user preferred stack was provided."
            result["is_provided"] = False
            return result

        partial = not (lang and fw and sdlc)
        score = 0
        if lang:
            score += language_scores.get(lang, 0)
        if fw:
            score += framework_scores.get(fw, 0)
        if sdlc:
            score += sdlc_scores.get(sdlc, 0)
        result["score"] = score

        selected_label = f"{best['language']} + {best['framework']} + {best['sdlc']}"
        pref_label = self._format_preferred_stack_label(result)

        if (
            lang == best["language"]
            and fw == best["framework"]
            and sdlc == best["sdlc"]
        ):
            result["alignment_status"] = "Aligned"
            result["comparison_summary"] = (
                "Your preferred stack aligns with the StackWise AI recommendation."
            )
            return result

        if (
            lang == best["language"]
            and fw == best["framework"]
            and sdlc
            and sdlc != best["sdlc"]
        ):
            result["alignment_status"] = "Partially aligned"
            result["comparison_summary"] = self._preferred_sdlc_mismatch_summary(
                lang, fw, sdlc, best["sdlc"], norm
            )
            return result

        if partial:
            result["alignment_status"] = "Partial preference"
            result["comparison_summary"] = (
                f"You provided a partial preference ({pref_label}). "
                "Only the selected parts were compared; missing framework or SDLC "
                "values were not assumed."
            )
            return result

        if score >= best.get("stack_score", 0) - 15:
            result["alignment_status"] = "Partially aligned"
            result["comparison_summary"] = (
                f"Your preferred stack ({pref_label}) is compatible and competitive "
                f"(score {score}) but {selected_label} ranked higher for the current inputs."
            )
        else:
            result["alignment_status"] = "Not selected"
            result["comparison_summary"] = (
                f"Your preferred stack is valid, but it scored lower than the selected "
                f"recommendation because the current project inputs emphasize changing "
                f"requirements, timeline, security, platform fit, or other weighted factors."
            )
        return result

    # ------------------------------------------------------------------
    # Scoring rules
    # ------------------------------------------------------------------

    def _apply_all_scoring_rules(self, ctx: _ScoringContext, n: NormalizedRequest) -> None:
        web = n.is_web
        mobile = n.is_mobile
        desktop = n.is_desktop
        api = n.is_api_backend
        ai = n.is_ai
        reporting = n.is_reporting_analytics
        crud = n.is_crud_admin
        web_admin = n.is_web_admin_portal
        auth = n.is_auth
        rt = n.is_realtime
        db_heavy = n.is_database_heavy
        embedded = n.is_embedded
        xp_desktop = n.is_cross_platform_desktop or desktop
        primary = n.project_context.get("primary_context", "mixed")

        if web:
            for lang, pts in (
                ("PHP", 25),
                ("JavaScript", 20),
                ("TypeScript", 15),
                ("Python", 15),
                ("Ruby", 10),
                ("C#", 10),
            ):
                ctx.add_language_score(lang, pts, "Web application platform fit")
            for fw, pts in (
                ("Laravel", 25),
                ("React", 20),
                ("Vue", 15),
                ("Next.js", 15),
                ("Django", 15),
                ("Flask", 10),
                ("Angular", 15),
                ("Ruby on Rails", 15),
                ("ASP.NET Core", 10),
            ):
                ctx.add_framework_score(fw, pts, "Web framework ecosystem")
            for sdlc, pts in (("Agile", 15), ("RAD", 10)):
                ctx.add_sdlc_score(sdlc, pts, "Iterative web delivery")

        if mobile:
            for lang, pts in (
                ("Dart", 30),
                ("Kotlin", 20),
                ("Swift", 20),
                ("JavaScript", 15),
                ("TypeScript", 15),
            ):
                ctx.add_language_score(lang, pts, "Mobile or cross-platform client")
            ctx.add_framework_score("Flutter", 35, "Cross-platform mobile UI")
            for sdlc, pts in (("Agile", 20), ("Prototype Model", 10)):
                ctx.add_sdlc_score(sdlc, pts, "Mobile iterative delivery")
            if "ios" in n.combined_text:
                ctx.add_language_score("Swift", 25, "iOS platform emphasis")
            if "android" in n.combined_text:
                ctx.add_language_score("Kotlin", 25, "Android platform emphasis")
            if "cross" in n.combined_text:
                ctx.add_framework_score("React", 10, "Cross-platform web-mobile UI option")

        if desktop:
            for lang, pts in (
                ("Java", 25),
                ("C#", 25),
                ("Python", 15),
                ("C++", 25),
                ("C", 15),
                ("Rust", 25),
                ("JavaScript", 10),
                ("TypeScript", 15),
            ):
                ctx.add_language_score(lang, pts, "Desktop application fit")
            for fw, pts in (
                ("Spring Boot", 10),
                ("ASP.NET Core", 20),
                ("Tauri", 30),
                ("Flutter", 15),
                ("Flet", 25),
            ):
                ctx.add_framework_score(fw, pts, "Desktop runtime/framework")
            for sdlc, pts in (("Waterfall", 15), ("Iterative", 15)):
                ctx.add_sdlc_score(sdlc, pts, "Desktop planning model")
            if "windows" in n.combined_text:
                ctx.add_language_score("C#", 10, "Windows desktop emphasis")

        if api:
            for lang, pts in (
                ("Python", 25),
                ("PHP", 20),
                ("JavaScript", 20),
                ("TypeScript", 15),
                ("Go", 30),
                ("Rust", 15),
                ("C#", 20),
                ("Java", 20),
            ):
                ctx.add_language_score(lang, pts, "API/backend service fit")
            for fw, pts in (
                ("FastAPI", 25),
                ("Laravel", 20),
                ("Express.js", 25),
                ("Spring Boot", 20),
                ("NestJS", 25),
                ("Django", 15),
                ("Flask", 15),
                ("ASP.NET Core", 20),
            ):
                ctx.add_framework_score(fw, pts, "Backend/API framework")
            for sdlc, pts in (
                ("Agile", 15),
                ("Iterative", 15),
                ("Kanban", 10),
                ("DevOps", 15),
            ):
                ctx.add_sdlc_score(sdlc, pts, "Service delivery lifecycle")

        if ai:
            for lang, pts in (("Python", 35), ("JavaScript", 10), ("TypeScript", 10), ("SQL", 20)):
                ctx.add_language_score(lang, pts, "AI/ML project profile")
            for fw, pts in (
                ("FastAPI", 25),
                ("Django", 15),
                ("Flask", 15),
                ("React", 10),
                ("Next.js", 10),
                ("Flet", 15),
            ):
                ctx.add_framework_score(fw, pts, "AI/ML API or serving stack")
            for sdlc, pts in (
                ("Iterative", 20),
                ("Agile", 15),
                ("Spiral", 10),
                ("Prototype Model", 10),
                ("DevOps", 10),
            ):
                ctx.add_sdlc_score(sdlc, pts, "Experimental AI/ML delivery")

        if reporting and not ai:
            self._score_reporting_context(ctx, n, primary)

        if crud:
            self._score_crud_context(ctx, n, primary)

        if auth:
            self._score_auth_context(ctx, n, primary)

        if "maps location" in n.features_text or "notifications" in n.features_text:
            self._score_mobile_feature_signals(ctx, n, primary)

        if rt:
            for lang, pts in (
                ("JavaScript", 20),
                ("TypeScript", 15),
                ("Python", 10),
                ("Go", 15),
            ):
                ctx.add_language_score(lang, pts, "Real-time/event-driven fit")
            for fw, pts in (
                ("React", 15),
                ("Express.js", 20),
                ("Laravel", 10),
                ("NestJS", 20),
                ("Vue", 10),
                ("Next.js", 10),
                ("FastAPI", 10),
            ):
                ctx.add_framework_score(fw, pts, "Real-time capable framework")
            for sdlc, pts in (
                ("Agile", 15),
                ("Iterative", 10),
                ("Kanban", 10),
                ("Extreme Programming (XP)", 10),
            ):
                ctx.add_sdlc_score(sdlc, pts, "Fast feedback for real-time features")

        if n.security_requirements == "high":
            for lang, pts in (
                ("Java", 15),
                ("C#", 15),
                ("Rust", 20),
                ("Go", 10),
                ("TypeScript", 10),
                ("C++", 10),
                ("C", 5),
            ):
                ctx.add_language_score(lang, pts, "High-security project profile")
            for fw, pts in (
                ("Laravel", 15),
                ("Spring Boot", 20),
                ("ASP.NET Core", 20),
                ("NestJS", 15),
                ("Django", 15),
            ):
                ctx.add_framework_score(fw, pts, "Security-oriented framework")
            for sdlc, pts in (
                ("Waterfall", 15),
                ("Spiral", 20),
                ("V-Model", 20),
                ("DevOps", 15),
            ):
                ctx.add_sdlc_score(sdlc, pts, "Risk-managed lifecycle")

        if n.performance_requirements == "high":
            for lang, pts in (
                ("Java", 20),
                ("C#", 20),
                ("Go", 25),
                ("Rust", 30),
                ("C++", 30),
                ("C", 25),
                ("TypeScript", 10),
            ):
                ctx.add_language_score(lang, pts, "Performance-critical profile")
            for fw, pts in (
                ("Spring Boot", 15),
                ("ASP.NET Core", 15),
                ("FastAPI", 10),
                ("NestJS", 10),
                ("Tauri", 10),
            ):
                ctx.add_framework_score(fw, pts, "Performance-capable runtime")
            for sdlc, pts in (
                ("Spiral", 15),
                ("Iterative", 15),
                ("DevOps", 10),
                ("Kanban", 5),
            ):
                ctx.add_sdlc_score(sdlc, pts, "Performance tuning cycles")

        if n.budget_constraints == "low":
            self._score_low_budget(ctx, primary)
            for sdlc, pts in (
                ("RAD", 15),
                ("Agile", 10),
                ("Lean", 15),
                ("Kanban", 10),
                ("Prototype Model", 10),
            ):
                ctx.add_sdlc_score(sdlc, pts, "Lean delivery")

        if n.timeline == "short":
            self._score_short_timeline(ctx, primary)
            for sdlc, pts in (
                ("RAD", 25),
                ("Agile", 20),
                ("Prototype Model", 15),
                ("Lean", 15),
                ("Kanban", 15),
            ):
                ctx.add_sdlc_score(sdlc, pts, "Short timeline delivery")
            if n.complexity == "low" and n.team_size <= 2:
                ctx.add_sdlc_score("Big Bang Model", 5, "Very small low-risk shortcut")

        elif n.timeline == "medium":
            for fw, pts in (
                ("Laravel", 10),
                ("React", 10),
                ("Flutter", 10),
                ("Django", 10),
                ("FastAPI", 10),
                ("Next.js", 10),
                ("NestJS", 10),
            ):
                ctx.add_framework_score(fw, pts, "Balanced delivery pace")
            for sdlc, pts in (
                ("Agile", 20),
                ("Iterative", 15),
                ("Scrum", 15),
                ("Kanban", 10),
                ("Incremental", 15),
                ("Feature-Driven Development (FDD)", 10),
            ):
                ctx.add_sdlc_score(sdlc, pts, "Medium timeline planning")

        elif n.timeline == "long":
            for lang, pts in (("Java", 15), ("C#", 15), ("C++", 10), ("Rust", 10)):
                ctx.add_language_score(lang, pts, "Long-horizon enterprise stack")
            for fw, pts in (
                ("Spring Boot", 15),
                ("ASP.NET Core", 15),
                ("Angular", 10),
                ("NestJS", 10),
            ):
                ctx.add_framework_score(fw, pts, "Enterprise long project framework")
            for sdlc, pts in (
                ("Waterfall", 20),
                ("Spiral", 15),
                ("Iterative", 15),
                ("V-Model", 15),
                ("DevOps", 10),
                ("Feature-Driven Development (FDD)", 15),
                ("Incremental", 10),
            ):
                ctx.add_sdlc_score(sdlc, pts, "Long timeline governance")

        exp = n.development_experience
        if exp == "beginner":
            for lang, pts in (("PHP", 15), ("Python", 15), ("JavaScript", 10), ("Ruby", 10), ("SQL", 10)):
                ctx.add_language_score(lang, pts, "Beginner-friendly language")
            for fw, pts in (
                ("Laravel", 15),
                ("Flutter", 10),
                ("Django", 10),
                ("Flask", 10),
                ("React", 5),
                ("Vue", 10),
                ("Ruby on Rails", 10),
            ):
                ctx.add_framework_score(fw, pts, "Beginner-friendly framework")
            for sdlc, pts in (
                ("RAD", 20),
                ("Prototype Model", 15),
                ("Agile", 10),
                ("Lean", 10),
                ("Kanban", 10),
            ):
                ctx.add_sdlc_score(sdlc, pts, "Beginner feedback loops")
        elif exp == "intermediate":
            for fw, pts in (
                ("Laravel", 15),
                ("React", 15),
                ("FastAPI", 15),
                ("Flutter", 15),
                ("Django", 15),
                ("Next.js", 10),
                ("Express.js", 10),
                ("Vue", 10),
                ("Angular", 10),
                ("NestJS", 10),
                ("Spring Boot", 10),
                ("ASP.NET Core", 10),
            ):
                ctx.add_framework_score(fw, pts, "Intermediate team fit")
            for sdlc, pts in (
                ("Agile", 20),
                ("Iterative", 10),
                ("Scrum", 10),
                ("Kanban", 10),
                ("Incremental", 10),
            ):
                ctx.add_sdlc_score(sdlc, pts, "Intermediate planning")
        elif exp == "advanced":
            for lang, pts in (
                ("TypeScript", 15),
                ("Java", 15),
                ("C#", 15),
                ("C++", 20),
                ("C", 15),
                ("Rust", 20),
                ("Go", 15),
            ):
                ctx.add_language_score(lang, pts, "Advanced team capability")
            for fw, pts in (
                ("Spring Boot", 20),
                ("ASP.NET Core", 20),
                ("Next.js", 15),
                ("Angular", 15),
                ("NestJS", 20),
                ("Tauri", 15),
            ):
                ctx.add_framework_score(fw, pts, "Advanced architecture framework")
            for sdlc, pts in (
                ("Spiral", 20),
                ("Scrum", 15),
                ("DevOps", 20),
                ("V-Model", 15),
                ("Feature-Driven Development (FDD)", 15),
                ("Extreme Programming (XP)", 10),
            ):
                ctx.add_sdlc_score(sdlc, pts, "Advanced governance")

        if n.team_size <= 2:
            for fw, pts in (
                ("Laravel", 15),
                ("FastAPI", 10),
                ("Flutter", 10),
                ("Flask", 10),
                ("Django", 10),
                ("Vue", 10),
                ("Ruby on Rails", 10),
            ):
                ctx.add_framework_score(fw, pts, "Small team velocity")
            for sdlc, pts in (
                ("RAD", 20),
                ("Agile", 10),
                ("Lean", 15),
                ("Kanban", 15),
                ("Prototype Model", 10),
            ):
                ctx.add_sdlc_score(sdlc, pts, "Small team process")
        elif 3 <= n.team_size <= 5:
            for fw, pts in (
                ("Laravel", 10),
                ("React", 10),
                ("Spring Boot", 10),
                ("Django", 10),
                ("FastAPI", 10),
                ("Next.js", 10),
                ("Flutter", 10),
                ("ASP.NET Core", 10),
            ):
                ctx.add_framework_score(fw, pts, "Medium team coordination")
            for sdlc, pts in (
                ("Agile", 20),
                ("Scrum", 15),
                ("Incremental", 10),
                ("Kanban", 10),
                ("Feature-Driven Development (FDD)", 10),
            ):
                ctx.add_sdlc_score(sdlc, pts, "Medium team cadence")
        elif n.team_size >= 6:
            for lang, pts in (("Java", 15), ("C#", 15), ("TypeScript", 15)):
                ctx.add_language_score(lang, pts, "Large team enterprise language")
            for fw, pts in (
                ("Spring Boot", 20),
                ("ASP.NET Core", 20),
                ("Angular", 20),
                ("NestJS", 15),
            ):
                ctx.add_framework_score(fw, pts, "Large team enterprise framework")
            for sdlc, pts in (
                ("Scrum", 20),
                ("Waterfall", 10),
                ("DevOps", 20),
                ("V-Model", 15),
                ("Feature-Driven Development (FDD)", 20),
                ("Incremental", 15),
            ):
                ctx.add_sdlc_score(sdlc, pts, "Large team governance")

        if n.complexity == "high":
            for lang, pts in (
                ("Java", 15),
                ("C#", 15),
                ("Python", 10),
                ("TypeScript", 15),
                ("Go", 15),
                ("Rust", 20),
                ("C++", 15),
            ):
                ctx.add_language_score(lang, pts, "High complexity maintainability")
            for fw, pts in (
                ("Spring Boot", 15),
                ("ASP.NET Core", 15),
                ("Angular", 15),
                ("NestJS", 15),
            ):
                ctx.add_framework_score(fw, pts, "Complex system framework")
            for sdlc, pts in (
                ("Spiral", 25),
                ("Iterative", 20),
                ("Scrum", 15),
                ("DevOps", 20),
                ("V-Model", 15),
                ("Incremental", 10),
                ("Feature-Driven Development (FDD)", 15),
            ):
                ctx.add_sdlc_score(sdlc, pts, "Complex project lifecycle")
        elif n.complexity == "medium":
            for lang, pts in (("PHP", 10), ("Python", 10), ("JavaScript", 10)):
                ctx.add_language_score(lang, pts, "Medium complexity fit")
            for fw, pts in (
                ("Laravel", 15),
                ("React", 10),
                ("Django", 10),
                ("FastAPI", 10),
                ("Vue", 10),
                ("Next.js", 10),
                ("Flutter", 10),
            ):
                ctx.add_framework_score(fw, pts, "Medium complexity framework")
            for sdlc, pts in (
                ("Agile", 20),
                ("Iterative", 10),
                ("Scrum", 10),
                ("Kanban", 10),
                ("Incremental", 10),
            ):
                ctx.add_sdlc_score(sdlc, pts, "Medium complexity planning")
        elif n.complexity == "low":
            for lang, pts in (("PHP", 15), ("JavaScript", 10), ("Python", 10)):
                ctx.add_language_score(lang, pts, "Low complexity rapid build")
            for fw, pts in (
                ("Laravel", 15),
                ("Flask", 10),
                ("Vue", 10),
                ("Ruby on Rails", 10),
            ):
                ctx.add_framework_score(fw, pts, "Simple project framework")
            for sdlc, pts in (
                ("Waterfall", 15),
                ("RAD", 20),
                ("Prototype Model", 15),
                ("Lean", 15),
            ):
                ctx.add_sdlc_score(sdlc, pts, "Simple scope delivery")
            if n.team_size <= 2:
                ctx.add_sdlc_score("Big Bang Model", 10, "Very small simple project")

        if n.scalability_needs == "high":
            for lang, pts in (("Java", 15), ("TypeScript", 15), ("Go", 25), ("Rust", 15)):
                ctx.add_language_score(lang, pts, "Scalability-oriented language")
            for fw, pts in (
                ("Spring Boot", 20),
                ("ASP.NET Core", 15),
                ("Next.js", 15),
                ("NestJS", 20),
                ("Angular", 10),
                ("FastAPI", 15),
            ):
                ctx.add_framework_score(fw, pts, "Scalable service framework")
            ctx.add_framework_score(
                "Flet",
                -25,
                "Large-scale systems favor mature web/backend frameworks over Flet",
            )
            for sdlc, pts in (
                ("Agile", 15),
                ("Spiral", 15),
                ("DevOps", 20),
                ("Kanban", 10),
                ("Incremental", 10),
            ):
                ctx.add_sdlc_score(sdlc, pts, "Scalable delivery operations")

        if n.maintenance_expectations == "low":
            for fw, pts in (
                ("Laravel", 15),
                ("Django", 10),
                ("Spring Boot", 10),
                ("ASP.NET Core", 10),
                ("Ruby on Rails", 10),
                ("FastAPI", 5),
                ("Vue", 5),
            ):
                ctx.add_framework_score(fw, pts, "Lower long-term maintenance burden")
            for sdlc, pts in (("Waterfall", 10), ("Lean", 10), ("Kanban", 10)):
                ctx.add_sdlc_score(sdlc, pts, "Low maintenance planning")

        if n.deployment_preference == "shared hosting":
            for lang, pts in (("PHP", 25), ("JavaScript", 10), ("SQL", 10)):
                ctx.add_language_score(lang, pts, "Shared hosting friendly stack")
            for fw, pts in (("Laravel", 20), ("Vue", 5), ("React", 5)):
                ctx.add_framework_score(fw, pts, "Shared hosting deployment")
            ctx.add_framework_score(
                "Flet",
                -30,
                "Shared hosting favors traditional web frameworks over Flet",
            )
            for sdlc, pts in (("Waterfall", 5), ("RAD", 10)):
                ctx.add_sdlc_score(sdlc, pts, "Hosting-constrained delivery")

        if n.deployment_preference == "cloud":
            for lang, pts in (
                ("Python", 15),
                ("TypeScript", 15),
                ("Go", 20),
                ("Rust", 10),
                ("Java", 10),
                ("C#", 10),
            ):
                ctx.add_language_score(lang, pts, "Cloud-native language fit")
            for fw, pts in (
                ("FastAPI", 15),
                ("Next.js", 15),
                ("Spring Boot", 15),
                ("NestJS", 15),
                ("Express.js", 10),
                ("ASP.NET Core", 15),
                ("Django", 10),
            ):
                ctx.add_framework_score(fw, pts, "Cloud deployment framework")
            devops_cloud_pts = 25
            if (
                n.security_requirements == "high"
                and n.requirements_stability == "stable"
            ):
                devops_cloud_pts = 10
            for sdlc, pts in (
                ("Agile", 15),
                ("DevOps", devops_cloud_pts),
                ("Scrum", 10),
                ("Kanban", 10),
            ):
                ctx.add_sdlc_score(sdlc, pts, "Cloud deployment lifecycle support")

        if db_heavy:
            for lang, pts in (
                ("SQL", 25),
                ("Python", 10),
                ("PHP", 10),
                ("C#", 10),
                ("Java", 10),
            ):
                ctx.add_language_score(lang, pts, "Database/reporting workload")
            for fw, pts in (
                ("Django", 10),
                ("Laravel", 10),
                ("ASP.NET Core", 10),
            ):
                ctx.add_framework_score(fw, pts, "Data-backed application framework")
            for sdlc, pts in (("Waterfall", 10), ("V-Model", 10), ("Iterative", 10)):
                ctx.add_sdlc_score(sdlc, pts, "Data-centric planning")

        if embedded:
            for lang, pts in (("C", 35), ("C++", 30), ("Rust", 25)):
                ctx.add_language_score(lang, pts, "Embedded/systems programming")
            for sdlc, pts in (
                ("Spiral", 20),
                ("V-Model", 20),
                ("Waterfall", 10),
                ("Iterative", 10),
            ):
                ctx.add_sdlc_score(sdlc, pts, "Systems engineering lifecycle")

        if xp_desktop:
            for lang, pts in (
                ("Rust", 20),
                ("TypeScript", 15),
                ("JavaScript", 10),
                ("C++", 15),
                ("C#", 15),
            ):
                ctx.add_language_score(lang, pts, "Cross-platform desktop shell")
            ctx.add_framework_score("Tauri", 35, "Lightweight secure desktop shell")
            ctx.add_framework_score("Flutter", 10, "Desktop UI option")
            ctx.add_framework_score("Flet", 20, "Python cross-platform desktop UI")
            for sdlc, pts in (("Iterative", 15), ("Agile", 10)):
                ctx.add_sdlc_score(sdlc, pts, "Desktop iterative delivery")

        if n.requirements_stability == "changing":
            for sdlc, pts in (
                ("Agile", 20),
                ("Iterative", 15),
                ("Scrum", 15),
                ("Kanban", 15),
                ("Prototype Model", 10),
                ("RAD", 10),
            ):
                ctx.add_sdlc_score(sdlc, pts, "Adaptive to changing requirements")
            ctx.add_sdlc_score("Waterfall", -10, "Less fit for changing scope")
            ctx.add_sdlc_score("V-Model", -5, "Less fit for volatile scope")
        elif n.requirements_stability == "stable":
            for sdlc, pts in (
                ("Waterfall", 20),
                ("V-Model", 20),
                ("Incremental", 10),
                ("Feature-Driven Development (FDD)", 10),
                ("Agile", 5),
            ):
                ctx.add_sdlc_score(sdlc, pts, "Stable requirements governance")

        if n.stakeholder_involvement == "high":
            for sdlc, pts in (
                ("Agile", 20),
                ("Scrum", 15),
                ("Prototype Model", 15),
                ("RAD", 10),
                ("Extreme Programming (XP)", 10),
            ):
                ctx.add_sdlc_score(sdlc, pts, "High stakeholder collaboration")
        elif n.stakeholder_involvement == "low":
            for sdlc, pts in (("Waterfall", 10), ("V-Model", 10), ("Kanban", 10)):
                ctx.add_sdlc_score(sdlc, pts, "Low stakeholder involvement fit")

        if web_admin and not ai:
            ctx.add_language_score("PHP", 15, "Beginner-friendly web admin portal")
            ctx.add_framework_score(
                "Laravel",
                20,
                "Laravel MVC, auth, migrations, and rapid CRUD for admin portals",
            )
            ctx.add_language_score("Python", 5, "Alternative web admin option")
            ctx.add_framework_score("Django", 5, "Alternative admin web framework")

        if "machine learning" in n.project_type_norm or n.project_type_norm.startswith("ai"):
            ctx.add_language_score("Python", 30, "AI/ML project type emphasis")
            ctx.add_framework_score("FastAPI", 25, "AI/ML API serving")
            ctx.add_framework_score("Django", 10, "AI/ML web tooling")
            ctx.add_sdlc_score("Iterative", 15, "AI experimentation cycles")

        if n.is_cross_platform_desktop and (
            "lightweight" in n.combined_text or "secure desktop" in n.combined_text
        ):
            ctx.add_language_score("Rust", 20, "Secure lightweight desktop host")
            ctx.add_language_score("TypeScript", 15, "Desktop shell with web UI")
            ctx.add_framework_score("Tauri", 25, "Cross-platform desktop shell priority")

        self._score_flet_context(ctx, n)
        self._apply_sdlc_context_rules(ctx, n, primary)

    def _score_flet_context(
        self, ctx: _ScoringContext, n: NormalizedRequest
    ) -> None:
        """Flet scoring basis: scored strongly for Python-based UI apps, dashboards,
        prototypes, internal tools, desktop-style apps, educational systems, and
        AI-assisted applications per official Flet documentation (web, desktop, and
        mobile apps in Python). Not scored as the default best option for large-scale
        enterprise web systems because its ecosystem and deployment patterns differ
        from mature web frameworks such as Laravel, Django, ASP.NET Core, and
        Spring Boot."""
        combined = n.combined_text
        primary = n.project_context.get("primary_context", "mixed")
        flet_signals = self._contains_any(
            combined,
            (
                "internal tool",
                "internal utility",
                "admin utility",
                "local tool",
                "educational",
                "student project",
                "capstone",
                "prototype",
                "mvp",
                "dashboard",
                "ai-assisted",
                "decision-support",
            ),
        )

        if not (
            n.is_desktop
            or flet_signals
            or n.is_ai
            or primary in ("desktop", "ai_ml")
            or (n.is_web and n.is_crud_admin and "dashboard" in combined)
        ):
            return

        if n.is_desktop or "desktop application" in n.project_type_norm:
            ctx.add_language_score("Python", 25, "Python desktop UI stack")
            ctx.add_framework_score(
                "Flet",
                40,
                "Python cross-platform desktop UI (official Flet capability)",
            )

        if self._contains_any(
            combined, ("internal tool", "internal utility", "admin utility", "local tool")
        ):
            ctx.add_language_score("Python", 20, "Python internal tooling fit")
            ctx.add_framework_score("Flet", 35, "Internal tool UI in Python")

        if "dashboard" in combined or "admin dashboard" in n.features_text:
            ctx.add_framework_score("Flet", 30, "Dashboard and reporting UI in Python")

        if n.is_ai or "chatbot" in combined:
            ctx.add_language_score("Python", 15, "Python AI-assisted tooling")
            ctx.add_framework_score(
                "Flet",
                25,
                "Python UI for AI-assisted tools and local AI integration",
            )

        if n.development_experience in ("beginner", "intermediate"):
            ctx.add_language_score("Python", 10, "Accessible Python UI stack")
            ctx.add_framework_score(
                "Flet",
                15,
                "Beginner-friendly Python UI development",
            )

        if n.timeline == "short" and n.complexity in ("low", "medium"):
            ctx.add_framework_score("Flet", 12, "Rapid Python UI prototyping")

        if n.deployment_preference == "local":
            ctx.add_framework_score(
                "Flet",
                15,
                "Local or desktop-style deployment fit",
            )

        flet_feature_markers = (
            "ai ml features",
            "chat messaging",
            "reports analytics",
            "admin dashboard",
            "offline-first mode",
            "api integrations",
        )
        if any(marker in n.features_text for marker in flet_feature_markers):
            ctx.add_framework_score(
                "Flet",
                18,
                "Selected features align with Python UI and local integration",
            )

        if n.is_web and n.is_crud_admin and primary != "mobile_first":
            ctx.add_framework_score(
                "Flet",
                10,
                "Moderate fit for web admin/reporting with Python UI",
            )

        if n.is_mobile and primary == "mobile_first":
            ctx.add_framework_score(
                "Flet",
                -25,
                "Mobile-first projects favor Flutter unless Python prototype is intended",
            )
            if "python" in combined or "prototype" in combined:
                ctx.add_framework_score("Flet", 10, "Python cross-platform prototype option")

        if primary == "backend_api" and not flet_signals:
            ctx.add_framework_score(
                "Flet",
                -35,
                "API-only backend projects do not need a Flet UI framework",
            )

        if n.deployment_preference == "shared hosting":
            ctx.add_framework_score(
                "Flet",
                -20,
                "Shared hosting deployment is a weak fit for Flet",
            )

        if (
            self._contains_any(
                combined,
                ("enterprise web", "ecommerce", "seo", "public web platform", "saas"),
            )
            and not flet_signals
        ):
            ctx.add_framework_score(
                "Flet",
                -20,
                "Large public web platforms favor mature web frameworks over Flet",
            )

    def _apply_sdlc_context_rules(
        self, ctx: _ScoringContext, n: NormalizedRequest, primary: str
    ) -> None:
        """Context-specific SDLC boosts so DevOps does not dominate enterprise systems."""
        if n.security_requirements == "high" and n.requirements_stability == "stable":
            for sdlc, pts in (
                ("V-Model", 25),
                ("Spiral", 20),
                ("Waterfall", 15),
                ("Incremental", 10),
                ("Scrum", 10),
            ):
                ctx.add_sdlc_score(
                    sdlc, pts, "High-security system with fixed requirements"
                )
            ctx.add_sdlc_score("DevOps", 5, "Operations support, not primary lifecycle")

        if n.security_requirements == "high" and n.complexity == "high":
            for sdlc, pts in (
                ("Spiral", 25),
                ("V-Model", 20),
                ("Scrum", 10),
            ):
                ctx.add_sdlc_score(sdlc, pts, "High-security complex system governance")
            devops_pts = 10 if n.deployment_preference == "cloud" else 5
            ctx.add_sdlc_score(
                "DevOps",
                devops_pts,
                "DevOps as delivery support for complex secure systems",
            )

        if n.deployment_preference == "cloud" and not (
            n.security_requirements == "high" and n.requirements_stability == "stable"
        ):
            ctx.add_sdlc_score("DevOps", 15, "Cloud deployment operations")
            ctx.add_sdlc_score("Kanban", 5, "Continuous flow for cloud delivery")

        if n.requirements_stability == "changing" and n.stakeholder_involvement == "high":
            for sdlc, pts in (
                ("Agile", 25),
                ("Scrum", 20),
                ("Iterative", 15),
                ("Kanban", 10),
            ):
                ctx.add_sdlc_score(sdlc, pts, "Changing requirements with active stakeholders")
            ctx.add_sdlc_score("Waterfall", -10, "Poor fit for changing stakeholder-driven scope")

        if primary == "mobile_first" and n.timeline == "short":
            for sdlc, pts in (
                ("Agile", 20),
                ("Prototype Model", 15),
                ("RAD", 10),
            ):
                ctx.add_sdlc_score(sdlc, pts, "Short-timeline mobile delivery")

        if (
            primary in ("web_crud", "web")
            and n.development_experience == "beginner"
            and n.timeline == "short"
        ):
            for sdlc, pts in (
                ("Agile", 20),
                ("RAD", 15),
                ("Incremental", 10),
            ):
                ctx.add_sdlc_score(sdlc, pts, "Beginner web CRUD rapid delivery")
            if n.requirements_stability == "stable":
                ctx.add_sdlc_score("Waterfall", 10, "Fixed-scope web delivery")

    # ------------------------------------------------------------------
    # Context-aware feature scoring (Phase 2.3)
    # ------------------------------------------------------------------

    def _score_crud_context(
        self, ctx: _ScoringContext, n: NormalizedRequest, primary: str
    ) -> None:
        if primary == "mobile_first":
            ctx.add_language_score("Dart", 25, "Mobile CRUD/data-entry screens")
            ctx.add_framework_score("Flutter", 30, "Mobile CRUD UI and local state")
            ctx.add_language_score("Kotlin", 8, "Native mobile CRUD alternative")
            ctx.add_language_score("Swift", 8, "Native mobile CRUD alternative")
            for fw, pts in (("Laravel", 3), ("Django", 3)):
                ctx.add_framework_score(
                    fw, pts, "Optional backend API only (not primary mobile UI)"
                )
            for sdlc, pts in (("Agile", 15), ("Prototype Model", 10)):
                ctx.add_sdlc_score(sdlc, pts, "Mobile iterative delivery")
            return
        if primary == "desktop":
            for lang, pts in (
                ("Rust", 15),
                ("TypeScript", 15),
                ("C#", 15),
                ("C++", 10),
            ):
                ctx.add_language_score(lang, pts, "Desktop CRUD application")
            for fw, pts in (("Tauri", 25), ("Flutter", 15), ("Flet", 20), ("ASP.NET Core", 15)):
                ctx.add_framework_score(fw, pts, "Desktop CRUD framework")
            return
        if primary == "backend_api":
            for fw, pts in (
                ("FastAPI", 15),
                ("Express.js", 12),
                ("NestJS", 12),
                ("Laravel", 10),
            ):
                ctx.add_framework_score(fw, pts, "API CRUD endpoints")
            return
        if primary == "embedded":
            return
        for lang, pts in (
            ("PHP", 25),
            ("Python", 15),
            ("JavaScript", 10),
            ("C#", 15),
            ("Java", 10),
            ("Ruby", 10),
            ("SQL", 15),
        ):
            ctx.add_language_score(lang, pts, "CRUD/admin system fit")
        for fw, pts in (
            ("Laravel", 30),
            ("Django", 25),
            ("ASP.NET Core", 20),
            ("Spring Boot", 15),
            ("Ruby on Rails", 20),
            ("React", 10),
            ("Vue", 10),
            ("Angular", 10),
            ("Next.js", 10),
        ):
            ctx.add_framework_score(fw, pts, "Admin/CRUD web framework")
        for sdlc, pts in (("Waterfall", 10), ("Agile", 15), ("Iterative", 10)):
            ctx.add_sdlc_score(sdlc, pts, "Structured admin delivery")

    def _score_auth_context(
        self, ctx: _ScoringContext, n: NormalizedRequest, primary: str
    ) -> None:
        if primary == "mobile_first":
            ctx.add_language_score("Dart", 15, "Mobile authentication flows")
            ctx.add_framework_score("Flutter", 20, "Mobile auth UI and secure storage")
            for fw, pts in (("FastAPI", 5), ("NestJS", 5), ("Laravel", 3)):
                ctx.add_framework_score(fw, pts, "Optional auth backend API")
            return
        if primary in ("backend_api", "ai_ml"):
            for fw, pts in (
                ("FastAPI", 15),
                ("NestJS", 15),
                ("Express.js", 12),
                ("Spring Boot", 12),
                ("Laravel", 10),
                ("Django", 10),
            ):
                ctx.add_framework_score(fw, pts, "API authentication services")
            return
        if primary == "embedded":
            return
        for lang, pts in (("PHP", 15), ("Java", 10), ("C#", 10), ("TypeScript", 10)):
            ctx.add_language_score(lang, pts, "Authentication-heavy stack")
        for fw, pts in (
            ("Laravel", 20),
            ("Spring Boot", 10),
            ("ASP.NET Core", 10),
            ("Django", 15),
            ("FastAPI", 10),
            ("Next.js", 10),
            ("NestJS", 15),
            ("Express.js", 10),
            ("Ruby on Rails", 10),
        ):
            ctx.add_framework_score(fw, pts, "Auth-ready framework")
        for sdlc, pts in (("Agile", 10), ("Waterfall", 10)):
            ctx.add_sdlc_score(sdlc, pts, "Security validation planning")
        if n.security_requirements == "high":
            ctx.add_sdlc_score("V-Model", 10, "Validation-focused security")

    def _score_reporting_context(
        self, ctx: _ScoringContext, n: NormalizedRequest, primary: str
    ) -> None:
        if primary == "mobile_first":
            ctx.add_framework_score("Flutter", 10, "Mobile charts and basic analytics UI")
            return
        if primary == "ai_ml":
            return
        for lang, pts in (("SQL", 20), ("PHP", 10), ("Python", 10), ("C#", 10), ("Java", 10)):
            ctx.add_language_score(lang, pts, "Reporting and records workload")
        for fw, pts in (
            ("Laravel", 12),
            ("Django", 12),
            ("ASP.NET Core", 10),
            ("Ruby on Rails", 10),
        ):
            ctx.add_framework_score(fw, pts, "Admin/reporting web framework")
        for sdlc, pts in (("Iterative", 10), ("Agile", 10), ("Waterfall", 5)):
            ctx.add_sdlc_score(sdlc, pts, "Reporting system delivery")

    def _score_mobile_feature_signals(
        self, ctx: _ScoringContext, n: NormalizedRequest, primary: str
    ) -> None:
        if primary not in ("mobile_first", "mixed"):
            return
        ctx.add_language_score("Dart", 20, "Maps/notifications mobile client")
        ctx.add_framework_score("Flutter", 25, "Mobile maps, location, and push notifications")
        if "maps location" in n.features_text:
            ctx.add_language_score("Kotlin", 10, "Native maps alternative")
            ctx.add_language_score("Swift", 10, "Native maps alternative")

    def _score_low_budget(self, ctx: _ScoringContext, primary: str) -> None:
        if primary == "mobile_first":
            ctx.add_language_score("Dart", 10, "Low-budget cross-platform mobile")
            ctx.add_framework_score("Flutter", 15, "Cost-effective mobile delivery")
            return
        if primary in ("embedded", "desktop"):
            return
        for lang, pts in (("PHP", 15), ("Python", 15), ("JavaScript", 15)):
            ctx.add_language_score(lang, pts, "Low-budget open-source fit")
        for fw, pts in (
            ("Laravel", 15),
            ("FastAPI", 10),
            ("React", 10),
            ("Flask", 10),
            ("Django", 10),
            ("Vue", 10),
            ("Express.js", 10),
            ("Flutter", 5),
            ("Ruby on Rails", 5),
        ):
            ctx.add_framework_score(fw, pts, "Cost-effective framework")

    def _score_short_timeline(self, ctx: _ScoringContext, primary: str) -> None:
        if primary == "mobile_first":
            for fw, pts in (("Flutter", 20),):
                ctx.add_framework_score(fw, pts, "Rapid mobile MVP")
            for sdlc, pts in (
                ("RAD", 25),
                ("Agile", 20),
                ("Prototype Model", 15),
                ("Lean", 15),
                ("Kanban", 15),
            ):
                ctx.add_sdlc_score(sdlc, pts, "Short timeline mobile delivery")
            return
        if primary == "backend_api":
            for fw, pts in (("FastAPI", 15), ("Express.js", 12), ("Flask", 12)):
                ctx.add_framework_score(fw, pts, "Rapid API delivery")
        elif primary not in ("embedded",):
            for fw, pts in (
                ("Laravel", 15),
                ("FastAPI", 10),
                ("Flutter", 5),
                ("Django", 15),
                ("Flask", 15),
                ("React", 10),
                ("Vue", 10),
                ("Express.js", 10),
                ("Ruby on Rails", 15),
            ):
                ctx.add_framework_score(fw, pts, "Rapid MVP framework")
        for sdlc, pts in (
            ("RAD", 25),
            ("Agile", 20),
            ("Prototype Model", 15),
            ("Lean", 15),
            ("Kanban", 15),
        ):
            ctx.add_sdlc_score(sdlc, pts, "Short timeline delivery")

    def _platform_fit_bonus(
        self, lang: str, fw: str, norm: NormalizedRequest
    ) -> int:
        primary = norm.project_context.get("primary_context", "mixed")
        pair = (lang, fw)
        if primary == "mobile_first":
            if pair == ("Dart", "Flutter"):
                return 80
            if lang in ("Kotlin", "Swift") and fw == NO_FRAMEWORK_LABEL:
                return 50
            if fw in WEB_ONLY_FRAMEWORKS:
                return -60
            if fw in ("Spring Boot", "ASP.NET Core"):
                return -30
            if fw in FRONTEND_ONLY_FRAMEWORKS:
                return -30
        elif primary == "web_crud":
            bonuses = {
                ("PHP", "Laravel"): 50,
                ("Python", "Django"): 45,
                ("Ruby", "Ruby on Rails"): 35,
                ("TypeScript", "Next.js"): 40,
            }
            if pair in bonuses:
                return bonuses[pair]
            if fw in ("React", "Vue", "Angular"):
                return 25
            if pair == ("Dart", "Flutter"):
                return -35
            if fw in ("Tauri", "Flet"):
                return -40
        elif primary == "backend_api":
            bonuses = {
                ("Python", "FastAPI"): 50,
                ("JavaScript", "Express.js"): 45,
                ("TypeScript", "NestJS"): 45,
                ("Java", "Spring Boot"): 45,
                ("C#", "ASP.NET Core"): 45,
                ("PHP", "Laravel"): 30,
            }
            if pair in bonuses:
                return bonuses[pair]
            if fw in FRONTEND_ONLY_FRAMEWORKS:
                return -40
        elif primary == "desktop":
            if pair == ("Python", "Flet"):
                bonus = 50
                if norm.development_experience in ("beginner", "intermediate"):
                    bonus += 15
                if self._contains_any(
                    norm.combined_text,
                    ("dashboard", "internal tool", "ai", "chatbot", "reports"),
                ):
                    bonus += 15
                if (
                    "lightweight" in norm.combined_text
                    and "secure" in norm.combined_text
                    and norm.development_experience == "advanced"
                ):
                    bonus -= 15
                return bonus
            if pair == ("Rust", "Tauri"):
                return 70
            if pair == ("TypeScript", "Tauri"):
                return 65
            if pair == ("Dart", "Flutter"):
                return 25
            if fw in ("Laravel", "Django", "Ruby on Rails"):
                return -45
        elif primary == "embedded":
            if lang in ("C", "C++", "Rust"):
                return 70
            if fw in WEB_ONLY_FRAMEWORKS or fw in FRONTEND_ONLY_FRAMEWORKS:
                return -70
        elif primary == "ai_ml":
            if lang == "Python" and fw in ("FastAPI", "Django", "Flask"):
                return 40
            if pair == ("Python", "Flet") and (
                norm.is_crud_admin or "dashboard" in norm.combined_text or norm.is_ai
            ):
                return 35
            if fw == "Laravel" and "crud" in norm.features_text:
                return -25
        elif primary == "database_centered":
            if lang == "SQL":
                return 50
        return 0

    def _context_fit_bonus(
        self, lang: str, fw: str, norm: NormalizedRequest
    ) -> int:
        primary = norm.project_context.get("primary_context", "mixed")
        bonus = 0
        if primary == "web_crud" and norm.is_web_admin_portal:
            if (lang, fw) == ("PHP", "Laravel"):
                bonus += 15
        if primary == "mobile_first" and norm.is_realtime:
            if fw == "Flutter":
                bonus += 10
        return bonus

    def _mismatch_penalty(
        self, lang: str, fw: str, norm: NormalizedRequest
    ) -> int:
        primary = norm.project_context.get("primary_context", "mixed")
        penalty = 0
        if primary == "mobile_first":
            if fw in WEB_ONLY_FRAMEWORKS:
                penalty += 80
            if lang == "PHP":
                penalty += 40
        elif primary == "web_crud":
            if fw == "Tauri" or fw == "Flet" or (lang == "Dart" and fw == "Flutter"):
                penalty += 50
        elif primary == "backend_api":
            if fw in FRONTEND_ONLY_FRAMEWORKS:
                penalty += 60
        elif primary == "embedded":
            if fw in WEB_ONLY_FRAMEWORKS | FRONTEND_ONLY_FRAMEWORKS | {"Flutter"}:
                penalty += 80
        elif primary == "desktop":
            if fw in ("Laravel", "Django", "Ruby on Rails"):
                penalty += 45
        if lang == "SQL" and fw not in (SQL_FRAMEWORK_LABEL, NO_FRAMEWORK_LABEL):
            if not norm.is_database_centered:
                penalty += 50
        if fw in ("Laravel", "Django", "Ruby on Rails") and lang == "SQL":
            penalty += 60
        return penalty

    def _compute_final_stack_score(
        self,
        lang: str,
        fw: str,
        sdlc: str,
        ctx: _ScoringContext,
        norm: NormalizedRequest,
    ) -> int:
        base = (
            ctx.language_scores.get(lang, 0)
            + ctx.framework_scores.get(fw, 0)
            + ctx.sdlc_scores.get(sdlc, 0)
        )
        return (
            base
            + self._platform_fit_bonus(lang, fw, norm)
            + self._context_fit_bonus(lang, fw, norm)
            - self._mismatch_penalty(lang, fw, norm)
        )

    @staticmethod
    def _is_mixed_context(norm: NormalizedRequest) -> bool:
        flags = norm.project_context
        active = sum(
            1
            for k in ("is_mobile", "is_web", "is_desktop", "is_backend_api")
            if flags.get(k)
        )
        return active >= 2

    def _get_contextual_stack_candidates(
        self, norm: NormalizedRequest
    ) -> tuple[tuple[str, str, str], ...]:
        pools: dict[str, tuple[tuple[str, str, str], ...]] = {
            "mobile_first": MOBILE_STACK_CANDIDATES,
            "web_crud": WEB_CRUD_STACK_CANDIDATES,
            "web": WEB_CRUD_STACK_CANDIDATES,
            "backend_api": BACKEND_API_STACK_CANDIDATES,
            "desktop": DESKTOP_STACK_CANDIDATES,
            "embedded": EMBEDDED_STACK_CANDIDATES,
            "ai_ml": AI_ML_STACK_CANDIDATES,
            "database_centered": WEB_CRUD_STACK_CANDIDATES,
        }
        primary = norm.project_context.get("primary_context", "mixed")
        contextual = pools.get(primary, BASE_STACK_CANDIDATES)
        merged = list(contextual)
        for item in BASE_STACK_CANDIDATES:
            if item not in merged:
                merged.append(item)
        return tuple(merged)

    def _apply_category_winner(
        self,
        best: dict[str, Any],
        stacks: list[dict[str, Any]],
        norm: NormalizedRequest,
    ) -> tuple[dict[str, Any], str | None]:
        primary = norm.project_context.get("primary_context", "mixed")
        lang, fw = best["language"], best["framework"]

        def pick_family(predicate) -> dict[str, Any] | None:
            for stack in stacks:
                if predicate(stack["language"], stack["framework"]):
                    return dict(stack)
            return None

        reject_reason: str | None = None
        if primary == "mobile_first":
            if fw in WEB_ONLY_FRAMEWORKS or lang == "PHP":
                reject_reason = "mobile_first: web stack cannot be primary"
                replacement = pick_family(
                    lambda l, f: f == "Flutter" or l in ("Kotlin", "Swift")
                )
                if replacement:
                    return replacement, reject_reason
        elif primary == "web_crud":
            if fw in ("Tauri", "Flet") or (lang == "Dart" and fw == "Flutter"):
                reject_reason = "web_crud: mobile/desktop stack not primary"
                replacement = pick_family(
                    lambda l, f: f
                    in ("Laravel", "Django", "Ruby on Rails", "ASP.NET Core", "Next.js")
                )
                if replacement:
                    return replacement, reject_reason
        elif primary == "backend_api":
            if fw in FRONTEND_ONLY_FRAMEWORKS:
                reject_reason = "backend_api: frontend framework cannot be primary"
                replacement = pick_family(
                    lambda l, f: f
                    in (
                        "FastAPI",
                        "Express.js",
                        "NestJS",
                        "Spring Boot",
                        "ASP.NET Core",
                        "Laravel",
                    )
                )
                if replacement:
                    return replacement, reject_reason
        elif primary == "embedded":
            if lang not in ("C", "C++", "Rust") or fw in WEB_ONLY_FRAMEWORKS:
                reject_reason = "embedded: systems language required"
                replacement = pick_family(lambda l, f: l in ("C", "C++", "Rust"))
                if replacement:
                    return replacement, reject_reason
        elif primary == "desktop":
            if fw in ("Laravel", "Django", "Ruby on Rails"):
                reject_reason = "desktop: web MVC stack not primary"
                replacement = pick_family(
                    lambda l, f: f in ("Tauri", "Flutter", "Flet")
                    or l in ("Rust", "TypeScript", "C#", "Python")
                )
                if replacement:
                    return replacement, reject_reason
        elif primary == "ai_ml":
            if fw == "Laravel" and lang == "PHP":
                reject_reason = "ai_ml: web CRUD stack not primary for AI project"
                replacement = pick_family(
                    lambda l, f: l == "Python"
                    and f in ("FastAPI", "Django", "Flask")
                )
                if replacement:
                    return replacement, reject_reason
        return best, reject_reason

    # ------------------------------------------------------------------
    # Stack ranking & compatibility
    # ------------------------------------------------------------------

    def _rank_stack_candidates(
        self,
        ctx: _ScoringContext,
        norm: NormalizedRequest,
        include_all: bool = False,
    ) -> list[dict[str, Any]]:
        stacks: dict[tuple[str, str, str], int] = {}
        candidates = list(self._get_contextual_stack_candidates(norm))
        top_langs = self._top_names(ctx.language_scores, 6)
        top_fws = self._top_names(ctx.framework_scores, 8)
        top_sdlcs = self._top_names(ctx.sdlc_scores, 6)
        for lang in top_langs:
            for fw in top_fws:
                aligned_lang = self._align_language_for_framework(fw, ctx, norm)
                if aligned_lang != lang and lang not in FRAMEWORK_LANGUAGES.get(fw, ()):
                    continue
                for sdlc in top_sdlcs:
                    triple = (aligned_lang, fw, sdlc)
                    if not self.is_compatible_stack(aligned_lang, fw):
                        continue
                    score = self._compute_final_stack_score(
                        aligned_lang, fw, sdlc, ctx, norm
                    )
                    stacks[triple] = max(stacks.get(triple, 0), score)

        for lang, fw, sdlc in candidates:
            if not self.is_compatible_stack(lang, fw):
                continue
            aligned = self._align_language_for_framework(fw, ctx, norm)
            score = self._compute_final_stack_score(aligned, fw, sdlc, ctx, norm)
            stacks[(aligned, fw, sdlc)] = max(stacks.get((aligned, fw, sdlc), 0), score)

        ranked = [
            {
                "language": lang,
                "framework": fw,
                "sdlc": sdlc,
                "stack_score": score,
            }
            for (lang, fw, sdlc), score in stacks.items()
            if score > 0 or include_all
        ]
        ranked.sort(key=lambda s: s["stack_score"], reverse=True)

        if norm.deployment_preference == "shared hosting":
            ranked.sort(
                key=lambda s: (
                    s["stack_score"]
                    + (15 if s["language"] == "PHP" and s["framework"] == "Laravel" else 0)
                    - (
                        20
                        if s["framework"] in ("Spring Boot", "NestJS", "Tauri")
                        else 0
                    )
                ),
                reverse=True,
            )

        return ranked

    def is_compatible_stack(self, language: str, framework: str) -> bool:
        if framework == NO_FRAMEWORK_LABEL:
            return language in FRAMEWORKLESS_LANGUAGES
        if framework == SQL_FRAMEWORK_LABEL:
            return language == "SQL"
        allowed = FRAMEWORK_LANGUAGES.get(framework)
        if not allowed:
            return False
        return language in allowed

    def _align_language_for_framework(
        self, framework: str, ctx: _ScoringContext, norm: NormalizedRequest
    ) -> str:
        allowed = FRAMEWORK_LANGUAGES.get(framework, ())
        if not allowed:
            return max(ctx.language_scores, key=ctx.language_scores.get)
        if len(allowed) == 1:
            return allowed[0]
        if framework == "Tauri":
            if norm.performance_requirements == "high" or norm.security_requirements == "high":
                return "Rust"
            ts = ctx.language_scores.get("TypeScript", 0)
            js = ctx.language_scores.get("JavaScript", 0)
            if ts >= js:
                return "TypeScript"
            return "JavaScript"
        if "TypeScript" in allowed and "JavaScript" in allowed:
            ts = ctx.language_scores.get("TypeScript", 0)
            js = ctx.language_scores.get("JavaScript", 0)
            return "TypeScript" if ts >= js else "JavaScript"
        return allowed[0]

    def _default_framework_for_language(
        self, language: str, ctx: _ScoringContext, norm: NormalizedRequest
    ) -> str:
        if language == "SQL" and norm.is_database_centered:
            return SQL_FRAMEWORK_LABEL
        options = LANGUAGE_FRAMEWORKS.get(language, ())
        if not options:
            if language in FRAMEWORKLESS_LANGUAGES:
                return NO_FRAMEWORK_LABEL
            return NO_FRAMEWORK_LABEL
        return max(options, key=lambda f: ctx.framework_scores.get(f, 0))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    _FEATURE_ALIASES: dict[str, str] = {
        "crud operations": "crud",
        "admin dashboard": "admin dashboard",
        "reports / analytics": "reports analytics",
        "reports/analytics": "reports analytics",
        "authentication": "authentication",
        "role-based access": "role-based access",
        "ai / ml features": "ai ml features",
        "chat / messaging": "chat messaging",
        "real-time updates": "realtime updates",
        "api / integrations": "api integrations",
        "maps / location": "maps location",
        "notifications": "notifications",
    }

    _AI_ML_TYPE_MARKERS: tuple[str, ...] = (
        "ai / machine learning",
        "machine learning project",
        "ai machine learning",
    )

    _AI_ML_GOAL_MARKERS: tuple[str, ...] = (
        "machine learning",
        "deep learning",
        "neural network",
        "chatbot",
        "prediction model",
        "ml model",
        "data science",
        "computer vision",
        "natural language processing",
        "tensorflow",
        "pytorch",
        "recommendation engine",
        "recommendation system",
        "artificial intelligence",
    )

    @classmethod
    def _normalize_feature_token(cls, feature: str) -> str:
        raw = cls._norm_token(feature)
        return cls._FEATURE_ALIASES.get(raw, raw)

    @classmethod
    def _is_ai_ml_project(
        cls,
        project_type_norm: str,
        features: list[str],
        goal_text: str,
        combined: str,
    ) -> bool:
        if any(marker in project_type_norm for marker in cls._AI_ML_TYPE_MARKERS):
            return True
        if any(f in ("ai ml features", "ai/ml features") for f in features):
            return True
        if any(marker in goal_text for marker in cls._AI_ML_GOAL_MARKERS):
            return True
        if "ai " in combined and "ml" in combined:
            return True
        return False

    @staticmethod
    def _is_reporting_analytics_profile(
        features: list[str],
        goal_text: str,
        combined: str,
        is_ai: bool,
    ) -> bool:
        if is_ai:
            return False
        if any("reports analytics" in f or f == "reports" for f in features):
            return True
        if "basic analytics" in goal_text:
            return True
        if "reports" in goal_text and "analytics" in goal_text:
            return True
        if "reporting" in combined and "dashboard" in combined:
            return True
        return False

    @staticmethod
    def _is_web_admin_portal(
        is_web: bool,
        is_crud: bool,
        is_auth: bool,
        is_ai: bool,
        project_type_norm: str,
    ) -> bool:
        if is_ai:
            return False
        if not (is_web and is_crud and is_auth):
            return False
        return any(
            token in project_type_norm
            for token in ("web application", "information system", "e-commerce")
        )

    @staticmethod
    def _preferred_sdlc_mismatch_summary(
        lang: str,
        fw: str,
        preferred_sdlc: str,
        selected_sdlc: str,
        norm: NormalizedRequest,
    ) -> str:
        base = (
            f"Your preferred language and framework ({lang} + {fw}) align with the "
            f"recommendation. {preferred_sdlc} was not selected — {selected_sdlc} fits "
            f"this project profile better."
        )
        if preferred_sdlc == "Waterfall" and norm.requirements_stability == "changing":
            return (
                f"{base} Waterfall is less suitable when requirements are changing and "
                f"stakeholder involvement is {norm.stakeholder_involvement}, where iterative "
                f"feedback (e.g. {selected_sdlc}) reduces rework risk."
            )
        if preferred_sdlc == "Waterfall":
            return (
                f"{base} Waterfall works best when requirements are fixed/stable and "
                f"documentation-heavy governance is required."
            )
        return base

    @staticmethod
    def _scoring_debug_enabled() -> bool:
        return DEBUG_RECOMMENDATION or os.environ.get(
            "STACKWISE_DEBUG_SCORING", ""
        ).strip() in ("1", "true", "yes")

    def _log_scoring_debug(
        self, norm: NormalizedRequest, ctx: _ScoringContext
    ) -> None:
        stacks = self._rank_stack_candidates(ctx, norm, include_all=True)[:10]
        log.info(
            "Recommendation scoring debug — timeline=%s budget=%s platform=%s",
            norm.timeline,
            norm.budget_constraints,
            norm.preferred_platform,
        )
        log.info("project_context: %s", norm.project_context)
        log.info(
            "top language scores: %s",
            sorted(ctx.language_scores.items(), key=lambda x: x[1], reverse=True)[:8],
        )
        log.info(
            "top framework scores: %s",
            sorted(ctx.framework_scores.items(), key=lambda x: x[1], reverse=True)[:8],
        )
        log.info(
            "top sdlc scores: %s",
            sorted(ctx.sdlc_scores.items(), key=lambda x: x[1], reverse=True)[:8],
        )
        log.info("top stack candidates: %s", stacks)

    @staticmethod
    def _norm_platform(value: str) -> str:
        v = " ".join(str(value or "").lower().strip().split())
        mapping = {
            "web application": "web",
            "mobile application": "mobile",
            "desktop application": "desktop",
            "backend/api": "backend api",
        }
        for key, token in mapping.items():
            if key in v:
                return token
        if v in ("web", "mobile", "desktop"):
            return v
        return v

    @staticmethod
    def _norm_token(value: str) -> str:
        return " ".join(str(value or "").lower().strip().split())

    @staticmethod
    def _contains_any(text: str, tokens: tuple[str, ...]) -> bool:
        return any(token in text for token in tokens)

    @staticmethod
    def _norm_timeline(value: str) -> str:
        v = value.lower().strip()
        if (
            "short" in v
            or "less than" in v
            or "1–2" in v
            or "1-2" in v
            or "1-3" in v
            or v in ("<1 month",)
        ):
            return "short"
        if "long" in v or "more than" in v or "5–6" in v or "5-6" in v or "6 month" in v or "6+" in v:
            return "long"
        if "3–4" in v or "3-4" in v or "medium" in v:
            return "medium"
        return "medium"

    @staticmethod
    def _norm_budget(value: str) -> str:
        v = value.lower().strip()
        if "very limited" in v or "limited" in v or v == "low" or "low budget" in v:
            return "low"
        if "not a concern" in v:
            return "high"
        if "flexible" in v:
            return "medium"
        if "high" in v:
            return "high"
        return "medium"

    @staticmethod
    def _norm_complexity(value: str) -> str:
        v = value.lower()
        if "very high" in v or v == "high":
            return "high"
        if "low" in v:
            return "low"
        return "medium"

    @staticmethod
    def _norm_stability(value: str) -> str:
        v = value.lower()
        if any(x in v for x in ("changing", "frequently", "somewhat", "experimental", "unknown")):
            return "changing"
        if any(x in v for x in ("stable", "fixed", "very stable", "mostly stable")):
            return "stable"
        return "changing" if "change" in v else "stable"

    @staticmethod
    def _norm_stakeholder(value: str) -> str:
        v = value.lower()
        if "high" in v or "frequent" in v:
            return "high"
        if "low" in v:
            return "low"
        return "medium"

    @staticmethod
    def _norm_experience(value: str) -> str:
        v = value.lower()
        if "beginner" in v:
            return "beginner"
        if "advanced" in v:
            return "advanced"
        return "intermediate"

    @staticmethod
    def _norm_level(value: str, high_tokens: tuple[str, ...]) -> str:
        v = value.lower().strip()
        if any(t in v for t in high_tokens):
            return "high"
        if "moderate" in v or "medium" in v:
            return "medium"
        if "low" in v or "small" in v or "basic" in v:
            return "low"
        return "medium"

    @staticmethod
    def _norm_maintenance(value: str) -> str:
        v = value.lower().strip()
        if any(x in v for x in ("short-term", "prototype only", "low maintenance")):
            return "low"
        if "long-term" in v or "production-ready" in v:
            return "high"
        if "medium" in v:
            return "medium"
        return "medium"

    @staticmethod
    def _norm_deployment(value: str) -> str:
        v = value.lower()
        if "shared hosting" in v:
            return "shared hosting"
        if "cloud" in v or "docker" in v or "container" in v:
            return "cloud"
        return "cloud" if "cloud" in v else "local"

    @staticmethod
    def _top_names(scores: dict[str, int], limit: int) -> list[str]:
        return [
            name
            for name, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        ]

    @staticmethod
    def _top_reason(reasons: list[str]) -> str:
        return reasons[-1] if reasons else ""

    @staticmethod
    def _confidence_label(score: int) -> str:
        if score >= 85:
            return "Very High"
        if score >= 75:
            return "High"
        if score >= 60:
            return "Moderate"
        return "Low"

    def _stack_to_alternative(
        self, stack: dict[str, Any], norm: NormalizedRequest, source: str
    ) -> dict[str, Any]:
        limitation = (
            "May need additional security, performance, or operational tuning depending on "
            "final non-functional requirements."
        )
        if (
            norm.deployment_preference == "cloud"
            and not self._is_devops_primary_project(norm)
        ):
            limitation = (
                f"{limitation} DevOps practices are recommended for CI/CD, cloud "
                "deployment, monitoring, and production maintenance."
            )
        raw_score = int(stack.get("stack_score", 0))
        entry: dict[str, Any] = {
            "language": stack["language"],
            "framework": stack["framework"],
            "sdlc": stack["sdlc"],
            "_raw_stack_score": raw_score,
            "fit_score": raw_score,
            "fit_percent": stack.get("fit_percent"),
            "fit_display": stack.get("fit_display"),
            "best_for": (
                f"Teams building {norm.project_type} with {norm.preferred_platform} "
                f"constraints and {norm.development_experience} experience."
            ),
            "limitation": limitation,
            "source": source,
        }
        return entry

    _DEVOPS_PRIMARY_MARKERS: tuple[str, ...] = (
        "ci/cd",
        "ci cd",
        "cicd",
        "deployment automation",
        "infrastructure as code",
        "monitoring platform",
        "cloud operations",
        "devops pipeline",
        "site reliability",
        "sre ",
        "platform engineering",
    )

    def _is_devops_primary_project(self, norm: NormalizedRequest) -> bool:
        combined = f"{norm.combined_text} {norm.goal_text} {norm.project_type_norm}"
        if any(marker in combined for marker in self._DEVOPS_PRIMARY_MARKERS):
            return True
        return "devops" in norm.project_type_norm and "application" not in combined

    def _sdlc_pool_for_alternatives(
        self, lang: str, fw: str, norm: NormalizedRequest
    ) -> tuple[str, ...]:
        primary = norm.project_context.get("primary_context", "mixed")
        if self._is_devops_primary_project(norm):
            return (
                "DevOps",
                "Agile",
                "Kanban",
                "Iterative",
                "Scrum",
            )
        if primary == "backend_api":
            return (
                "Scrum",
                "Spiral",
                "Iterative",
                "Incremental",
                "Agile",
                "Kanban",
            )
        if primary == "mobile_first":
            return ("Agile", "Prototype Model", "RAD", "Iterative")
        if primary in ("web_crud", "web"):
            return ("Agile", "RAD", "Iterative", "Scrum", "Incremental")
        if primary == "desktop":
            return ("Iterative", "Agile", "Spiral", "Prototype Model")
        if primary == "embedded":
            return ("V-Model", "Spiral", "Iterative", "Waterfall")
        if primary == "ai_ml":
            return ("Iterative", "Agile", "Spiral", "Prototype Model")
        if norm.security_requirements == "high" and norm.requirements_stability == "stable":
            return ("V-Model", "Spiral", "Waterfall", "Scrum", "Incremental")
        return ("Agile", "Scrum", "Iterative", "Spiral", "Incremental")

    def _best_sdlc_for_alternative_pair(
        self,
        lang: str,
        fw: str,
        norm: NormalizedRequest,
        ctx: _ScoringContext,
        avoid: frozenset[str] | None = None,
    ) -> str:
        avoid = avoid or frozenset()
        pool = self._sdlc_pool_for_alternatives(lang, fw, norm)
        candidates = [
            s
            for s in pool
            if s not in avoid
            and (s != "DevOps" or self._is_devops_primary_project(norm))
        ]
        if not candidates:
            candidates = [
                s
                for s in SDLC_MODELS
                if s not in avoid and s != "DevOps"
            ]
        return max(candidates, key=lambda s: ctx.sdlc_scores.get(s, 0))

    def _resolve_alternative_stack_row(
        self,
        lang: str,
        fw: str,
        sdlc: str,
        ctx: _ScoringContext,
        norm: NormalizedRequest,
    ) -> dict[str, Any]:
        if sdlc == "DevOps" and not self._is_devops_primary_project(norm):
            sdlc = self._best_sdlc_for_alternative_pair(lang, fw, norm, ctx)
        score = self._compute_final_stack_score(lang, fw, sdlc, ctx, norm)
        return {
            "language": lang,
            "framework": fw,
            "sdlc": sdlc,
            "stack_score": score,
        }

    def _resolve_alternative_stack_candidates(
        self,
        ctx: _ScoringContext,
        norm: NormalizedRequest,
        best: dict[str, Any],
        ranked: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        primary = norm.project_context.get("primary_context", "mixed")
        by_triple: dict[tuple[str, str, str], dict[str, Any]] = {}

        def consider(lang: str, fw: str, sdlc: str) -> None:
            if not self.is_compatible_stack(lang, fw):
                return
            row = self._resolve_alternative_stack_row(lang, fw, sdlc, ctx, norm)
            key = (lang, fw, row["sdlc"])
            if key not in by_triple or row["stack_score"] > by_triple[key]["stack_score"]:
                by_triple[key] = row

        if primary == "backend_api":
            for lang, fw, sdlc in (
                ("TypeScript", "NestJS", "Scrum"),
                ("C#", "ASP.NET Core", "Spiral"),
                ("Java", "Spring Boot", "Spiral"),
                ("TypeScript", "NestJS", "Iterative"),
            ):
                consider(lang, fw, sdlc)

        for stack in ranked:
            consider(
                stack["language"],
                stack["framework"],
                stack["sdlc"],
            )

        ordered = sorted(by_triple.values(), key=lambda s: s["stack_score"], reverse=True)
        if primary == "backend_api":
            return self._prioritize_backend_api_alternatives(ordered, by_triple)
        return ordered

    @staticmethod
    def _prioritize_backend_api_alternatives(
        ordered: list[dict[str, Any]],
        by_triple: dict[tuple[str, str, str], dict[str, Any]],
    ) -> list[dict[str, Any]]:
        preset_keys = (
            ("TypeScript", "NestJS", "Scrum"),
            ("C#", "ASP.NET Core", "Spiral"),
            ("Java", "Spring Boot", "Spiral"),
            ("TypeScript", "NestJS", "Iterative"),
        )
        result: list[dict[str, Any]] = []
        seen: set[tuple[str, str, str]] = set()
        for key in preset_keys:
            row = by_triple.get(key)
            if row and key not in seen:
                result.append(row)
                seen.add(key)
        for row in ordered:
            key = (row["language"], row["framework"], row["sdlc"])
            if key not in seen:
                result.append(row)
                seen.add(key)
        return result

    @staticmethod
    def _alternative_fit_display(percent: int) -> str:
        if percent >= 88:
            return "Strong fit"
        return f"{percent}% Fit"

    def _normalize_alternative_fit_percents(
        self, alts: list[dict[str, Any]], winner_stack_score: int
    ) -> None:
        if not alts:
            return
        raw_scores = [int(a.get("_raw_stack_score", 0)) for a in alts]

        max_raw = max(raw_scores)
        min_raw = min(raw_scores)
        ref = max(winner_stack_score, max_raw, 1)
        span = max(max_raw - min_raw, 1)

        for alt, raw in zip(alts, raw_scores):
            win_ratio = raw / ref
            rel = (raw - min_raw) / span
            pct = 60 + round(min(35, rel * 18 + win_ratio * 17))
            pct = max(60, min(95, pct))
            alt["fit_percent"] = pct
            alt["fit_display"] = self._alternative_fit_display(pct)
            alt["fit_score"] = pct

    def _legacy_component_alternatives(
        self,
        scores: dict[str, int],
        winner: str,
        reasons: dict[str, list[str]],
    ) -> list[dict[str, Any]]:
        ranked = sorted(
            ((n, s) for n, s in scores.items() if n != winner),
            key=lambda x: x[1],
            reverse=True,
        )[:3]
        alts = []
        for name, score in ranked:
            reason_list = reasons.get(name, [])
            alts.append(
                {
                    "name": name,
                    "score": score,
                    "reason": reason_list[-1] if reason_list else "Runner-up for this profile.",
                }
            )
        return alts

    def _compatibility_message(self, language: str, framework: str) -> str | None:
        if not language or not framework:
            return None
        if not self.is_compatible_stack(language, framework):
            required = ", ".join(FRAMEWORK_LANGUAGES.get(framework, ()))
            return (
                f"{language} + {framework} is incompatible because {framework} "
                f"requires {required or 'a specific host language'}."
            )
        return None

    def _maybe_add_user_preferred_alternative(
        self,
        alts: list[dict[str, Any]],
        user_pref: dict[str, Any],
        norm: NormalizedRequest,
        ctx: _ScoringContext | None = None,
    ) -> list[dict[str, Any]]:
        if not user_pref.get("is_provided"):
            return alts
        if not user_pref.get("is_compatible"):
            return alts
        if user_pref.get("alignment_status") == "Aligned":
            return alts
        lang = user_pref.get("language") or ""
        fw = user_pref.get("framework") or ""
        sdlc = user_pref.get("sdlc") or ""
        if not (lang and fw and sdlc):
            return alts
        duplicate = any(
            a["language"] == lang and a["framework"] == fw and a["sdlc"] == sdlc
            for a in alts
        )
        if duplicate:
            return alts
        if user_pref.get("score", 0) < 30:
            return alts
        if ctx is not None:
            resolved = self._resolve_alternative_stack_row(lang, fw, sdlc, ctx, norm)
            sdlc = resolved["sdlc"]
            pref_raw = int(resolved["stack_score"])
        else:
            if sdlc == "DevOps" and not self._is_devops_primary_project(norm):
                sdlc = "Agile"
            pref_raw = int(user_pref.get("score", 0))
        entry = {
            "language": lang,
            "framework": fw,
            "sdlc": sdlc,
            "_raw_stack_score": pref_raw,
            "fit_score": pref_raw,
            "best_for": (
                f"Honors your stated preference while remaining compatible with "
                f"{norm.project_type} constraints."
            ),
            "limitation": "May score below the top system recommendation for current weighted inputs.",
            "source": "User Preferred Stack",
        }
        return [entry, *alts][:5]

    @staticmethod
    def _format_preferred_stack_label(pref: dict[str, Any]) -> str:
        parts = [pref.get("language"), pref.get("framework"), pref.get("sdlc")]
        return " + ".join(p for p in parts if p)

    def _sql_support_note(self, norm: NormalizedRequest, language: str) -> str | None:
        if language == "SQL" or not norm.is_database_heavy:
            return None
        return (
            "SQL remains important as a supporting database/query technology for reporting, "
            "records, and analytics even though the primary application language differs."
        )

    @staticmethod
    def _risk_to_string(item: dict[str, Any]) -> str:
        return (
            f"{item.get('risk')}: {item.get('reason')} "
            f"Impact: {item.get('impact')} Mitigation: {item.get('mitigation')}"
        )

    @staticmethod
    def _skill_gap_to_string(item: dict[str, Any]) -> str:
        return (
            f"{item.get('skill')} — required {item.get('required_level')}, "
            f"your level {item.get('user_level')} ({item.get('gap_level')} gap): "
            f"{item.get('suggestion')}"
        )

    @staticmethod
    def _gap_level(user: str, required: str) -> str:
        order = {"beginner": 0, "intermediate": 1, "advanced": 2}
        u = order.get(user.lower(), 1)
        r = order.get(required.lower(), 1)
        if u >= r:
            return "Low"
        if r - u == 1:
            return "Moderate"
        return "High"


# Framework skill maps (all framework candidates)
FRAMEWORK_SKILL_MAP: dict[str, dict[str, str]] = {
    "Laravel": {
        "skill": "Laravel (PHP MVC)",
        "required_level": "Intermediate",
        "suggestion": "Practice routing, Eloquent ORM, migrations, and Laravel authentication scaffolding.",
    },
    "FastAPI": {
        "skill": "FastAPI (Python APIs)",
        "required_level": "Intermediate",
        "suggestion": "Learn Python typing, Pydantic models, dependency injection, and OpenAPI docs.",
    },
    "Django": {
        "skill": "Django (Python web)",
        "required_level": "Intermediate",
        "suggestion": "Study Django models, admin, class-based views, and built-in auth permissions.",
    },
    "Flask": {
        "skill": "Flask (Python microframework)",
        "required_level": "Beginner",
        "suggestion": "Build small apps with blueprints, Jinja templates, and SQLAlchemy basics.",
    },
    "React": {
        "skill": "React (UI components)",
        "required_level": "Intermediate",
        "suggestion": "Learn components, hooks, state management, and API integration patterns.",
    },
    "Vue": {
        "skill": "Vue.js",
        "required_level": "Intermediate",
        "suggestion": "Practice Vue SFCs, composition API, and Vue Router for SPA flows.",
    },
    "Angular": {
        "skill": "Angular (enterprise SPA)",
        "required_level": "Advanced",
        "suggestion": "Study modules, services, RxJS, and Angular CLI project structure.",
    },
    "Next.js": {
        "skill": "Next.js (React meta-framework)",
        "required_level": "Intermediate",
        "suggestion": "Learn file-based routing, SSR/SSG, and deployment to cloud hosting.",
    },
    "NestJS": {
        "skill": "NestJS (Node APIs)",
        "required_level": "Advanced",
        "suggestion": "Study modules, providers, guards, and TypeScript decorators in NestJS.",
    },
    "Express.js": {
        "skill": "Express.js",
        "required_level": "Intermediate",
        "suggestion": "Practice middleware, routing, validation, and REST API design in Express.",
    },
    "Flutter": {
        "skill": "Flutter (Dart UI)",
        "required_level": "Intermediate",
        "suggestion": "Learn Dart syntax, widgets, state management, and platform builds.",
    },
    "Spring Boot": {
        "skill": "Spring Boot (Java)",
        "required_level": "Advanced",
        "suggestion": "Study Spring DI, REST controllers, JPA, and security configuration.",
    },
    "ASP.NET Core": {
        "skill": "ASP.NET Core (C#)",
        "required_level": "Intermediate",
        "suggestion": "Learn C#, EF Core, Razor/API endpoints, and deployment to IIS or cloud.",
    },
    "Ruby on Rails": {
        "skill": "Ruby on Rails",
        "required_level": "Intermediate",
        "suggestion": "Practice Rails MVC, ActiveRecord, and convention-over-configuration workflows.",
    },
    "Tauri": {
        "skill": "Tauri (desktop shell)",
        "required_level": "Advanced",
        "suggestion": "Learn Rust/TS integration, IPC, packaging, and desktop security boundaries.",
    },
    "Flet": {
        "skill": "Flet (Python UI)",
        "required_level": "Beginner",
        "suggestion": (
            "Learn Flet controls, layout, event handling, routing/navigation, and state "
            "management; then connect Python services, databases, and packaging basics."
        ),
    },
}


def _roadmap_phase(
    phase: str,
    title: str,
    description: str,
    objectives: list[str],
    deliverables: list[str],
    priorities: list[str],
    focus: str,
) -> dict[str, Any]:
    return {
        "phase": phase,
        "title": title,
        "description": description,
        "objectives": objectives,
        "deliverables": deliverables,
        "priorities": priorities,
        "estimated_focus": focus,
    }


ROADMAP_TEMPLATES: dict[str, list[dict[str, Any]]] = {
    "Agile": [
        _roadmap_phase("1", "Discovery", "Clarify users and MVP scope.", ["User stories"], ["Backlog"], ["Scope"], "1–2 weeks"),
        _roadmap_phase("2", "Sprints", "Iterative build and review.", ["Working increments"], ["MVP modules"], ["Core features"], "Ongoing"),
        _roadmap_phase("3", "Release", "Harden and deploy.", ["Stable release"], ["Deployable build"], ["Quality"], "Final sprint"),
    ],
    "Waterfall": [
        _roadmap_phase("1", "Requirements", "Document scope and constraints.", ["Signed spec"], ["SRS"], ["Clarity"], "20%"),
        _roadmap_phase("2", "Design", "Architecture and UI design.", ["Design docs"], ["Diagrams"], ["Structure"], "20%"),
        _roadmap_phase("3", "Implementation", "Build per specification.", ["Codebase"], ["Modules"], ["Delivery"], "40%"),
        _roadmap_phase("4", "Verification", "Test and deploy.", ["Test reports"], ["Release"], ["Quality"], "20%"),
    ],
    "Iterative": [
        _roadmap_phase("1", "Iteration 1", "Core prototype.", ["Feasibility"], ["Prototype"], ["Risk reduction"], "25%"),
        _roadmap_phase("2", "Iteration 2", "Expand features.", ["Feature growth"], ["Beta"], ["Feedback"], "35%"),
        _roadmap_phase("3", "Iteration 3", "Production readiness.", ["Stabilization"], ["Release"], ["Hardening"], "40%"),
    ],
    "Incremental": [
        _roadmap_phase("1", "Increment A", "Deliver first usable slice.", ["Partial value"], ["Module A"], ["MVP"], "30%"),
        _roadmap_phase("2", "Increment B", "Add major capabilities.", ["Expanded system"], ["Module B"], ["Growth"], "40%"),
        _roadmap_phase("3", "Increment C", "Complete remaining scope.", ["Full feature set"], ["Final release"], ["Completion"], "30%"),
    ],
    "Spiral": [
        _roadmap_phase("1", "Planning", "Objectives and risk analysis.", ["Risk register"], ["Plan"], ["Risk"], "15%"),
        _roadmap_phase("2", "Prototype", "Validate risky areas.", ["Proofs"], ["Prototype"], ["Learning"], "25%"),
        _roadmap_phase("3", "Engineering", "Build production quality.", ["Production build"], ["System"], ["Quality"], "40%"),
        _roadmap_phase("4", "Evaluation", "Review and next cycle.", ["Lessons learned"], ["Release decision"], ["Governance"], "20%"),
    ],
    "V-Model": [
        _roadmap_phase("1", "Requirements", "Define tests from requirements.", ["Test plan"], ["Specs"], ["Traceability"], "20%"),
        _roadmap_phase("2", "Design", "Map design to integration tests.", ["Design tests"], ["Design docs"], ["Validation"], "20%"),
        _roadmap_phase("3", "Build & Test", "Implement with unit/integration tests.", ["Verified build"], ["Code"], ["Quality"], "40%"),
        _roadmap_phase("4", "Acceptance", "User acceptance testing.", ["UAT sign-off"], ["Release"], ["Compliance"], "20%"),
    ],
    "RAD": [
        _roadmap_phase("1", "Workshops", "Rapid requirements with users.", ["Agreed scope"], ["Wireframes"], ["Speed"], "15%"),
        _roadmap_phase("2", "Construction", "Iterative UI + logic build.", ["Working UI"], ["MVP"], ["Feedback"], "55%"),
        _roadmap_phase("3", "Cutover", "Integrate and deploy quickly.", ["Live system"], ["Deploy"], ["Stability"], "30%"),
    ],
    "Prototype Model": [
        _roadmap_phase("1", "Prototype", "Throwaway or evolutionary prototype.", ["Validated UX"], ["Prototype"], ["Learning"], "35%"),
        _roadmap_phase("2", "Refinement", "Incorporate feedback.", ["Revised design"], ["Improved UI"], ["Fit"], "35%"),
        _roadmap_phase("3", "Production", "Build final system.", ["Production app"], ["Release"], ["Quality"], "30%"),
    ],
    "Scrum": [
        _roadmap_phase("1", "Sprint 0", "Backlog grooming and setup.", ["Ready backlog"], ["Infrastructure"], ["Foundation"], "10%"),
        _roadmap_phase("2", "Sprints 1–n", "Sprint delivery with reviews.", ["Increments"], ["Potentially shippable items"], ["Velocity"], "70%"),
        _roadmap_phase("3", "Release", "Potentially shippable product.", ["Release"], ["Deploy"], ["Done"], "20%"),
    ],
    "Kanban": [
        _roadmap_phase("1", "Flow setup", "Define board and WIP limits.", ["Kanban board"], ["Policies"], ["Flow"], "15%"),
        _roadmap_phase("2", "Continuous delivery", "Pull work through stages.", ["Features shipped"], ["Metrics"], ["Throughput"], "70%"),
        _roadmap_phase("3", "Optimize", "Reduce bottlenecks.", ["Improved cycle time"], ["Stable flow"], ["Efficiency"], "15%"),
    ],
    "DevOps": [
        _roadmap_phase("1", "CI/CD", "Pipeline and environments.", ["Automated builds"], ["Pipeline"], ["Automation"], "30%"),
        _roadmap_phase("2", "Build & monitor", "Develop with observability.", ["Instrumented app"], ["Dashboards"], ["Reliability"], "40%"),
        _roadmap_phase("3", "Operate", "Release and iterate in production.", ["Deployed services"], ["Runbooks"], ["Ops"], "30%"),
    ],
    "Lean": [
        _roadmap_phase("1", "Value stream", "Identify waste and MVP value.", ["Value map"], ["MVP scope"], ["Lean focus"], "20%"),
        _roadmap_phase("2", "Build MVP", "Deliver minimum valuable product.", ["MVP"], ["Core flow"], ["Speed"], "50%"),
        _roadmap_phase("3", "Improve", "Measure and refine.", ["Metrics"], ["Enhancements"], ["Learning"], "30%"),
    ],
    "Big Bang Model": [
        _roadmap_phase("1", "Design & build", "Single integrated effort.", ["Working build"], ["All modules"], ["Speed"], "70%"),
        _roadmap_phase("2", "Test & release", "Test then deploy.", ["Release"], ["Deploy package"], ["Completion"], "30%"),
    ],
    "Feature-Driven Development (FDD)": [
        _roadmap_phase("1", "Model", "Overall object model.", ["Domain model"], ["Model doc"], ["Domain"], "20%"),
        _roadmap_phase("2", "Feature list", "Decompose into features.", ["Feature backlog"], ["Feature map"], ["Planning"], "20%"),
        _roadmap_phase("3", "By feature", "Design/build per feature.", ["Feature sets"], ["Completed features"], ["Delivery"], "60%"),
    ],
    "Extreme Programming (XP)": [
        _roadmap_phase("1", "Planning game", "Stories and release plan.", ["Stories"], ["Plan"], ["Collaboration"], "15%"),
        _roadmap_phase("2", "Iterations", "TDD, pair programming, small releases.", ["Tested code"], ["Frequent builds"], ["Quality"], "70%"),
        _roadmap_phase("3", "Release", "Customer-approved release.", ["Release"], ["Acceptance"], ["Feedback"], "15%"),
    ],
}
