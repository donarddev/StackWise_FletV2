"""Phase 2.3 test harness — context-aware recommendation engine.

Run from project root::

    python test_recommendation_engine.py
"""

from __future__ import annotations

import sys
from typing import Any

from app.controllers.recommendation_controller import generate_recommendation_from_request
from app.services.recommendation_service import FRAMEWORK_LANGUAGES, FRAMEWORKS, LANGUAGES, SDLC_MODELS

ALL_CANDIDATES = set(LANGUAGES) | set(FRAMEWORKS) | set(SDLC_MODELS)

COMPATIBILITY: dict[str, tuple[str, ...]] = FRAMEWORK_LANGUAGES


def is_compatible(language: str, framework: str) -> bool:
    if framework == "No framework required":
        return language in {"Kotlin", "Swift", "C", "C++", "Go", "Rust", "SQL"}
    allowed = COMPATIBILITY.get(framework)
    if not allowed:
        return True
    return language in allowed


def assert_common(data: dict[str, Any], case_name: str) -> list[str]:
    errors: list[str] = []
    for field in (
        "recommended_language",
        "recommended_framework",
        "recommended_sdlc",
        "confidence_score",
        "confidence_label",
        "alternative_technology_stacks",
        "why_not_this",
        "risk_analysis",
        "skill_gap_analysis",
        "suggested_project_roadmap",
        "user_preferred_stack",
        "scoring_basis",
        "defense_explanation",
        "validation_note",
    ):
        if field not in data:
            errors.append(f"{case_name}: missing field '{field}'")

    lang = data.get("recommended_language", "")
    fw = data.get("recommended_framework", "")
    if lang and fw and not is_compatible(lang, fw):
        errors.append(f"{case_name}: incompatible pair {lang} + {fw}")

    score = int(data.get("confidence_score", 0))
    if score < 60 or score > 95:
        errors.append(f"{case_name}: confidence_score {score} outside 60–95")
    if score in (99, 100):
        errors.append(f"{case_name}: confidence_score must not be {score}")

    for key in ("recommended_language", "recommended_framework", "recommended_sdlc"):
        val = data.get(key, "")
        if val and val not in ALL_CANDIDATES and val not in (
            "No framework required",
            "Database-focused stack",
        ):
            errors.append(f"{case_name}: unsupported candidate in {key}: {val}")

    for alt in data.get("alternative_technology_stacks", []) or []:
        if not is_compatible(alt.get("language", ""), alt.get("framework", "")):
            errors.append(
                f"{case_name}: incompatible alternative {alt.get('language')} + {alt.get('framework')}"
            )
        fit = alt.get("fit_score")
        if fit is not None:
            try:
                fit_i = int(fit)
                if fit_i > 100:
                    errors.append(
                        f"{case_name}: alternative fit_score must not be raw points ({fit_i})"
                    )
                elif fit_i < 60 or fit_i > 95:
                    errors.append(
                        f"{case_name}: alternative fit_score {fit_i} outside 60–95"
                    )
            except (TypeError, ValueError):
                pass

    return errors


def run_case(name: str, payload: dict[str, Any], extra_checks=None) -> list[str]:
    result = generate_recommendation_from_request(payload)
    errors: list[str] = []
    if not result.get("success"):
        return [f"{name}: success=False — {result.get('error')}"]
    data = result["data"]
    errors.extend(assert_common(data, name))
    if extra_checks:
        errors.extend(extra_checks(data, name))
    return errors


