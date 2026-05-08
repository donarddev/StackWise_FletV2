"""Knowledge base of technology profiles.

This module defines typed profiles for programming languages, frameworks, and
SDLC models. The recommendation engine scores these profiles against the
user's project request along several weighted dimensions.

Keep this module data-only — no scoring logic here, just facts about each
technology. Scoring happens in ``recommendation_service.py``.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class LanguageProfile:
    name: str
    summary: str

    # Higher is better, on a 0–10 scale unless noted
    learning_curve_friendliness: int  # 10 = easy to learn
    development_speed: int            # 10 = ships fast
    runtime_performance: int          # 10 = very fast
    type_safety: int                  # 10 = strongly typed
    ecosystem_breadth: int            # 10 = huge ecosystem
    scalability_ceiling: int          # 10 = scales massively
    security_maturity: int            # 10 = great built-in security story

    great_for_project_types: tuple[str, ...]
    great_for_platforms: tuple[str, ...]
    typical_frameworks: tuple[str, ...]


@dataclass(frozen=True)
class FrameworkProfile:
    name: str
    language: str
    summary: str

    development_speed: int
    learning_curve_friendliness: int
    scalability_ceiling: int
    security_maturity: int
    ecosystem_breadth: int

    great_for_project_types: tuple[str, ...]
    great_for_platforms: tuple[str, ...]


@dataclass(frozen=True)
class SDLCProfile:
    name: str
    summary: str

    suits_small_team: int       # 0–10
    suits_large_team: int       # 0–10
    suits_changing_reqs: int    # 0–10 (agility)
    suits_fixed_scope: int      # 0–10
    suits_fast_timeline: int    # 0–10
    overhead: int               # 0–10 (LOWER is better)
    risk_management: int        # 0–10

    great_for_goals: tuple[str, ...] = field(default_factory=tuple)


# ---------------------------------------------------------------------------
# Languages
# ---------------------------------------------------------------------------

LANGUAGES: list[LanguageProfile] = [
    LanguageProfile(
        name="Python",
        summary="Readable, batteries-included, excellent for AI/ML, data, scripting, and back-ends.",
        learning_curve_friendliness=10,
        development_speed=10,
        runtime_performance=5,
        type_safety=5,
        ecosystem_breadth=10,
        scalability_ceiling=8,
        security_maturity=8,
        great_for_project_types=(
            "Data Science / Analytics",
            "Machine Learning / AI",
            "API / Backend Service",
            "Web Application",
            "DevOps / Infrastructure",
        ),
        great_for_platforms=("Web", "Cloud / Server", "Linux", "macOS", "Windows"),
        typical_frameworks=("Django", "FastAPI", "Flask"),
    ),
    LanguageProfile(
        name="JavaScript / TypeScript",
        summary="The web's lingua franca. TypeScript adds the type-safety larger teams need.",
        learning_curve_friendliness=8,
        development_speed=9,
        runtime_performance=7,
        type_safety=8,
        ecosystem_breadth=10,
        scalability_ceiling=9,
        security_maturity=7,
        great_for_project_types=(
            "Web Application",
            "API / Backend Service",
            "Mobile Application",
            "Desktop Application",
        ),
        great_for_platforms=("Web", "Cross-Platform", "Cloud / Server"),
        typical_frameworks=("Next.js", "React", "Express", "NestJS", "React Native"),
    ),
    LanguageProfile(
        name="Go",
        summary="Concurrency-first language with a tiny syntax and great cloud-native ecosystem.",
        learning_curve_friendliness=8,
        development_speed=8,
        runtime_performance=9,
        type_safety=9,
        ecosystem_breadth=8,
        scalability_ceiling=10,
        security_maturity=9,
        great_for_project_types=(
            "API / Backend Service",
            "DevOps / Infrastructure",
            "Enterprise System",
        ),
        great_for_platforms=("Cloud / Server", "Linux"),
        typical_frameworks=("Gin", "Echo", "Fiber"),
    ),
    LanguageProfile(
        name="Java",
        summary="Mature, enterprise-grade, with the most battle-tested runtime and tooling.",
        learning_curve_friendliness=6,
        development_speed=7,
        runtime_performance=9,
        type_safety=9,
        ecosystem_breadth=10,
        scalability_ceiling=10,
        security_maturity=10,
        great_for_project_types=(
            "Enterprise System",
            "API / Backend Service",
            "Mobile Application",
        ),
        great_for_platforms=("Cloud / Server", "Android", "Cross-Platform"),
        typical_frameworks=("Spring Boot", "Quarkus"),
    ),
    LanguageProfile(
        name="Rust",
        summary="Memory-safe systems language. Use when correctness and performance matter most.",
        learning_curve_friendliness=4,
        development_speed=6,
        runtime_performance=10,
        type_safety=10,
        ecosystem_breadth=8,
        scalability_ceiling=10,
        security_maturity=10,
        great_for_project_types=(
            "API / Backend Service",
            "Embedded / IoT",
            "DevOps / Infrastructure",
            "Game Development",
        ),
        great_for_platforms=("Cloud / Server", "Linux", "Windows", "macOS"),
        typical_frameworks=("Axum", "Actix Web"),
    ),
    LanguageProfile(
        name="C#",
        summary="Modern, expressive, and a top choice on Windows, Unity games, and .NET back-ends.",
        learning_curve_friendliness=7,
        development_speed=8,
        runtime_performance=8,
        type_safety=9,
        ecosystem_breadth=9,
        scalability_ceiling=9,
        security_maturity=9,
        great_for_project_types=(
            "Game Development",
            "Enterprise System",
            "API / Backend Service",
            "Desktop Application",
        ),
        great_for_platforms=("Windows", "Cross-Platform", "Cloud / Server"),
        typical_frameworks=("ASP.NET Core", "Unity"),
    ),
    LanguageProfile(
        name="Dart",
        summary="The language of Flutter — one codebase for iOS, Android, web, and desktop.",
        learning_curve_friendliness=8,
        development_speed=9,
        runtime_performance=7,
        type_safety=8,
        ecosystem_breadth=7,
        scalability_ceiling=7,
        security_maturity=7,
        great_for_project_types=(
            "Mobile Application",
            "Desktop Application",
            "Web Application",
        ),
        great_for_platforms=("Cross-Platform", "iOS", "Android"),
        typical_frameworks=("Flutter",),
    ),
    LanguageProfile(
        name="Swift",
        summary="Apple's modern language. The best choice for premium iOS/macOS experiences.",
        learning_curve_friendliness=7,
        development_speed=8,
        runtime_performance=9,
        type_safety=9,
        ecosystem_breadth=7,
        scalability_ceiling=7,
        security_maturity=8,
        great_for_project_types=("Mobile Application", "Desktop Application"),
        great_for_platforms=("iOS", "macOS"),
        typical_frameworks=("SwiftUI",),
    ),
    LanguageProfile(
        name="Kotlin",
        summary="Pragmatic, modern alternative to Java. First-class on Android.",
        learning_curve_friendliness=7,
        development_speed=8,
        runtime_performance=9,
        type_safety=9,
        ecosystem_breadth=9,
        scalability_ceiling=9,
        security_maturity=9,
        great_for_project_types=(
            "Mobile Application",
            "API / Backend Service",
            "Enterprise System",
        ),
        great_for_platforms=("Android", "Cloud / Server", "Cross-Platform"),
        typical_frameworks=("Spring Boot", "Ktor"),
    ),
    LanguageProfile(
        name="C++",
        summary="High-performance systems language for games, engines, and embedded software.",
        learning_curve_friendliness=3,
        development_speed=5,
        runtime_performance=10,
        type_safety=7,
        ecosystem_breadth=9,
        scalability_ceiling=10,
        security_maturity=7,
        great_for_project_types=("Game Development", "Embedded / IoT"),
        great_for_platforms=("Windows", "Linux", "macOS"),
        typical_frameworks=("Unreal Engine", "Qt"),
    ),
]


# ---------------------------------------------------------------------------
# Frameworks
# ---------------------------------------------------------------------------

FRAMEWORKS: list[FrameworkProfile] = [
    FrameworkProfile(
        name="FastAPI", language="Python",
        summary="Type-driven async Python APIs with automatic OpenAPI docs.",
        development_speed=10, learning_curve_friendliness=8,
        scalability_ceiling=9, security_maturity=8, ecosystem_breadth=8,
        great_for_project_types=(
            "API / Backend Service",
            "Machine Learning / AI",
            "Data Science / Analytics",
        ),
        great_for_platforms=("Web", "Cloud / Server"),
    ),
    FrameworkProfile(
        name="Django", language="Python",
        summary="Batteries-included Python framework. Admin, ORM, auth out of the box.",
        development_speed=10, learning_curve_friendliness=8,
        scalability_ceiling=8, security_maturity=10, ecosystem_breadth=9,
        great_for_project_types=("Web Application", "API / Backend Service", "Enterprise System"),
        great_for_platforms=("Web", "Cloud / Server"),
    ),
    FrameworkProfile(
        name="Flask", language="Python",
        summary="Minimal Python micro-framework for small APIs and quick prototypes.",
        development_speed=9, learning_curve_friendliness=10,
        scalability_ceiling=6, security_maturity=7, ecosystem_breadth=8,
        great_for_project_types=("API / Backend Service", "Web Application"),
        great_for_platforms=("Web", "Cloud / Server"),
    ),
    FrameworkProfile(
        name="Next.js", language="JavaScript / TypeScript",
        summary="Production React framework with SSR, edge, and excellent DX.",
        development_speed=9, learning_curve_friendliness=7,
        scalability_ceiling=10, security_maturity=8, ecosystem_breadth=10,
        great_for_project_types=("Web Application", "API / Backend Service"),
        great_for_platforms=("Web",),
    ),
    FrameworkProfile(
        name="React + Vite", language="JavaScript / TypeScript",
        summary="Lean SPA setup. Pair with any backend.",
        development_speed=9, learning_curve_friendliness=8,
        scalability_ceiling=8, security_maturity=7, ecosystem_breadth=10,
        great_for_project_types=("Web Application",),
        great_for_platforms=("Web",),
    ),
    FrameworkProfile(
        name="NestJS", language="JavaScript / TypeScript",
        summary="Opinionated, modular Node back-end with first-class TypeScript.",
        development_speed=8, learning_curve_friendliness=7,
        scalability_ceiling=9, security_maturity=8, ecosystem_breadth=9,
        great_for_project_types=("API / Backend Service", "Enterprise System"),
        great_for_platforms=("Web", "Cloud / Server"),
    ),
    FrameworkProfile(
        name="Express", language="JavaScript / TypeScript",
        summary="Minimal Node HTTP framework. Endlessly flexible.",
        development_speed=9, learning_curve_friendliness=9,
        scalability_ceiling=7, security_maturity=6, ecosystem_breadth=10,
        great_for_project_types=("API / Backend Service", "Web Application"),
        great_for_platforms=("Web", "Cloud / Server"),
    ),
    FrameworkProfile(
        name="React Native", language="JavaScript / TypeScript",
        summary="Cross-platform mobile apps with a JS codebase and native UI.",
        development_speed=8, learning_curve_friendliness=7,
        scalability_ceiling=8, security_maturity=7, ecosystem_breadth=9,
        great_for_project_types=("Mobile Application",),
        great_for_platforms=("Cross-Platform", "iOS", "Android"),
    ),
    FrameworkProfile(
        name="Flutter", language="Dart",
        summary="Single codebase, native-quality UI on iOS, Android, web, and desktop.",
        development_speed=9, learning_curve_friendliness=7,
        scalability_ceiling=8, security_maturity=8, ecosystem_breadth=8,
        great_for_project_types=("Mobile Application", "Desktop Application", "Web Application"),
        great_for_platforms=("Cross-Platform", "iOS", "Android"),
    ),
    FrameworkProfile(
        name="Spring Boot", language="Java",
        summary="The default for enterprise Java back-ends. Mature, deep, and reliable.",
        development_speed=7, learning_curve_friendliness=5,
        scalability_ceiling=10, security_maturity=10, ecosystem_breadth=10,
        great_for_project_types=("Enterprise System", "API / Backend Service"),
        great_for_platforms=("Cloud / Server",),
    ),
    FrameworkProfile(
        name="Gin", language="Go",
        summary="Fast, minimal Go HTTP framework — great for microservices.",
        development_speed=8, learning_curve_friendliness=8,
        scalability_ceiling=10, security_maturity=8, ecosystem_breadth=8,
        great_for_project_types=("API / Backend Service", "DevOps / Infrastructure"),
        great_for_platforms=("Cloud / Server",),
    ),
    FrameworkProfile(
        name="ASP.NET Core", language="C#",
        summary="Cross-platform, high-performance .NET web framework.",
        development_speed=8, learning_curve_friendliness=7,
        scalability_ceiling=10, security_maturity=10, ecosystem_breadth=9,
        great_for_project_types=("Enterprise System", "API / Backend Service", "Web Application"),
        great_for_platforms=("Cloud / Server", "Windows", "Cross-Platform"),
    ),
    FrameworkProfile(
        name="SwiftUI", language="Swift",
        summary="Declarative UI for premium iOS and macOS apps.",
        development_speed=8, learning_curve_friendliness=7,
        scalability_ceiling=8, security_maturity=8, ecosystem_breadth=7,
        great_for_project_types=("Mobile Application", "Desktop Application"),
        great_for_platforms=("iOS", "macOS"),
    ),
    FrameworkProfile(
        name="Unity", language="C#",
        summary="Industry-standard game engine for 2D/3D, mobile, and console.",
        development_speed=8, learning_curve_friendliness=7,
        scalability_ceiling=8, security_maturity=7, ecosystem_breadth=10,
        great_for_project_types=("Game Development",),
        great_for_platforms=("Cross-Platform", "Windows", "iOS", "Android"),
    ),
    FrameworkProfile(
        name="PyTorch + FastAPI", language="Python",
        summary="State-of-the-art deep learning with a thin inference API.",
        development_speed=9, learning_curve_friendliness=7,
        scalability_ceiling=9, security_maturity=7, ecosystem_breadth=10,
        great_for_project_types=("Machine Learning / AI", "Data Science / Analytics"),
        great_for_platforms=("Cloud / Server", "Linux"),
    ),
]


# ---------------------------------------------------------------------------
# SDLC models
# ---------------------------------------------------------------------------

SDLC_MODELS: list[SDLCProfile] = [
    SDLCProfile(
        name="Agile / Scrum",
        summary="Time-boxed sprints, working software every iteration, continuous feedback.",
        suits_small_team=8, suits_large_team=8,
        suits_changing_reqs=10, suits_fixed_scope=5,
        suits_fast_timeline=8, overhead=5, risk_management=8,
        great_for_goals=(
            "Production SaaS Product", "Startup Launch", "Client Project", "MVP / Prototype",
        ),
    ),
    SDLCProfile(
        name="Kanban",
        summary="Continuous flow with WIP limits — optimized for throughput.",
        suits_small_team=10, suits_large_team=7,
        suits_changing_reqs=9, suits_fixed_scope=6,
        suits_fast_timeline=9, overhead=3, risk_management=6,
        great_for_goals=("Internal Tool", "MVP / Prototype", "Open Source Library"),
    ),
    SDLCProfile(
        name="Waterfall",
        summary="Phase-gated, document-heavy. Ideal when scope is fixed and contractual.",
        suits_small_team=6, suits_large_team=8,
        suits_changing_reqs=2, suits_fixed_scope=10,
        suits_fast_timeline=5, overhead=8, risk_management=8,
        great_for_goals=("Client Project", "Research"),
    ),
    SDLCProfile(
        name="DevOps (CD)",
        summary="Automated pipelines, infra-as-code, observability — ship reliably and often.",
        suits_small_team=8, suits_large_team=10,
        suits_changing_reqs=9, suits_fixed_scope=6,
        suits_fast_timeline=7, overhead=6, risk_management=10,
        great_for_goals=("Production SaaS Product", "Startup Launch"),
    ),
    SDLCProfile(
        name="Lean Startup",
        summary="Build–Measure–Learn. Validate hypotheses with minimal code.",
        suits_small_team=10, suits_large_team=5,
        suits_changing_reqs=10, suits_fixed_scope=4,
        suits_fast_timeline=10, overhead=2, risk_management=6,
        great_for_goals=("MVP / Prototype", "Startup Launch", "Learning / Educational"),
    ),
    SDLCProfile(
        name="Spiral",
        summary="Risk-driven, iterative — prototype, evaluate, refine, repeat.",
        suits_small_team=6, suits_large_team=8,
        suits_changing_reqs=8, suits_fixed_scope=7,
        suits_fast_timeline=5, overhead=8, risk_management=10,
        great_for_goals=("Research", "Production SaaS Product"),
    ),
]
