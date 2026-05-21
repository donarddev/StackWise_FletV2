"""Temporary Phase 2 test harness for the weighted recommendation engine.

Run from project root::

    python test_recommendation_engine.py

Does not import Flet, start the app, or connect to the database.
"""

from __future__ import annotations

import sys
from typing import Any

from app.controllers.recommendation_controller import generate_recommendation_from_request

# ---------------------------------------------------------------------------
# Language–framework compatibility (Phase 1 rules)
# ---------------------------------------------------------------------------

LANGUAGE_FRAMEWORK_COMPATIBILITY: dict[str, list[str]] = {
    "Python": ["FastAPI", "Django", "Flask"],
    "PHP": ["Laravel"],
    "JavaScript / TypeScript": ["Next.js", "React", "Express", "NestJS"],
    "Java": ["Spring Boot"],
    "C#": ["ASP.NET Core"],
    "Dart": ["Flutter"],
    "Kotlin": ["Android/Ktor"],
    "Swift": ["SwiftUI"],
    "Ruby": ["Rails"],
    "Go": ["Gin"],
    "Rust": ["Tauri"],
    "SQL": ["Database-focused stack"],
}

CONFIDENCE_LABELS = frozenset({"Very High", "High", "Moderate", "Low"})

DEFENSE_KEYWORDS = (
    "weighted multi-criteria decision matrix",
    "iso/iec 25010",
    "iso/iec/ieee 12207",
    "pmbok",
    "official documentation",
    "decision support",
)

# Expected logical winners per scenario (flexible sets for assertions)
EXPECTED: dict[str, dict[str, frozenset[str]]] = {
    "case_1": {
        "languages": frozenset({"PHP", "Python", "JavaScript / TypeScript"}),
        "frameworks": frozenset(
            {
                "Laravel",
                "Django",
                "FastAPI",
                "Flask",
                "Next.js",
                "React",
                "Express",
                "NestJS",
            }
        ),
        "sdlc": frozenset({"Agile", "Scrum", "Kanban", "Lean Startup", "Prototype", "XP"}),
    },
    "case_2": {
        "languages": frozenset({"Dart"}),
        "frameworks": frozenset({"Flutter"}),
        "sdlc": frozenset({"Agile", "Lean Startup", "Prototype", "Scrum", "Kanban"}),
    },
    "case_3": {
        "languages": frozenset({"Java", "C#"}),
        "frameworks": frozenset({"Spring Boot", "ASP.NET Core"}),
        "sdlc": frozenset(
            {"Spiral", "V-Model", "DevOps", "Iterative", "Waterfall", "FDD"}
        ),
    },
    "case_4": {
        "languages": frozenset({"Python"}),
        "frameworks": frozenset({"FastAPI", "Django", "Flask"}),
        "sdlc": frozenset({"Agile", "Iterative", "Kanban", "Scrum", "Lean Startup"}),
    },
    "case_5": {
        "languages": frozenset(
            {
                "PHP",
                "Python",
                "JavaScript / TypeScript",
                "Java",
                "C#",
                "Go",
                "Kotlin",
            }
        ),
        "frameworks": frozenset(
            {
                "Laravel",
                "Django",
                "FastAPI",
                "Flask",
                "Next.js",
                "React",
                "Express",
                "NestJS",
                "Spring Boot",
                "ASP.NET Core",
            }
        ),
        "sdlc": frozenset({"Waterfall", "V-Model", "Spiral", "FDD", "Incremental"}),
        "forbid_language": "SQL",
    },
    "case_6": {
        "languages": frozenset({"SQL"}),
        "frameworks": frozenset({"Database-focused stack"}),
        "sdlc": frozenset({"Waterfall", "V-Model", "Spiral", "FDD", "DevOps"}),
    },
}