def test_student_portal() -> list[str]:
    payload = {
        "project_name": "Student Information Portal",
        "project_type": "Web Application",
        "selected_features": [
            "Authentication",
            "CRUD Operations",
            "Admin Dashboard",
            "Reports / Analytics",
        ],
        "project_goal": (
            "Build a web-based student information portal that allows administrators "
            "to manage student records, user accounts, reports, and basic analytics."
        ),
        "team_size": 3,
        "complexity": "Medium",
        "timeline": "Short",
        "requirements_stability": "Changing",
        "stakeholder_involvement": "High",
        "preferred_platform": "Web",
        "development_experience": "Beginner",
        "scalability_needs": "Medium",
        "performance_requirements": "Medium",
        "security_requirements": "Medium",
        "budget_constraints": "Low",
        "maintenance_expectations": "Medium",
        "deployment_preference": "Cloud deployment",
        "user_preferred_language": "PHP",
        "user_preferred_framework": "Laravel",
        "user_preferred_sdlc": "Waterfall",
        "user_preferred_reason": "I already know Laravel.",
    }

    def checks(data: dict[str, Any], name: str) -> list[str]:
        errs: list[str] = []
        pref = data.get("user_preferred_stack", {})
        if not pref.get("is_provided"):
            errs.append(f"{name}: user_preferred_stack should be provided")
        if not pref.get("is_compatible"):
            errs.append(f"{name}: user preferred PHP + Laravel should be compatible")

        if data["recommended_language"] != "PHP":
            errs.append(
                f"{name}: expected PHP, got {data['recommended_language']}"
            )
        if data["recommended_framework"] != "Laravel":
            errs.append(
                f"{name}: expected Laravel, got {data['recommended_framework']}"
            )
        if data["recommended_sdlc"] not in ("Agile", "RAD"):
            errs.append(
                f"{name}: expected Agile or RAD SDLC, got {data['recommended_sdlc']}"
            )

        alts = data.get("alternative_technology_stacks", []) or []
        has_django_alt = any(
            a.get("language") == "Python" and a.get("framework") == "Django"
            for a in alts
        )
        if not has_django_alt:
            errs.append(f"{name}: expected Python + Django as an alternative stack")

        why_not = data.get("why_not_this", []) or []
        if not why_not:
            errs.append(f"{name}: why_not_this must not be empty")
        else:
            first = why_not[0]
            if first.get("source") != "User Preferred Stack":
                errs.append(
                    f"{name}: first why_not_this should be User Preferred Stack, "
                    f"got {first.get('source')}"
                )
        labels = " ".join(
            w.get("technology_or_stack", "") for w in why_not
        )
        if "User Preferred Stack" not in labels:
            errs.append(f"{name}: expected User Preferred Stack in why_not_this")
        if "Waterfall" not in labels and data["recommended_sdlc"] != "Waterfall":
            errs.append(
                f"{name}: why_not_this should mention preferred Waterfall SDLC mismatch"
            )

        if pref.get("alignment_status") not in ("Partially aligned", "Aligned"):
            errs.append(
                f"{name}: expected Partially aligned preferred stack, "
                f"got {pref.get('alignment_status')}"
            )

        return errs

    return run_case("Student Information Portal", payload, checks)


def test_mobile_event_app() -> list[str]:
    """Mobile-first: notifications, maps, auth, CRUD must not yield Laravel."""
    payload = {
        "project_name": "Campus Event Mobile App",
        "project_type": "Mobile Application",
        "selected_features": [
            "Notifications",
            "Maps / Location",
            "Authentication",
            "CRUD Operations",
        ],
        "project_goal": (
            "Mobile app for campus events with maps, push notifications, and user accounts"
        ),
        "team_size": 3,
        "complexity": "Medium",
        "timeline": "Short",
        "requirements_stability": "Changing",
        "stakeholder_involvement": "High",
        "preferred_platform": "Mobile",
        "development_experience": "Intermediate",
        "scalability_needs": "Medium",
        "performance_requirements": "Moderate",
        "security_requirements": "Moderate",
        "budget_constraints": "Low",
        "maintenance_expectations": "Medium",
        "deployment_preference": "Cloud deployment",
    }

    def checks(data: dict[str, Any], name: str) -> list[str]:
        errs: list[str] = []
        lang, fw, sdlc = (
            data["recommended_language"],
            data["recommended_framework"],
            data["recommended_sdlc"],
        )
        if lang != "Dart" or fw != "Flutter":
            errs.append(f"{name}: expected Dart + Flutter, got {lang} + {fw}")
        if sdlc not in ("Agile", "Prototype Model"):
            errs.append(f"{name}: expected Agile or Prototype Model, got {sdlc}")
        if lang == "PHP" or fw == "Laravel":
            errs.append(f"{name}: must not return PHP + Laravel for mobile-first app")
        return errs

    return run_case("Mobile Event App", payload, checks)


def test_mobile() -> list[str]:
    payload = {
        "project_name": "FieldSync Mobile",
        "project_type": "Mobile Application",
        "selected_features": ["Authentication", "Offline-first Mode"],
        "project_goal": "Cross-platform mobile application for iOS and Android",
        "team_size": 2,
        "complexity": "Medium",
        "timeline": "Short",
        "requirements_stability": "Somewhat Changing",
        "stakeholder_involvement": "High",
        "preferred_platform": "Cross-platform",
        "development_experience": "Intermediate",
        "scalability_needs": "Medium",
        "performance_requirements": "Moderate",
        "security_requirements": "Moderate",
        "budget_constraints": "Flexible",
        "maintenance_expectations": "Production-ready system",
        "deployment_preference": "Cloud deployment",
    }

    def checks(data: dict[str, Any], name: str) -> list[str]:
        errs: list[str] = []
        if data["recommended_language"] != "Dart" or data["recommended_framework"] != "Flutter":
            errs.append(
                f"{name}: expected Dart + Flutter, got "
                f"{data['recommended_language']} + {data['recommended_framework']}"
            )
        if data["recommended_sdlc"] not in ("Agile", "Prototype Model"):
            errs.append(f"{name}: expected Agile or Prototype Model SDLC")
        return errs

    return run_case("Mobile cross-platform app", payload, checks)


