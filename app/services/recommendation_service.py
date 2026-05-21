"""Weighted multi-criteria recommendation engine (Phase 1).

The scoring weights are not claimed to be absolute or expert-validated. They are
designed as a source-based decision-support model. The criteria are mapped to
recognized software quality characteristics, software life-cycle considerations,
project tailoring principles, and technology compatibility profiles. The scoring
can be further validated using representative test cases and sensitivity testing.

Method: Weighted Multi-Criteria Decision Matrix / Weighted Scoring Model.

Source basis:
- ISO/IEC 25010 — functional suitability, performance, compatibility, usability,
  reliability, security, maintainability, portability.
- ISO/IEC/IEEE 12207 — life-cycle process suitability (SDLC selection).
- PMBOK tailoring — predictive vs adaptive process choice from project context.
- Technology profiles — official documentation and credible references (names only).

This service has no Flet, database, or AI dependencies.

SQL gating:
SQL is treated primarily as a database/query language. It is recommended as the main
stack only for database-centered systems such as records management, reporting,
analytics, and data warehouse projects. For general application development, SQL may
be included as a supporting database technology rather than the primary programming
language.
"""

from __future__ import annotations

import re
from typing import Any

from app.schemas.recommendation_schema import RecommendationRequest, RecommendationResult
from app.services.recommendation_profiles import (
    FRAMEWORK_PROFILES,
    LANGUAGE_FRAMEWORK_MAP,
    LANGUAGE_PROFILES,
    MATCH_MODERATE,
    MATCH_STRONG,
    MATCH_VERY_STRONG,
    MATCH_WEAK,
    SDLC_PROFILES,
    SQL_FRAMEWORK_LABEL,
    FrameworkTechProfile,
    LanguageTechProfile,
    SDLCTechProfile,
    match_points,
)