TEST_CASES: list[dict[str, Any]] = [
    {
        "key": "case_1",
        "name": "Student Web App",
        "payload": {
            "project_name": "Student Information Portal",
            "project_type": "Web Application",
            "selected_features": ["Authentication", "CRUD Operations", "Admin Dashboard"],
            "project_goal": "Build a student information system with secure login and records",
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
            "maintenance_expectations": "Long-term maintainable project",
            "deployment_preference": "Cloud deployment",
        },
    },
    {
        "key": "case_2",
        "name": "Mobile Cross-Platform Offline App",
        "payload": {
            "project_name": "FieldSync Mobile",
            "project_type": "Mobile Application",
            "selected_features": ["Offline-first Mode", "Authentication", "Maps / Location"],
            "project_goal": "Cross-platform mobile app with offline sync for field workers",
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
        },
    },
    {
        "key": "case_3",
        "name": "Enterprise High-Security System",
        "payload": {
            "project_name": "SecureCore Enterprise",
            "project_type": "Information System",
            "selected_features": [
                "Authentication",
                "Role-based Access",
                "Reports / Analytics",
                "API / Integrations",
            ],
            "project_goal": "Enterprise system with high security and scalable architecture",
            "team_size": 12,
            "complexity": "High",
            "timeline": "More than 6 months",
            "requirements_stability": "Mostly Stable",
            "stakeholder_involvement": "Medium",
            "preferred_platform": "Backend/API",
            "development_experience": "Advanced",
            "scalability_needs": "Large user base",
            "performance_requirements": "High",
            "security_requirements": "Payment or financial data",
            "budget_constraints": "Not a concern",
            "maintenance_expectations": "Production-ready system",
            "deployment_preference": "Docker/containerized",
        },
    },
    {
        "key": "case_4",
        "name": "AI Data Dashboard with API",
        "payload": {
            "project_name": "InsightML Dashboard",
            "project_type": "AI / Machine Learning Project",
            "selected_features": [
                "AI / ML Features",
                "Reports / Analytics",
                "API / Integrations",
                "Admin Dashboard",
            ],
            "project_goal": "AI and data analytics dashboard with REST API for model serving",
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
        },
    },
    {
        "key": "case_5",
        "name": "Fixed-Requirement Documentation-Heavy Project",
        "payload": {
            "project_name": "GovRecords Compliance System",
            "project_type": "Information System",
            "selected_features": ["CRUD Operations", "Reports / Analytics", "Role-based Access"],
            "project_goal": (
                "Build a government compliance information system with records, "
                "reports, and user roles"
            ),
            "team_size": 8,
            "complexity": "High",
            "timeline": "5–6 months",
            "requirements_stability": "Very Stable",
            "stakeholder_involvement": "Low",
            "preferred_platform": "Web",
            "development_experience": "Advanced",
            "scalability_needs": "Medium user base",
            "performance_requirements": "Moderate",
            "security_requirements": "High",
            "budget_constraints": "Flexible",
            "maintenance_expectations": "Production-ready system",
            "deployment_preference": "Cloud deployment",
        },
    },
    {
        "key": "case_6",
        "name": "Database-Focused Records & Reporting System",
        "payload": {
            "project_name": "Compliance Records Warehouse",
            "project_type": "Records Management System",
            "selected_features": [
                "Records Management",
                "Query-heavy Reporting",
                "Reports / Analytics",
                "Database Management",
            ],
            "project_goal": (
                "Build a database-centered compliance records and reporting system."
            ),
            "team_size": 6,
            "complexity": "High",
            "timeline": "5–6 months",
            "requirements_stability": "Very Stable",
            "stakeholder_involvement": "Medium",
            "preferred_platform": "Web",
            "development_experience": "Advanced",
            "scalability_needs": "Large user base",
            "performance_requirements": "High",
            "security_requirements": "High",
            "budget_constraints": "Flexible",
            "maintenance_expectations": "Production-ready system",
            "deployment_preference": "Cloud deployment",
        },
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _top_scores(scores: dict[str, float], limit: int = 5) -> list[tuple[str, float]]:
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)[:limit]


def _format_scores(scores: dict[str, float], limit: int = 5) -> str:
    lines = [f"  {name}: {score:.1f}" for name, score in _top_scores(scores, limit)]
    return "\n".join(lines) if lines else "  (none)"


def _format_alternatives(alternatives: list[dict[str, Any]]) -> str:
    if not alternatives:
        return "  (none)"
    return "\n".join(
        f"  - {a.get('name')}: {a.get('score')} — {a.get('reason', '')}"
        for a in alternatives
    )


def _format_list(items: list[str], indent: str = "  ") -> str:
    if not items:
        return f"{indent}(none)"
    return "\n".join(f"{indent}- {item}" for item in items)


def _format_roadmap(roadmap: list[dict[str, str]]) -> str:
    if not roadmap:
        return "  (none)"
    lines: list[str] = []
    for step in roadmap:
        phase = step.get("phase", "?")
        title = step.get("title", "Step")
        desc = step.get("description", "")
        lines.append(f"  {phase}. {title}")
        lines.append(f"     {desc}")
    return "\n".join(lines)


def check_framework_compatibility(language: str, framework: str) -> str | None:
    allowed = LANGUAGE_FRAMEWORK_COMPATIBILITY.get(language)
    if allowed is None:
        return f"Unknown language for compatibility check: {language}"
    if framework not in allowed:
        return (
            "ERROR: Incompatible recommendation detected:\n"
            f"Language: {language}\n"
            f"Framework: {framework}"
        )
    return None


def check_defense_explanation(text: str) -> list[str]:
    warnings: list[str] = []
    lower = text.lower()
    for keyword in DEFENSE_KEYWORDS:
        if keyword not in lower:
            warnings.append(f"Defense explanation missing keyword: '{keyword}'")
    if "absolute correctness" not in lower and "decision support" not in lower:
        warnings.append(
            "Defense explanation should state decision-support, not absolute correctness."
        )
    return warnings


def assert_basic_result(result: dict[str, Any], case_name: str) -> tuple[dict[str, Any], list[str]]:
    """Return (data, errors)."""
    errors: list[str] = []

    if not result.get("success"):
        errors.append(f"{case_name}: success is False — {result.get('error', 'unknown error')}")
        return {}, errors

    data = result.get("data")
    if not data or not isinstance(data, dict):
        errors.append(f"{case_name}: data is missing or not a dict")
        return {}, errors

    lang = data.get("recommended_language", "")
    fw = data.get("recommended_framework", "")
    sdlc = data.get("recommended_sdlc", "")

    if not lang:
        errors.append(f"{case_name}: recommended_language is empty")
    if not fw:
        errors.append(f"{case_name}: recommended_framework is empty")
    if not sdlc:
        errors.append(f"{case_name}: recommended_sdlc is empty")

    score = data.get("confidence_score", -1)
    try:
        score_f = float(score)
    except (TypeError, ValueError):
        score_f = -1
    if not (0 <= score_f <= 100):
        errors.append(f"{case_name}: confidence_score {score} not in 0–100")

    label = data.get("confidence_label", "")
    if label not in CONFIDENCE_LABELS:
        errors.append(f"{case_name}: invalid confidence_label '{label}'")

    compat_err = check_framework_compatibility(lang, fw)
    if compat_err:
        errors.append(compat_err)

    for alt_key, winner_field in (
        ("alternative_languages", "recommended_language"),
        ("alternative_frameworks", "recommended_framework"),
        ("alternative_sdlc_models", "recommended_sdlc"),
    ):
        winner = data.get(winner_field, "")
        for alt in data.get(alt_key, []) or []:
            if alt.get("name") == winner:
                errors.append(
                    f"{case_name}: alternative '{alt_key}' includes winner '{winner}'"
                )

    for field in ("defense_explanation", "scoring_basis", "validation_note"):
        if not data.get(field):
            errors.append(f"{case_name}: missing '{field}'")

    if case_name == "Fixed-Requirement Documentation-Heavy Project":
        assert lang != "SQL", (
            f"{case_name}: SQL must not be the primary language for a general "
            "Information System"
        )

    return data, errors


def assert_logical_expectation(
    data: dict[str, Any], case_key: str, case_name: str
) -> tuple[list[str], list[str]]:
    """Return (warnings, hard_errors) for logical expectation checks."""
    warnings: list[str] = []
    errors: list[str] = []
    expected = EXPECTED.get(case_key, {})
    lang = data.get("recommended_language", "")
    fw = data.get("recommended_framework", "")
    sdlc = data.get("recommended_sdlc", "")

    if expected.get("languages") and lang not in expected["languages"]:
        warnings.append(
            f"{case_name}: language '{lang}' not in expected set "
            f"{sorted(expected['languages'])}"
        )
    if expected.get("frameworks") and fw not in expected["frameworks"]:
        warnings.append(
            f"{case_name}: framework '{fw}' not in expected set "
            f"{sorted(expected['frameworks'])}"
        )
    if expected.get("sdlc") and sdlc not in expected["sdlc"]:
        warnings.append(
            f"{case_name}: SDLC '{sdlc}' not in expected set {sorted(expected['sdlc'])}"
        )

    forbidden = expected.get("forbid_language")
    if forbidden and lang == forbidden:
        errors.append(
            f"{case_name}: '{forbidden}' must not be the primary language for a general "
            "application information system"
        )

    return warnings, errors


def print_case_output(case_name: str, data: dict[str, Any], warnings: list[str]) -> None:
    width = 50
    print("=" * width)
    print(f"TEST CASE: {case_name}")
    print("=" * width)

    score = float(data.get("confidence_score", 0))
    label = data.get("confidence_label", "")
    print(f"Recommended Language: {data.get('recommended_language')}")
    print(f"Recommended Framework: {data.get('recommended_framework')}")
    print(f"Recommended SDLC: {data.get('recommended_sdlc')}")
    print(f"Confidence: {score:.1f}% {label}")
    print()

    print("Top Language Scores:")
    print(_format_scores(data.get("language_scores", {})))
    print()
    print("Top Framework Scores:")
    print(_format_scores(data.get("framework_scores", {})))
    print()
    print("Top SDLC Scores:")
    print(_format_scores(data.get("sdlc_scores", {})))
    print()

    print("Alternative Languages:")
    print(_format_alternatives(data.get("alternative_languages", [])))
    print()
    print("Alternative Frameworks:")
    print(_format_alternatives(data.get("alternative_frameworks", [])))
    print()
    print("Alternative SDLC Models:")
    print(_format_alternatives(data.get("alternative_sdlc_models", [])))
    print()

    print("Explanation:")
    print(data.get("explanation", "(none)"))
    print()
    print("Risks:")
    print(_format_list(data.get("risks", [])))
    print()
    print("Skill Gaps:")
    print(_format_list(data.get("skill_gaps", [])))
    print()
    print("Roadmap:")
    print(_format_roadmap(data.get("roadmap", [])))
    print()
    print("Scoring Basis:")
    print(f"  {data.get('scoring_basis', '(none)')}")
    print()
    print("Defense Explanation:")
    print(f"  {data.get('defense_explanation', '(none)')}")
    print()
    print("Validation Note:")
    print(f"  {data.get('validation_note', '(none)')}")
    print()

    defense_warnings = check_defense_explanation(data.get("defense_explanation", ""))
    all_warnings = warnings + defense_warnings
    if all_warnings:
        print("WARNINGS:")
        for w in all_warnings:
            print(f"  ! {w}")
        print()


def run_all_tests() -> int:
    """Run all scenarios; return exit code (0 = pass, 1 = fail)."""
    print("StackWise Recommendation Engine — Phase 2 Test Harness")
    print("Method: Weighted Multi-Criteria Decision Matrix (no Flet / no DB)\n")

    all_errors: list[str] = []
    all_warnings: list[str] = []
    passed = 0

    for index, case in enumerate(TEST_CASES, start=1):
        case_name = case["name"]
        print(f"\n>>> Running Test Case {index}: {case_name}...\n")

        result = generate_recommendation_from_request(case["payload"])
        data, errors = assert_basic_result(result, case_name)
        all_errors.extend(errors)

        if data:
            logical_warnings, logical_errors = assert_logical_expectation(
                data, case["key"], case_name
            )
            all_warnings.extend(logical_warnings)
            all_errors.extend(logical_errors)
            errors.extend(logical_errors)
            print_case_output(case_name, data, logical_warnings + logical_errors)
            if not errors:
                passed += 1
                print(f"PASSED: {case_name}\n")
            else:
                print(f"FAILED: {case_name}\n")
                for err in errors:
                    print(f"  ERROR: {err}\n")
        else:
            print(f"FAILED: {case_name} — no data returned.\n")
            for err in errors:
                print(f"  ERROR: {err}\n")

    # Summary
    print("=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Test cases run: {len(TEST_CASES)}")
    print(f"Passed (hard checks): {passed}/{len(TEST_CASES)}")
    print(f"Hard errors: {len(all_errors)}")
    print(f"Warnings (logical / defense keywords): {len(all_warnings)}")

    if all_errors:
        print("\nFAILED — hard assertion errors:")
        for err in all_errors:
            print(f"  - {err}")
    else:
        print("\nAll hard checks passed.")

    if all_warnings:
        print("\nWarnings (review for defense documentation):")
        for w in all_warnings:
            print(f"  - {w}")

    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(run_all_tests())