def test_ai() -> list[str]:
    payload = {
        "project_name": "Insight Bot",
        "project_type": "AI / Machine Learning Project",
        "selected_features": ["AI / ML Features", "Chat / Messaging", "API / Integrations"],
        "project_goal": "Build a recommendation chatbot with analytics API",
        "team_size": 4,
        "complexity": "High",
        "timeline": "3–4 months",
        "requirements_stability": "Frequently Changing",
        "stakeholder_involvement": "High",
        "preferred_platform": "Web",
        "development_experience": "Intermediate",
        "scalability_needs": "Expected to grow fast",
        "performance_requirements": "High",
        "security_requirements": "Sensitive user data",
        "budget_constraints": "Flexible",
        "maintenance_expectations": "Long-term maintainable project",
        "deployment_preference": "Cloud deployment",
    }

    def checks(data: dict[str, Any], name: str) -> list[str]:
        errs: list[str] = []
        if data["recommended_language"] != "Python":
            errs.append(f"{name}: expected Python for AI project")
        if data["recommended_framework"] not in ("FastAPI", "Django", "Flask"):
            errs.append(f"{name}: expected Python API/web framework")
        if data["recommended_sdlc"] not in ("Iterative", "Agile", "Spiral"):
            errs.append(f"{name}: expected iterative/agile/spiral SDLC")
        return errs

    return run_case("AI/chatbot project", payload, checks)


def test_backend_api() -> list[str]:
    payload = {
        "project_name": "Integration Hub API",
        "project_type": "Backend System",
        "selected_features": ["API / Integrations", "Authentication"],
        "project_goal": "Backend API with authentication, high scalability, and cloud deployment",
        "team_size": 5,
        "complexity": "High",
        "timeline": "3–4 months",
        "requirements_stability": "Somewhat Changing",
        "stakeholder_involvement": "Medium",
        "preferred_platform": "Backend/API",
        "development_experience": "Advanced",
        "scalability_needs": "Expected to grow fast",
        "performance_requirements": "High",
        "security_requirements": "High",
        "budget_constraints": "Flexible",
        "maintenance_expectations": "Production-ready system",
        "deployment_preference": "Cloud deployment",
    }

    def checks(data: dict[str, Any], name: str) -> list[str]:
        errs: list[str] = []
        fw = data["recommended_framework"]
        if fw in ("React", "Vue", "Angular"):
            errs.append(
                f"{name}: frontend framework {fw} must not be primary backend stack"
            )
        if fw not in (
            "FastAPI",
            "Express.js",
            "NestJS",
            "Spring Boot",
            "ASP.NET Core",
            "Laravel",
            "Django",
            "Flask",
        ):
            errs.append(f"{name}: expected backend/API framework, got {fw}")
        return errs

    return run_case("Backend API System", payload, checks)


def test_backend_api_alternative_sdlc_and_fit() -> list[str]:
    payload = {
        "project_name": "Integration Hub API",
        "project_type": "Backend System",
        "selected_features": ["API / Integrations", "Authentication"],
        "project_goal": "Backend API with authentication, high scalability, and cloud deployment",
        "team_size": 5,
        "complexity": "High",
        "timeline": "3–4 months",
        "requirements_stability": "Somewhat Changing",
        "stakeholder_involvement": "Medium",
        "preferred_platform": "Backend/API",
        "development_experience": "Advanced",
        "scalability_needs": "Expected to grow fast",
        "performance_requirements": "High",
        "security_requirements": "High",
        "budget_constraints": "Flexible",
        "maintenance_expectations": "Production-ready system",
        "deployment_preference": "Cloud deployment",
    }

    def checks(data: dict[str, Any], name: str) -> list[str]:
        errs: list[str] = []
        alts = data.get("alternative_technology_stacks", []) or []
        if len(alts) < 2:
            errs.append(f"{name}: expected at least 2 alternative stacks")
        frameworks = {a.get("framework") for a in alts}
        for expected in ("NestJS", "ASP.NET Core", "Spring Boot"):
            if expected not in frameworks:
                errs.append(f"{name}: expected {expected} in alternatives")
        for alt in alts:
            if alt.get("sdlc") == "DevOps":
                errs.append(f"{name}: DevOps must not appear as alternative SDLC")
            if int(alt.get("fit_score", 0)) > 100:
                errs.append(f"{name}: raw fit_score leaked to UI field")
            if alt.get("fit_display") is None and alt.get("fit_percent") is None:
                errs.append(f"{name}: missing fit_display/fit_percent on alternative")
        labels = {
            (a.get("language"), a.get("framework"), a.get("sdlc")) for a in alts
        }
        for want in (
            ("TypeScript", "NestJS", "Scrum"),
            ("C#", "ASP.NET Core", "Spiral"),
            ("Java", "Spring Boot", "Spiral"),
        ):
            if want not in labels:
                errs.append(f"{name}: expected alternative stack {want}")
        return errs

    return run_case("Backend API alternative SDLC/fit", payload, checks)