class RecommendationService:
    """Deterministic weighted scoring engine for stack recommendations."""

    # Database-centered project types — SQL may compete as the primary language.
    _DATABASE_FOCUSED_PROJECT_TYPES = frozenset(
        {
            "Database System",
            "Data Warehouse",
            "Reporting System",
            "Analytics System",
            "Records Management System",
            "Data Management System",
        }
    )

    # Strong database-centered features (two or more can qualify SQL as primary).
    _DATABASE_STRONG_FEATURES = frozenset(
        {
            "reports / analytics",
            "data warehousing",
            "database management",
            "records management",
            "query-heavy reporting",
            "data analysis",
        }
    )

    # Features that suggest SQL as supporting technology only.
    _DATABASE_SUPPORT_FEATURES = frozenset(
        {
            "reports / analytics",
            "data warehousing",
            "database management",
            "records management",
            "query-heavy reporting",
            "data analysis",
            "crud operations",
            "crud",
            "role-based access",
        }
    )

    # Full phrases only — avoid matching general goals that mention "records" or "reports".
    _DATABASE_GOAL_KEYWORDS = (
        "database system",
        "data warehouse",
        "reporting system",
        "analytics platform",
        "records management",
        "compliance records database",
        "query-heavy reporting",
        "database-centered",
        "database centered",
    )

    _LANGUAGE_CRITERIA = (
        "project_type",
        "features",
        "platform",
        "development_experience",
        "scalability",
        "performance",
        "security",
        "budget",
        "maintainability",
        "deployment",
        "project_goal",
    )

    _FRAMEWORK_CRITERIA = (
        "project_type",
        "features",
        "platform",
        "development_experience",
        "scalability",
        "performance",
        "security",
        "budget",
        "maintainability",
        "deployment",
    )

    _SDLC_CRITERIA = (
        "requirements_stability",
        "timeline",
        "team_size",
        "stakeholder_involvement",
        "complexity",
        "maintenance",
        "deployment",
    )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def recommend(self, request: RecommendationRequest) -> RecommendationResult:
        """Run full weighted scoring and return a structured result."""
        norm = self._normalize_request(request)

        language_scores, lang_matched = self._calculate_language_scores(norm)
        top_language = max(language_scores, key=language_scores.get)

        framework_scores, fw_matched = self._calculate_framework_scores(norm, top_language)
        top_framework = max(framework_scores, key=framework_scores.get)

        sdlc_scores, sdlc_matched = self._calculate_sdlc_scores(norm)
        top_sdlc = max(sdlc_scores, key=sdlc_scores.get)

        confidence = self._compute_confidence(
            language_scores,
            framework_scores,
            sdlc_scores,
            lang_matched,
            fw_matched,
            sdlc_matched,
        )
        label = self.get_confidence_label(confidence)

        explanation = self.build_explanation(
            norm, top_language, top_framework, top_sdlc, confidence, label
        )
        sql_support = self.build_sql_support_note(norm, top_language)
        if sql_support:
            explanation = f"{explanation}\n\n{sql_support}"

        skill_gaps = self.build_skill_gaps(norm, top_language, top_framework)
        if sql_support and sql_support not in skill_gaps:
            skill_gaps = [*skill_gaps, sql_support]

        return RecommendationResult(
            recommended_language=top_language,
            recommended_framework=top_framework,
            recommended_sdlc=top_sdlc,
            confidence_score=round(confidence, 1),
            confidence_label=label,
            language_scores=language_scores,
            framework_scores=framework_scores,
            sdlc_scores=sdlc_scores,
            alternative_languages=self.get_top_items(language_scores, top_language),
            alternative_frameworks=self.get_top_items(framework_scores, top_framework),
            alternative_sdlc_models=self.get_top_items(sdlc_scores, top_sdlc),
            explanation=explanation,
            risks=self.build_risks(norm, top_language, top_framework, top_sdlc),
            skill_gaps=skill_gaps,
            roadmap=self.build_roadmap(norm, top_language, top_framework, top_sdlc),
            scoring_basis=self.get_scoring_basis(),
            defense_explanation=self.get_defense_explanation(),
            validation_note=self.get_validation_note(),
        )

    def calculate_language_scores(self, request: RecommendationRequest) -> dict[str, float]:
        """Score each programming language using the weighted decision matrix."""
        scores, _ = self._calculate_language_scores(request)
        return scores

    def calculate_framework_scores(
        self,
        request: RecommendationRequest,
        recommended_language: str,
    ) -> dict[str, float]:
        """Score frameworks compatible with the given language only."""
        scores, _ = self._calculate_framework_scores(request, recommended_language)
        return scores

    def calculate_sdlc_scores(self, request: RecommendationRequest) -> dict[str, float]:
        """Score SDLC models using 12207 / PMBOK tailoring dimensions."""
        scores, _ = self._calculate_sdlc_scores(request)
        return scores

    def _calculate_language_scores(
        self, request: RecommendationRequest
    ) -> tuple[dict[str, float], dict[str, int]]:
        norm = self._normalize_request(request)
        scores: dict[str, float] = {}
        matched: dict[str, int] = {}

        for profile in LANGUAGE_PROFILES:
            total, hits = self._score_language_profile(profile, norm)
            scores[profile.name] = round(total, 2)
            matched[profile.name] = hits

        self._apply_sql_language_gating(norm, scores)

        return scores, matched

    def is_database_focused_project(self, request: RecommendationRequest) -> bool:
        """Return True only when the project is clearly database-centered.

        General information systems with CRUD, reports, or role-based access alone
        are not database-focused. SQL may win as the primary language only when
        the project type, goal, or feature set explicitly indicates a database-
        centered system.
        """
        if request.project_type in self._DATABASE_FOCUSED_PROJECT_TYPES:
            return True

        goal_lower = request.project_goal.lower()
        if any(keyword in goal_lower for keyword in self._DATABASE_GOAL_KEYWORDS):
            return True

        strong_feature_hits = sum(
            1
            for feature in request.selected_features
            if self._normalize_feature_name(feature) in self._DATABASE_STRONG_FEATURES
        )
        # Requires two strong database features; one (e.g. Reports / Analytics) is not enough.
        return strong_feature_hits >= 2

    def has_database_supporting_needs(self, request: RecommendationRequest) -> bool:
        """Return True when SQL is relevant as supporting tech (not primary winner)."""
        if self.is_database_focused_project(request):
            return False

        goal_lower = request.project_goal.lower()
        if any(
            token in goal_lower
            for token in ("database", "reporting", "analytics", "records", "data warehouse")
        ):
            return True

        return any(
            self._normalize_feature_name(feature) in self._DATABASE_SUPPORT_FEATURES
            for feature in request.selected_features
        )

    def build_sql_support_note(
        self, request: RecommendationRequest, recommended_language: str
    ) -> str | None:
        """Note when SQL remains important but is not the primary application language."""
        if recommended_language == "SQL":
            return None
        if not self.has_database_supporting_needs(request):
            return None
        return (
            "SQL/database design remains important for this project because the selected "
            "features or goals include reporting, records management, CRUD/data operations, "
            "or other data-heavy requirements. Use SQL as a supporting database technology "
            "alongside the recommended application language — not as the standalone "
            "application framework unless the project is database-centered."
        )

    @staticmethod
    def _normalize_feature_name(feature: str) -> str:
        return feature.strip().lower()

    def _apply_sql_language_gating(
        self, request: RecommendationRequest, scores: dict[str, float]
    ) -> None:
        """Cap SQL so it cannot win unless the project is database-centered."""
        if "SQL" not in scores or self.is_database_focused_project(request):
            return

        non_sql = [value for name, value in scores.items() if name != "SQL"]
        if not non_sql:
            scores["SQL"] = 0.0
            return

        top_non_sql_score = max(non_sql)
        scores["SQL"] = min(scores["SQL"], top_non_sql_score * 0.60)

    def _calculate_framework_scores(
        self,
        request: RecommendationRequest,
        recommended_language: str,
    ) -> tuple[dict[str, float], dict[str, int]]:
        norm = self._normalize_request(request)
        allowed = set(LANGUAGE_FRAMEWORK_MAP.get(recommended_language, []))
        scores: dict[str, float] = {}
        matched: dict[str, int] = {}

        for profile in FRAMEWORK_PROFILES:
            if profile.name not in allowed and profile.language == recommended_language:
                allowed.add(profile.name)
            if profile.name not in allowed:
                continue
            total, hits = self._score_framework_profile(profile, norm)
            scores[profile.name] = round(total, 2)
            matched[profile.name] = hits

        if recommended_language == "SQL" and SQL_FRAMEWORK_LABEL not in scores:
            scores[SQL_FRAMEWORK_LABEL] = float(MATCH_VERY_STRONG * 3)
            matched[SQL_FRAMEWORK_LABEL] = 3

        if not scores and recommended_language in LANGUAGE_FRAMEWORK_MAP:
            for name in LANGUAGE_FRAMEWORK_MAP[recommended_language]:
                scores[name] = 0.0
                matched[name] = 0

        return scores, matched

    def _calculate_sdlc_scores(
        self, request: RecommendationRequest
    ) -> tuple[dict[str, float], dict[str, int]]:
        norm = self._normalize_request(request)
        scores: dict[str, float] = {}
        matched: dict[str, int] = {}

        for profile in SDLC_PROFILES:
            total, hits = self._score_sdlc_profile(profile, norm)
            scores[profile.name] = round(total, 2)
            matched[profile.name] = hits

        return scores, matched

    @staticmethod
    def get_confidence_label(score: float) -> str:
        if score >= 85:
            return "Very High"
        if score >= 70:
            return "High"
        if score >= 50:
            return "Moderate"
        return "Low"

    def get_top_items(
        self,
        scores: dict[str, float],
        winner: str,
        limit: int = 3,
    ) -> list[dict[str, Any]]:
        """Return top alternatives excluding the selected winner."""
        ranked = sorted(
            ((name, score) for name, score in scores.items() if name != winner),
            key=lambda item: item[1],
            reverse=True,
        )
        alternatives: list[dict[str, Any]] = []
        for name, score in ranked[:limit]:
            alternatives.append(
                {
                    "name": name,
                    "score": score,
                    "reason": self._alternative_reason(name, score, winner, scores.get(winner, 0)),
                }
            )
        return alternatives

    def build_explanation(
        self,
        request: RecommendationRequest,
        language: str,
        framework: str,
        sdlc: str,
        confidence: float,
        confidence_label: str | None = None,
    ) -> str:
        label = confidence_label or self.get_confidence_label(confidence)
        norm = self._normalize_request(request)

        conf_text = {
            "Very High": (
                "High confidence means the selected stack strongly matched several "
                "weighted criteria with a clear margin over alternatives."
            ),
            "High": (
                "High confidence means the selected stack strongly matched several criteria."
            ),
            "Moderate": (
                "Moderate confidence means the selected stack fits, but alternatives "
                "are also close — review alternatives before committing."
            ),
            "Low": (
                "Low confidence means inputs may be incomplete, conflicting, or not "
                "strongly matched by one stack — refine requirements or compare alternatives."
            ),
        }.get(label, "")

        if language == "SQL":
            language_role = (
                f"Language: {language} is recommended as the primary database/query stack "
                f"because this project is database-centered ({norm.project_type}). "
                f"The {framework} pairing reflects a data-focused implementation approach."
            )
        else:
            language_role = (
                f"Language: {language} is the primary application development language for "
                f"this project. It aligns with your platform ({norm.preferred_platform}), "
                f"experience level ({norm.development_experience}), and project goal. "
                f"Scores reflect ISO/IEC 25010 quality dimensions including functional "
                f"suitability, performance, security, maintainability, and portability. "
                f"SQL may still be used as a supporting database/query technology when the "
                f"project requires data storage, reporting, or analytics alongside the "
                f"application stack."
            )

        return (
            f"For '{norm.project_name}' ({norm.project_type}), the weighted multi-criteria "
            f"decision matrix recommends {language} with {framework}, using the {sdlc} "
            f"life-cycle model (confidence: {confidence:.1f}/100, {label}).\n\n"
            f"{language_role}\n\n"
            f"Framework: {framework} is compatible with {language} and supports your "
            f"selected features and deployment preference ({norm.deployment_preference}).\n\n"
            f"SDLC: {sdlc} fits requirements stability ({norm.requirements_stability}), "
            f"timeline ({norm.timeline}), team size ({norm.team_size}), and stakeholder "
            f"involvement ({norm.stakeholder_involvement}) per ISO/IEC/IEEE 12207 and "
            f"PMBOK tailoring guidance.\n\n"
            f"{conf_text}\n\n"
            "This output is decision-support based on documented criteria — not absolute truth. "
            "Validate with representative test cases and sensitivity testing before defense."
        )

    def build_risks(
        self,
        request: RecommendationRequest,
        language: str,
        framework: str,
        sdlc: str,
    ) -> list[str]:
        norm = self._normalize_request(request)
        risks: list[str] = []

        if norm.complexity in ("High", "Very High") and norm.team_size <= 3:
            risks.append(
                "High complexity with a small team increases delivery and coordination risk."
            )
        if self._normalize_security(norm.security_requirements) == "High":
            risks.append(
                "Elevated security requirements demand authentication, authorization, and "
                "data-protection controls from the first iteration."
            )
        if self._normalize_scalability(norm.scalability_needs) == "High":
            risks.append(
                "High scalability needs introduce infrastructure, caching, and load-testing risks."
            )
        if norm.timeline == "Short":
            risks.append(
                "A short timeline raises incomplete-feature and reduced-testing risk."
            )
        if self._normalize_stability(norm.requirements_stability) == "Changing":
            risks.append(
                "Changing requirements increase scope-creep risk without iterative feedback loops."
            )
        if norm.development_experience == "Beginner" and language in (
            "Java",
            "Rust",
            "JavaScript / TypeScript",
        ):
            risks.append(
                f"Beginner experience with {language} and {framework} adds learning-curve risk."
            )
        if self._normalize_performance(norm.performance_requirements) == "High":
            risks.append(
                "Strict performance requirements need early profiling, benchmarking, and optimization."
            )
        if not risks:
            risks.append(
                "No major risks flagged; maintain code review, testing, and documentation discipline."
            )
        return risks

    def build_skill_gaps(
        self,
        request: RecommendationRequest,
        language: str,
        framework: str,
    ) -> list[str]:
        norm = self._normalize_request(request)
        if norm.development_experience not in ("Beginner", "Team has mixed experience"):
            return [
                f"Team experience appears adequate for {language} and {framework}; "
                "focus on consistent architecture and quality practices."
            ]

        gaps_map: dict[tuple[str, str], list[str]] = {
            ("Java", "Spring Boot"): [
                "Learn Java fundamentals, OOP, and JVM tooling.",
                "Study REST APIs, dependency injection, and Spring Boot project structure.",
            ],
            ("Python", "FastAPI"): [
                "Learn Python basics, virtual environments, and typing.",
                "Practice API routes, request validation, and OpenAPI documentation in FastAPI.",
            ],
            ("JavaScript / TypeScript", "Next.js"): [
                "Learn JavaScript/TypeScript, React components, and hooks.",
                "Study Next.js routing, data fetching, and deployment to cloud hosting.",
            ],
            ("Dart", "Flutter"): [
                "Learn Dart syntax, widgets, and layout.",
                "Practice Flutter state management and platform builds (Android/iOS).",
            ],
            ("PHP", "Laravel"): [
                "Learn PHP basics, MVC pattern, routing, and validation.",
                "Study Laravel migrations, Eloquent ORM, and authentication scaffolding.",
            ],
            ("C#", "ASP.NET Core"): [
                "Learn C# fundamentals and .NET project structure.",
                "Practice ASP.NET Core controllers, EF Core, and deployment on cloud or IIS.",
            ],
            ("Kotlin", "Android/Ktor"): [
                "Learn Kotlin syntax and Android activity/fragment lifecycle or Ktor server basics.",
            ],
            ("Swift", "SwiftUI"): [
                "Learn Swift basics and SwiftUI declarative UI patterns.",
            ],
            ("Ruby", "Rails"): [
                "Learn Ruby syntax, Rails conventions, MVC, and ActiveRecord.",
            ],
            ("Go", "Gin"): [
                "Learn Go modules, HTTP handlers, and middleware patterns in Gin.",
            ],
            ("Rust", "Tauri"): [
                "Learn Rust ownership model and Tauri command bridge to a web frontend.",
            ],
        }

        key = (language, framework)
        if key in gaps_map:
            return gaps_map[key]
        return [
            f"Build fundamentals in {language} before advanced {framework} features.",
            "Use official documentation tutorials and a small practice project first.",
        ]

    def build_roadmap(
        self,
        request: RecommendationRequest,
        language: str,
        framework: str,
        sdlc: str,
    ) -> list[dict[str, str]]:
        norm = self._normalize_request(request)
        iterative = self._normalize_stability(norm.requirements_stability) == "Changing"
        sprint_note = (
            "Use short iterations with stakeholder demos."
            if iterative
            else "Lock scope and trace requirements to design artifacts."
        )

        return [
            {
                "phase": "1",
                "title": "Requirement Gathering",
                "description": (
                    f"Document goals for '{norm.project_name}', enumerate features "
                    f"({', '.join(norm.selected_features) or 'core features'}), and map "
                    f"non-functional needs (security, performance, scalability). {sprint_note}"
                ),
            },
            {
                "phase": "2",
                "title": "Planning & Design",
                "description": (
                    f"Choose {sdlc} ceremonies/artifacts, design data models, and define "
                    f"architecture for {language} + {framework} on {norm.preferred_platform}."
                ),
            },
            {
                "phase": "3",
                "title": "Development",
                "description": (
                    f"Implement core workflows with {framework}, following {language} best "
                    f"practices and team size of {norm.team_size}."
                ),
            },
            {
                "phase": "4",
                "title": "Testing",
                "description": (
                    "Add unit, integration, and security tests; validate performance and "
                    "role-based access for critical features."
                ),
            },
            {
                "phase": "5",
                "title": "Deployment",
                "description": (
                    f"Deploy to {norm.deployment_preference} with monitoring, backups, and "
                    "environment configuration."
                ),
            },
            {
                "phase": "6",
                "title": "Maintenance",
                "description": (
                    f"Plan updates for {norm.maintenance_expectations} maintenance expectations; "
                    "track defects, dependencies, and documentation."
                ),
            },
        ]

    @staticmethod
    def get_scoring_basis() -> str:
        return (
            "Weighted Multi-Criteria Decision Matrix: each technology is scored against "
            "project type, features (ISO/IEC 25010 functional suitability), platform and "
            "deployment (portability/compatibility), experience (usability), scalability and "
            "performance (performance efficiency / reliability), security, budget, and "
            "maintainability. SDLC models are scored using ISO/IEC/IEEE 12207 process fit and "
            "PMBOK tailoring for stability, timeline, team size, and stakeholder involvement. "
            "Match levels: very strong=30, strong=20, moderate=10, weak=0 points."
        )

    @staticmethod
    def get_defense_explanation() -> str:
        return (
            "The recommendation engine uses a weighted multi-criteria decision matrix. "
            "The criteria are based on ISO/IEC 25010 software quality characteristics, "
            "ISO/IEC/IEEE 12207 software life-cycle considerations, and PMBOK project "
            "tailoring principles. Each technology is assigned a compatibility profile "
            "based on official documentation and credible software engineering references. "
            "The system computes scores consistently, applies language-framework compatibility "
            "rules, ranks alternatives, and returns a confidence level. The system does not "
            "claim absolute correctness; it provides explainable decision support."
        )

    @staticmethod
    def get_validation_note() -> str:
        return (
            "The scoring weights are not claimed to be absolute or expert-validated. They are "
            "designed as a source-based decision-support model. The criteria are mapped to "
            "recognized software quality characteristics, software life-cycle considerations, "
            "project tailoring principles, and technology compatibility profiles. The scoring "
            "can be further validated using representative test cases and sensitivity testing."
        )

    # ------------------------------------------------------------------
    # Scoring internals
    # ------------------------------------------------------------------

    def _score_language_profile(
        self, profile: LanguageTechProfile, request: RecommendationRequest
    ) -> tuple[float, int]:
        total = 0.0
        hits = 0

        # Functional suitability — project type (ISO/IEC 25010)
        level = profile.project_types.get(request.project_type, 1)
        total += match_points(level)
        hits += 1 if level > 0 else 0

        # Functional suitability — selected features
        if request.selected_features:
            feature_points = [
                match_points(profile.features.get(f, 1)) for f in request.selected_features
            ]
            total += sum(feature_points) / len(feature_points)
            hits += sum(1 for p in feature_points if p > 0)
        else:
            total += MATCH_MODERATE
            hits += 1

        # Portability / compatibility — platform
        level = profile.platforms.get(request.preferred_platform, 1)
        total += match_points(level)
        hits += 1 if level > 0 else 0

        # Usability — developer experience
        level = profile.experience.get(request.development_experience, 2)
        total += match_points(level)
        hits += 1 if level > 0 else 0

        # Performance efficiency & reliability — scalability
        level = profile.scalability.get(
            self._normalize_scalability(request.scalability_needs), 2
        )
        total += match_points(level)
        hits += 1 if level > 0 else 0

        # Performance efficiency
        level = profile.performance.get(
            self._normalize_performance(request.performance_requirements), 2
        )
        total += match_points(level)
        hits += 1 if level > 0 else 0

        # Security (ISO/IEC 25010)
        level = profile.security.get(
            self._normalize_security(request.security_requirements), 2
        )
        total += match_points(level)
        hits += 1 if level > 0 else 0

        # Budget / resource constraints
        level = profile.budget.get(
            self._normalize_budget(request.budget_constraints), 2
        )
        total += match_points(level)
        hits += 1 if level > 0 else 0

        # Maintainability (ISO/IEC 25010)
        level = profile.maintainability.get(
            self._normalize_maintenance(request.maintenance_expectations), 2
        )
        total += match_points(level)
        hits += 1 if level > 0 else 0

        # Portability — deployment preference
        level = profile.deployment.get(request.deployment_preference, 2)
        total += match_points(level)
        hits += 1 if level > 0 else 0

        # Functional suitability — project goal keywords
        goal_level = self._goal_match_level(request.project_goal, profile.goal_keywords)
        total += match_points(goal_level)
        hits += 1 if goal_level > 0 else 0

        return total, hits

    def _score_framework_profile(
        self, profile: FrameworkTechProfile, request: RecommendationRequest
    ) -> tuple[float, int]:
        total = 0.0
        hits = 0

        level = profile.project_types.get(request.project_type, 1)
        total += match_points(level)
        hits += 1 if level > 0 else 0

        if request.selected_features:
            feature_points = [
                match_points(profile.features.get(f, 1)) for f in request.selected_features
            ]
            total += sum(feature_points) / len(feature_points)
            hits += sum(1 for p in feature_points if p > 0)
        else:
            total += MATCH_MODERATE
            hits += 1

        for attr, normalizer in (
            ("platforms", None),
            ("experience", None),
            ("scalability", self._normalize_scalability),
            ("performance", self._normalize_performance),
            ("security", self._normalize_security),
            ("budget", self._normalize_budget),
            ("maintainability", self._normalize_maintenance),
            ("deployment", None),
        ):
            mapping = getattr(profile, attr)
            if not mapping:
                continue
            if normalizer and attr != "platforms":
                if attr == "scalability":
                    key = normalizer(request.scalability_needs)
                elif attr == "performance":
                    key = normalizer(request.performance_requirements)
                elif attr == "security":
                    key = normalizer(request.security_requirements)
                elif attr == "budget":
                    key = normalizer(request.budget_constraints)
                elif attr == "maintainability":
                    key = normalizer(request.maintenance_expectations)
                else:
                    key = ""
            elif attr == "platforms":
                key = request.preferred_platform
            elif attr == "experience":
                key = request.development_experience
            else:
                key = request.deployment_preference

            level = mapping.get(key, 2) if mapping else 2
            total += match_points(level)
            hits += 1 if level > 0 else 0

        return total, hits

    def _score_sdlc_profile(
        self, profile: SDLCTechProfile, request: RecommendationRequest
    ) -> tuple[float, int]:
        total = 0.0
        hits = 0

        # ISO/IEC/IEEE 12207 — requirements stability drives process selection
        stability = self._normalize_stability(request.requirements_stability)
        level = profile.requirements_stability.get(stability, 1)
        total += match_points(level)
        hits += 1 if level > 0 else 0

        # PMBOK tailoring — timeline
        timeline = self._normalize_timeline(request.timeline)
        level = profile.timeline.get(timeline, 1)
        total += match_points(level)
        hits += 1 if level > 0 else 0

        # Team organization feasibility
        team_band = self._team_size_band(request.team_size)
        level = profile.team_size_band.get(team_band, 1)
        total += match_points(level)
        hits += 1 if level > 0 else 0

        # Stakeholder feedback needs
        stakeholder = self._normalize_stakeholder(request.stakeholder_involvement)
        level = profile.stakeholder.get(stakeholder, 1)
        total += match_points(level)
        hits += 1 if level > 0 else 0

        # Complexity / risk control
        level = profile.complexity.get(request.complexity, 1)
        total += match_points(level)
        hits += 1 if level > 0 else 0

        # Maintenance consideration (12207 maintenance processes)
        maintenance = self._normalize_maintenance(request.maintenance_expectations)
        level = profile.maintenance.get(maintenance, 1)
        total += match_points(level)
        hits += 1 if level > 0 else 0

        # DevOps / deployment alignment
        level = profile.deployment.get(request.deployment_preference, 1)
        total += match_points(level)
        hits += 1 if level > 0 else 0

        return total, hits

    def _compute_confidence(
        self,
        lang_scores: dict[str, float],
        fw_scores: dict[str, float],
        sdlc_scores: dict[str, float],
        lang_matched: dict[str, int],
        fw_matched: dict[str, int],
        sdlc_matched: dict[str, int],
    ) -> float:
        def _category_confidence(
            scores: dict[str, float],
            matched: dict[str, int],
            max_criteria: int,
        ) -> float:
            if not scores:
                return 40.0
            ranked = sorted(scores.values(), reverse=True)
            winner = ranked[0]
            runner = ranked[1] if len(ranked) > 1 else 0.0
            winner_name = max(scores, key=scores.get)
            gap = (winner - runner) / winner if winner > 0 else 0.0
            coverage = matched.get(winner_name, 0) / max(1, max_criteria)
            return min(100.0, winner * 0.35 + gap * 35.0 + coverage * 30.0)

        lang_c = _category_confidence(lang_scores, lang_matched, len(self._LANGUAGE_CRITERIA))
        fw_c = _category_confidence(fw_scores, fw_matched, len(self._FRAMEWORK_CRITERIA))
        sdlc_c = _category_confidence(sdlc_scores, sdlc_matched, len(self._SDLC_CRITERIA))

        blended = lang_c * 0.45 + fw_c * 0.35 + sdlc_c * 0.20
        return max(0.0, min(100.0, blended))

    @staticmethod
    def _alternative_reason(name: str, score: float, winner: str, winner_score: float) -> str:
        gap = winner_score - score
        if gap < 15:
            return f"{name} is a close alternative (score {score:.1f} vs winner {winner_score:.1f})."
        return f"{name} scored {score:.1f} — viable if constraints or team skills differ."

    @staticmethod
    def _goal_match_level(goal: str, keywords: tuple[str, ...]) -> int:
        goal_lower = goal.lower()
        hits = sum(1 for kw in keywords if kw in goal_lower)
        if hits >= 2:
            return 3
        if hits == 1:
            return 2
        if re.search(r"\b(app|system|platform|service|portal)\b", goal_lower):
            return 1
        return 0

    def _normalize_request(self, request: RecommendationRequest) -> RecommendationRequest:
        """Return a copy with normalized tier values for consistent scoring."""
        return RecommendationRequest(
            project_name=request.project_name,
            project_type=request.project_type,
            selected_features=list(request.selected_features),
            project_goal=request.project_goal,
            team_size=max(1, int(request.team_size)),
            complexity=request.complexity,
            timeline=self._normalize_timeline(request.timeline),
            requirements_stability=self._normalize_stability(request.requirements_stability),
            stakeholder_involvement=self._normalize_stakeholder(
                request.stakeholder_involvement
            ),
            preferred_platform=request.preferred_platform,
            development_experience=request.development_experience,
            scalability_needs=self._normalize_scalability(request.scalability_needs),
            performance_requirements=self._normalize_performance(
                request.performance_requirements
            ),
            security_requirements=self._normalize_security(request.security_requirements),
            budget_constraints=self._normalize_budget(request.budget_constraints),
            maintenance_expectations=self._normalize_maintenance(
                request.maintenance_expectations
            ),
            deployment_preference=request.deployment_preference,
        )

    @staticmethod
    def _normalize_timeline(value: str) -> str:
        v = value.lower().strip()
        if v in ("short",) or "less than" in v or "1–2" in v or "1-2" in v:
            return "Short"
        if v in ("long",) or "more than" in v or "5–6" in v or "5-6" in v:
            return "Long"
        if "3–4" in v or "3-4" in v or v == "medium":
            return "Medium"
        return "Medium"

    @staticmethod
    def _normalize_stability(value: str) -> str:
        v = value.lower().strip()
        if v in ("changing", "frequently", "somewhat", "unknown", "experimental"):
            return "Changing"
        if v in ("fixed", "very stable", "mostly stable", "stable"):
            return "Fixed"
        return "Changing" if "chang" in v else "Fixed"

    @staticmethod
    def _normalize_stakeholder(value: str) -> str:
        v = value.lower().strip()
        if "frequent" in v or v in ("very high", "high"):
            return "High" if v != "very high" else "Very High"
        if v == "low":
            return "Low"
        return "Medium"

    @staticmethod
    def _normalize_scalability(value: str) -> str:
        v = value.lower().strip()
        if "large" in v or "grow fast" in v or "expected to grow" in v or v == "high":
            return "High"
        if "small" in v or v == "low":
            return "Low"
        return "Medium"

    @staticmethod
    def _normalize_performance(value: str) -> str:
        v = value.lower().strip()
        if "real-time" in v or "low latency" in v or v == "high":
            return "High"
        if v == "basic" or v == "low":
            return "Low"
        return "Medium"

    @staticmethod
    def _normalize_security(value: str) -> str:
        v = value.lower().strip()
        if "payment" in v or "financial" in v or "sensitive" in v or v == "high":
            return "High"
        if v == "basic" or v == "low":
            return "Low"
        return "Medium"

    @staticmethod
    def _normalize_budget(value: str) -> str:
        v = value.lower().strip()
        if "very limited" in v or v in ("low", "limited"):
            return "Low"
        if "not a concern" in v or "flexible" in v or v == "high":
            return "High"
        return "Medium"

    @staticmethod
    def _normalize_maintenance(value: str) -> str:
        v = value.lower().strip()
        if "production" in v or "long-term" in v:
            return "High"
        if "prototype" in v or "short-term" in v:
            return "Low"
        return "Medium"

    @staticmethod
    def _team_size_band(team_size: int) -> str:
        if team_size <= 1:
            return "Solo"
        if team_size <= 3:
            return "Small"
        if team_size <= 8:
            return "Medium"
        return "Large"