def test_web_crud_student_portal() -> list[str]:
    """Web CRUD admin — Laravel/Django family; no Flutter/Tauri/C++."""
    payload = {
        "project_name": "Student Portal",
        "project_type": "Web Application",
        "selected_features": [
            "Authentication",
            "CRUD Operations",
            "Admin Dashboard",
            "Reports / Analytics",
        ],
        "project_goal": "Web student portal with admin dashboard and reports",
        "team_size": 3,
        "complexity": "Medium",
        "timeline": "Short",
        "requirements_stability": "Changing",
        "stakeholder_involvement": "High",
        "preferred_platform": "Web",
        "development_experience": "Beginner",
        "scalability_needs": "Medium user base",
        "performance_requirements": "Moderate",
        "security_requirements": "Moderate",
        "budget_constraints": "Limited",
        "maintenance_expectations": "Medium",
        "deployment_preference": "Cloud deployment",
    }

    def checks(data: dict[str, Any], name: str) -> list[str]:
        errs: list[str] = []
        stack = (data["recommended_language"], data["recommended_framework"])
        allowed = {
            ("PHP", "Laravel"),
            ("Python", "Django"),
        }
        if stack not in allowed:
            errs.append(f"{name}: expected PHP+Laravel or Python+Django, got {stack[0]}+{stack[1]}")
        if data["recommended_framework"] in ("Flutter", "Tauri") or data["recommended_language"] in (
            "C",
            "C++",
            "Rust",
        ):
            errs.append(f"{name}: must not return mobile/desktop/systems primary stack")
        return errs

    return run_case("Web CRUD Student Portal", payload, checks)


def test_enterprise_security() -> list[str]:
    payload = {
        "project_name": "SecureCore Enterprise",
        "project_type": "Information System",
        "selected_features": ["Authentication", "Role-based Access", "Reports / Analytics"],
        "project_goal": "Enterprise system with high security and scalable architecture",
        "team_size": 12,
        "complexity": "High",
        "timeline": "More than 6 months",
        "requirements_stability": "Very Stable",
        "stakeholder_involvement": "Medium",
        "preferred_platform": "Backend/API",
        "development_experience": "Advanced",
        "scalability_needs": "Large user base",
        "performance_requirements": "High",
        "security_requirements": "Payment or financial data",
        "budget_constraints": "Not a concern",
        "maintenance_expectations": "Production-ready system",
        "deployment_preference": "Docker/containerized",
    }

    def checks(data: dict[str, Any], name: str) -> list[str]:
        errs: list[str] = []
        lang = data["recommended_language"]
        fw = data["recommended_framework"]
        if lang not in ("Java", "C#") or fw not in ("Spring Boot", "ASP.NET Core"):
            errs.append(f"{name}: expected Java/Spring or C#/ASP.NET, got {lang}+{fw}")
        if data["recommended_sdlc"] not in (
            "Spiral",
            "Scrum",
            "Waterfall",
            "V-Model",
            "DevOps",
        ):
            errs.append(f"{name}: expected enterprise SDLC model")
        return errs

    return run_case("Enterprise high-security", payload, checks)


def test_embedded() -> list[str]:
    payload = {
        "project_name": "Firmware Controller",
        "project_type": "Embedded System",
        "selected_features": ["API / Integrations"],
        "project_goal": "Firmware and low-level systems programming for hardware device",
        "team_size": 4,
        "complexity": "High",
        "timeline": "5–6 months",
        "requirements_stability": "Very Stable",
        "stakeholder_involvement": "Low",
        "preferred_platform": "Desktop",
        "development_experience": "Advanced",
        "scalability_needs": "Small user base",
        "performance_requirements": "High",
        "security_requirements": "High",
        "budget_constraints": "Flexible",
        "maintenance_expectations": "Long-term maintainable project",
        "deployment_preference": "Local only",
    }

    def checks(data: dict[str, Any], name: str) -> list[str]:
        errs: list[str] = []
        if data["recommended_language"] not in ("C", "C++", "Rust"):
            errs.append(f"{name}: expected C/C++/Rust for embedded")
        if data["recommended_sdlc"] not in (
            "V-Model",
            "Spiral",
            "Waterfall",
            "Iterative",
        ):
            errs.append(f"{name}: expected systems-oriented SDLC")
        return errs

    return run_case("Embedded/systems project", payload, checks)


def test_desktop_tauri() -> list[str]:
    payload = {
        "project_name": "DeskShell",
        "project_type": "Desktop Application",
        "selected_features": ["Authentication", "Offline-first Mode"],
        "project_goal": "Cross-platform lightweight secure desktop application",
        "team_size": 3,
        "complexity": "Medium",
        "timeline": "3–4 months",
        "requirements_stability": "Mostly Stable",
        "stakeholder_involvement": "Medium",
        "preferred_platform": "Desktop",
        "development_experience": "Advanced",
        "scalability_needs": "Medium",
        "performance_requirements": "High",
        "security_requirements": "High",
        "budget_constraints": "Flexible",
        "maintenance_expectations": "Long-term maintainable project",
        "deployment_preference": "Cloud deployment",
    }

    def checks(data: dict[str, Any], name: str) -> list[str]:
        errs: list[str] = []
        stack = (data["recommended_language"], data["recommended_framework"])
        if stack not in (("Rust", "Tauri"), ("TypeScript", "Tauri")):
            errs.append(f"{name}: expected Rust/TypeScript + Tauri, got {stack[0]}+{stack[1]}")
        return errs

    return run_case("Cross-platform desktop app", payload, checks)


def test_database_records() -> list[str]:
    payload = {
        "project_name": "Records Portal",
        "project_type": "Web Application",
        "selected_features": ["CRUD Operations", "Reports / Analytics", "Role-based Access"],
        "project_goal": "Web-based records and reporting management system with SQL queries",
        "team_size": 5,
        "complexity": "Medium",
        "timeline": "3–4 months",
        "requirements_stability": "Mostly Stable",
        "stakeholder_involvement": "Medium",
        "preferred_platform": "Web",
        "development_experience": "Intermediate",
        "scalability_needs": "Medium",
        "performance_requirements": "Moderate",
        "security_requirements": "Moderate",
        "budget_constraints": "Limited",
        "maintenance_expectations": "Long-term maintainable project",
        "deployment_preference": "Shared hosting",
    }

    def checks(data: dict[str, Any], name: str) -> list[str]:
        errs: list[str] = []
        if data["recommended_language"] == "SQL":
            errs.append(f"{name}: SQL must not be primary for general web records system")
        if not is_compatible(data["recommended_language"], data["recommended_framework"]):
            errs.append(f"{name}: incompatible primary stack")
        sql_score = data.get("language_scores", {}).get("SQL", 0)
        if sql_score <= 0:
            errs.append(f"{name}: SQL should still score as supporting technology")
        return errs

    return run_case("Database-heavy records system", payload, checks)


def test_incompatible_preferred() -> list[str]:
    payload = {
        "project_name": "Bad Pair Preference",
        "project_type": "Web Application",
        "selected_features": ["Authentication", "CRUD Operations"],
        "project_goal": "Simple web portal",
        "team_size": 2,
        "complexity": "Low",
        "timeline": "Short",
        "requirements_stability": "Changing",
        "stakeholder_involvement": "Medium",
        "preferred_platform": "Web",
        "development_experience": "Beginner",
        "scalability_needs": "Medium",
        "performance_requirements": "Basic",
        "security_requirements": "Basic",
        "budget_constraints": "Limited",
        "maintenance_expectations": "Short-term school project",
        "deployment_preference": "Cloud deployment",
        "user_preferred_language": "Java",
        "user_preferred_framework": "Laravel",
        "user_preferred_sdlc": "Agile",
    }

    def checks(data: dict[str, Any], name: str) -> list[str]:
        errs: list[str] = []
        pref = data.get("user_preferred_stack", {})
        if pref.get("is_compatible") is not False:
            errs.append(f"{name}: user_preferred_stack.is_compatible should be False")
        summary = pref.get("comparison_summary", "").lower()
        if "php" not in summary and "incompatible" not in summary:
            errs.append(f"{name}: comparison should explain Laravel requires PHP")
        why = " ".join(
            w.get("technology_or_stack", "") + w.get("reason", "")
            for w in data.get("why_not_this", [])
        ).lower()
        if "laravel" not in why and "php" not in why:
            errs.append(f"{name}: why_not_this should mention Java + Laravel incompatibility")
        return errs

    return run_case("Incompatible user preferred stack", payload, checks)


def test_confidence_varies_across_project_types() -> list[str]:
    from app.controllers.recommendation_controller import (
        generate_recommendation_from_request,
    )

    payloads = [
        {
            "project_name": "Student Portal",
            "project_type": "Web Application",
            "selected_features": ["Authentication", "CRUD Operations", "Admin Dashboard"],
            "project_goal": "Web student portal",
            "team_size": 3,
            "complexity": "Medium",
            "timeline": "Short",
            "requirements_stability": "Changing",
            "stakeholder_involvement": "High",
            "preferred_platform": "Web",
            "development_experience": "Beginner",
            "scalability_needs": "Medium",
            "performance_requirements": "Moderate",
            "security_requirements": "Moderate",
            "budget_constraints": "Limited",
            "maintenance_expectations": "Medium",
            "deployment_preference": "Cloud deployment",
        },
        {
            "project_name": "Campus Event Mobile App",
            "project_type": "Mobile Application",
            "selected_features": ["Notifications", "Maps / Location", "Authentication"],
            "project_goal": "Mobile campus events app",
            "team_size": 3,
            "complexity": "Medium",
            "timeline": "Short",
            "requirements_stability": "Changing",
            "stakeholder_involvement": "High",
            "preferred_platform": "Mobile",
            "development_experience": "Intermediate",
            "scalability_needs": "Medium",
            "performance_requirements": "Moderate",
            "security_requirements": "Moderate",
            "budget_constraints": "Low",
            "maintenance_expectations": "Medium",
            "deployment_preference": "Cloud deployment",
        },
        {
            "project_name": "AI Student Support Chatbot",
            "project_type": "AI / Machine Learning Project",
            "selected_features": ["AI / ML Features", "Chat / Messaging"],
            "project_goal": "Chatbot with prediction and recommendation engine",
            "team_size": 4,
            "complexity": "High",
            "timeline": "3–4 months",
            "requirements_stability": "Frequently Changing",
            "stakeholder_involvement": "High",
            "preferred_platform": "Web",
            "development_experience": "Intermediate",
            "scalability_needs": "Expected to grow fast",
            "performance_requirements": "High",
            "security_requirements": "Moderate",
            "budget_constraints": "Flexible",
            "maintenance_expectations": "Long-term maintainable project",
            "deployment_preference": "Cloud deployment",
        },
        {
            "project_name": "Hospital Patient Management System",
            "project_type": "Web Application",
            "selected_features": [
                "Authentication",
                "CRUD Operations",
                "Admin Dashboard",
                "Reports / Analytics",
            ],
            "project_goal": "Hospital system with high security and scalability",
            "team_size": 12,
            "complexity": "High",
            "timeline": "More than 6 months",
            "requirements_stability": "Fixed",
            "stakeholder_involvement": "Medium",
            "preferred_platform": "Web",
            "development_experience": "Advanced",
            "scalability_needs": "Large user base",
            "performance_requirements": "High",
            "security_requirements": "High",
            "budget_constraints": "High",
            "maintenance_expectations": "Production-ready system",
            "deployment_preference": "Cloud deployment",
        },
        {
            "project_name": "Offline Inventory Desktop App",
            "project_type": "Desktop Application",
            "selected_features": ["Authentication", "Offline-first Mode"],
            "project_goal": "Cross-platform lightweight secure desktop inventory",
            "team_size": 3,
            "complexity": "Medium",
            "timeline": "3–4 months",
            "requirements_stability": "Mostly Stable",
            "stakeholder_involvement": "Medium",
            "preferred_platform": "Desktop",
            "development_experience": "Advanced",
            "scalability_needs": "Medium",
            "performance_requirements": "High",
            "security_requirements": "High",
            "budget_constraints": "Flexible",
            "maintenance_expectations": "Long-term maintainable project",
            "deployment_preference": "Cloud deployment",
        },
    ]

    confidences: list[int] = []
    errs: list[str] = []
    for payload in payloads:
        r = generate_recommendation_from_request(payload)
        if not r.get("success"):
            return ["confidence_variety: engine returned success=False"]
        score = int(r["data"]["confidence_score"])
        confidences.append(score)
        if score < 60 or score > 95:
            errs.append(f"confidence_variety: score {score} outside 60–95")
        if score in (99, 100):
            errs.append(f"confidence_variety: score must not be {score}")

    if len(set(confidences)) <= 1:
        errs.append(
            f"confidence_variety: all confidence scores identical: {confidences}"
        )
    return errs


def test_hospital_sdlc_not_devops_by_default() -> list[str]:
    payload = {
        "project_name": "Hospital Patient Management System",
        "project_type": "Web Application",
        "selected_features": [
            "Authentication",
            "CRUD Operations",
            "Admin Dashboard",
            "Reports / Analytics",
        ],
        "project_goal": (
            "Enterprise hospital patient management with high security, "
            "high performance, and cloud deployment"
        ),
        "team_size": 12,
        "complexity": "High",
        "timeline": "More than 6 months",
        "requirements_stability": "Fixed",
        "stakeholder_involvement": "Medium",
        "preferred_platform": "Web",
        "development_experience": "Advanced",
        "scalability_needs": "Large user base",
        "performance_requirements": "High",
        "security_requirements": "High",
        "budget_constraints": "High",
        "maintenance_expectations": "Production-ready system",
        "deployment_preference": "Cloud deployment",
    }

    def checks(data: dict[str, Any], name: str) -> list[str]:
        errs: list[str] = []
        sdlc = data["recommended_sdlc"]
        allowed = {
            "Spiral",
            "V-Model",
            "Waterfall",
            "Scrum",
            "Incremental",
            "Feature-Driven Development (FDD)",
        }
        if sdlc == "DevOps":
            errs.append(f"{name}: DevOps must not be primary SDLC for hospital system")
        if sdlc not in allowed:
            errs.append(
                f"{name}: expected enterprise governance SDLC, got {sdlc}"
            )
        return errs

    return run_case("Hospital SDLC not DevOps", payload, checks)


def test_new_confidence_not_overwritten() -> list[str]:
    payload = {
        "project_name": "Student Information Portal",
        "project_type": "Web Application",
        "selected_features": [
            "Authentication",
            "CRUD Operations",
            "Admin Dashboard",
            "Reports / Analytics",
        ],
        "project_goal": "Web student portal",
        "team_size": 3,
        "complexity": "Medium",
        "timeline": "Short",
        "requirements_stability": "Changing",
        "stakeholder_involvement": "High",
        "preferred_platform": "Web",
        "development_experience": "Beginner",
        "scalability_needs": "Medium",
        "performance_requirements": "Medium",
        "security_requirements": "Medium",
        "budget_constraints": "Low",
        "maintenance_expectations": "Medium",
        "deployment_preference": "Cloud deployment",
        "user_preferred_language": "PHP",
        "user_preferred_framework": "Laravel",
        "user_preferred_sdlc": "Waterfall",
    }

    def checks(data: dict[str, Any], name: str) -> list[str]:
        errs: list[str] = []
        top = int(data["confidence_score"])
        saved = data.get("saved_recommendation", {})
        saved_conf = int(saved.get("confidence", -1))
        if top != saved_conf:
            errs.append(
                f"{name}: confidence_score {top} != saved_recommendation.confidence {saved_conf}"
            )
        return errs

    return run_case("Confidence not overwritten in saved payload", payload, checks)


def test_recommendation_variety() -> list[str]:
    """Across scenarios, recommendations must not all be identical."""
    from app.controllers.recommendation_controller import (
        generate_recommendation_from_request,
    )

    scenarios = [
        {
            "project_name": "Portal",
            "project_type": "Web Application",
            "selected_features": ["CRUD Operations", "Authentication"],
            "project_goal": "Web admin portal",
            "team_size": 3,
            "complexity": "Medium",
            "timeline": "Short",
            "requirements_stability": "Changing",
            "stakeholder_involvement": "High",
            "preferred_platform": "Web",
            "development_experience": "Beginner",
            "scalability_needs": "Medium",
            "performance_requirements": "Medium",
            "security_requirements": "Medium",
            "budget_constraints": "Low",
            "maintenance_expectations": "Medium",
            "deployment_preference": "Cloud deployment",
        },
        {
            "project_name": "Mobile App",
            "project_type": "Mobile Application",
            "selected_features": ["Notifications", "Authentication"],
            "project_goal": "Mobile application",
            "team_size": 2,
            "complexity": "Medium",
            "timeline": "Short",
            "requirements_stability": "Changing",
            "stakeholder_involvement": "High",
            "preferred_platform": "Mobile",
            "development_experience": "Intermediate",
            "scalability_needs": "Medium",
            "performance_requirements": "Moderate",
            "security_requirements": "Moderate",
            "budget_constraints": "Low",
            "maintenance_expectations": "Medium",
            "deployment_preference": "Cloud deployment",
        },
        {
            "project_name": "API",
            "project_type": "Backend System",
            "selected_features": ["API / Integrations", "Authentication"],
            "project_goal": "Backend API microservice",
            "team_size": 4,
            "complexity": "High",
            "timeline": "3–4 months",
            "requirements_stability": "Somewhat Changing",
            "stakeholder_involvement": "Medium",
            "preferred_platform": "Backend/API",
            "development_experience": "Advanced",
            "scalability_needs": "Expected to grow fast",
            "performance_requirements": "High",
            "security_requirements": "High",
            "budget_constraints": "Flexible",
            "maintenance_expectations": "Production-ready system",
            "deployment_preference": "Cloud deployment",
        },
        {
            "project_name": "Desktop",
            "project_type": "Desktop Application",
            "selected_features": ["Authentication"],
            "project_goal": "Cross-platform lightweight secure desktop application",
            "team_size": 3,
            "complexity": "Medium",
            "timeline": "3–4 months",
            "requirements_stability": "Mostly Stable",
            "stakeholder_involvement": "Medium",
            "preferred_platform": "Desktop",
            "development_experience": "Advanced",
            "scalability_needs": "Medium",
            "performance_requirements": "High",
            "security_requirements": "High",
            "budget_constraints": "Flexible",
            "maintenance_expectations": "Long-term maintainable project",
            "deployment_preference": "Cloud deployment",
        },
        {
            "project_name": "Firmware",
            "project_type": "Embedded System",
            "selected_features": [],
            "project_goal": "Firmware and low-level embedded hardware control",
            "team_size": 4,
            "complexity": "High",
            "timeline": "5–6 months",
            "requirements_stability": "Very Stable",
            "stakeholder_involvement": "Low",
            "preferred_platform": "Desktop",
            "development_experience": "Advanced",
            "scalability_needs": "Small user base",
            "performance_requirements": "High",
            "security_requirements": "High",
            "budget_constraints": "Flexible",
            "maintenance_expectations": "Long-term maintainable project",
            "deployment_preference": "Local only",
        },
    ]

    stacks: list[tuple[str, str, str]] = []
    frameworks: set[str] = set()
    for payload in scenarios:
        r = generate_recommendation_from_request(payload)
        if not r.get("success"):
            return ["variety: engine returned success=False"]
        d = r["data"]
        stacks.append(
            (d["recommended_language"], d["recommended_framework"], d["recommended_sdlc"])
        )
        frameworks.add(d["recommended_framework"])

    errs: list[str] = []
    if len(set(stacks)) < 3:
        errs.append(
            f"variety: expected diverse stacks across scenarios, got {stacks}"
        )
    if "Laravel" not in frameworks and "Flutter" not in frameworks:
        errs.append("variety: expected at least Laravel and Flutter among results")
    backend_fws = frameworks & {
        "FastAPI",
        "NestJS",
        "Express.js",
        "Spring Boot",
        "ASP.NET Core",
    }
    if not backend_fws:
        errs.append("variety: expected at least one backend/API framework result")
    if "Tauri" not in frameworks and not any(s[0] in ("C", "C++", "Rust") for s in stacks):
        errs.append("variety: expected Tauri or systems language for desktop/embedded scenario")
    return errs


def main() -> int:
    cases = [
        test_web_crud_student_portal,
        test_student_portal,
        test_mobile_event_app,
        test_mobile,
        test_backend_api,
        test_backend_api_alternative_sdlc_and_fit,
        test_ai,
        test_enterprise_security,
        test_embedded,
        test_desktop_tauri,
        test_database_records,
        test_incompatible_preferred,
        test_confidence_varies_across_project_types,
        test_hospital_sdlc_not_devops_by_default,
        test_new_confidence_not_overwritten,
        test_recommendation_variety,
    ]
    all_errors: list[str] = []
    print("StackWise Recommendation Engine — Phase 2.4 Tests\n")
    for fn in cases:
        print(f"Running {fn.__name__}...")
        errs = fn()
        if errs:
            all_errors.extend(errs)
            print(f"  FAIL ({len(errs)} errors)")
            for e in errs:
                print(f"    - {e}")
        else:
            print("  PASS")

    print("\n" + "=" * 50)
    if all_errors:
        print(f"FAILED: {len(all_errors)} error(s)")
        return 1
    print("All tests passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
