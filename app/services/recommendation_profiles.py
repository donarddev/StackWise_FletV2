"""Technology compatibility profiles for the weighted scoring engine.

Profiles are source-based (official documentation and credible references —
see module comments in ``recommendation_service.py``). Match levels map to
weighted points: very strong=30, strong=20, moderate=10, weak=0.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

# Weighted Multi-Criteria Decision Matrix point values
MATCH_VERY_STRONG = 30
MATCH_STRONG = 20
MATCH_MODERATE = 10
MATCH_WEAK = 0

_MATCH_POINTS = (MATCH_WEAK, MATCH_MODERATE, MATCH_STRONG, MATCH_VERY_STRONG)


def match_points(level: int) -> int:
    """Convert a 0–3 match level to weighted matrix points."""
    return _MATCH_POINTS[max(0, min(3, level))]


@dataclass(frozen=True)
class LanguageTechProfile:
    """Compatibility profile for a programming language."""

    name: str
    sources: tuple[str, ...]
    project_types: Mapping[str, int] = field(default_factory=dict)
    features: Mapping[str, int] = field(default_factory=dict)
    platforms: Mapping[str, int] = field(default_factory=dict)
    experience: Mapping[str, int] = field(default_factory=dict)
    scalability: Mapping[str, int] = field(default_factory=dict)
    performance: Mapping[str, int] = field(default_factory=dict)
    security: Mapping[str, int] = field(default_factory=dict)
    budget: Mapping[str, int] = field(default_factory=dict)
    maintainability: Mapping[str, int] = field(default_factory=dict)
    deployment: Mapping[str, int] = field(default_factory=dict)
    goal_keywords: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class FrameworkTechProfile:
    """Compatibility profile for a framework (must match parent language)."""

    name: str
    language: str
    sources: tuple[str, ...]
    project_types: Mapping[str, int] = field(default_factory=dict)
    features: Mapping[str, int] = field(default_factory=dict)
    platforms: Mapping[str, int] = field(default_factory=dict)
    experience: Mapping[str, int] = field(default_factory=dict)
    scalability: Mapping[str, int] = field(default_factory=dict)
    performance: Mapping[str, int] = field(default_factory=dict)
    security: Mapping[str, int] = field(default_factory=dict)
    budget: Mapping[str, int] = field(default_factory=dict)
    maintainability: Mapping[str, int] = field(default_factory=dict)
    deployment: Mapping[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class SDLCTechProfile:
    """Compatibility profile for an SDLC / process model."""

    name: str
    sources: tuple[str, ...]
    requirements_stability: Mapping[str, int] = field(default_factory=dict)
    timeline: Mapping[str, int] = field(default_factory=dict)
    team_size_band: Mapping[str, int] = field(default_factory=dict)
    stakeholder: Mapping[str, int] = field(default_factory=dict)
    complexity: Mapping[str, int] = field(default_factory=dict)
    maintenance: Mapping[str, int] = field(default_factory=dict)
    deployment: Mapping[str, int] = field(default_factory=dict)


# Normalized tier keys used internally after request normalization
_TIER = ("Low", "Medium", "High", "Very High")
_STABILITY = ("Fixed", "Changing", "Experimental")
_TIMELINE = ("Short", "Medium", "Long")
_TEAM = ("Solo", "Small", "Medium", "Large")
_STAKEHOLDER = ("Low", "Medium", "High", "Very High")


def _tier_map(high: int, med: int = 2, low: int = 1) -> dict[str, int]:
    return {"Low": low, "Medium": med, "High": high, "Very High": high}


def _all_tier(level: int) -> dict[str, int]:
    return {t: level for t in _TIER}


# ---------------------------------------------------------------------------
# Language profiles — ratings 0–3 per normalized criterion value
# ---------------------------------------------------------------------------

LANGUAGE_PROFILES: list[LanguageTechProfile] = [
    LanguageTechProfile(
        name="Python",
        sources=("Official Python documentation", "GeeksforGeeks"),
        project_types={
            "Web Application": 3,
            "Mobile Application": 1,
            "Desktop Application": 2,
            "API / Backend System": 3,
            "AI / Machine Learning Project": 3,
            "E-commerce System": 2,
            "Information System": 3,
            "Portfolio / Personal Project": 3,
            "Capstone / Thesis Project": 3,
        },
        features={
            "Authentication": 2,
            "CRUD Operations": 3,
            "CRUD": 3,
            "Admin Dashboard": 2,
            "Dashboard": 2,
            "Reports / Analytics": 3,
            "Payments": 2,
            "Chat / Messaging": 2,
            "Notifications": 2,
            "File Uploads": 2,
            "API / Integrations": 3,
            "Real-time Updates": 2,
            "AI / ML Features": 3,
            "Offline-first Mode": 1,
            "Search / Filtering": 2,
            "Role-based Access": 2,
            "Maps / Location": 1,
        },
        platforms={"Web": 3, "Mobile": 1, "Desktop": 2, "Cross-platform": 2, "Backend/API": 3, "Not sure": 2},
        experience={"Beginner": 3, "Intermediate": 3, "Advanced": 2, "Team has mixed experience": 3},
        scalability=_tier_map(3, 2, 1),
        performance=_tier_map(2, 2, 3),
        security=_tier_map(2, 2, 2),
        budget={"Low": 3, "Medium": 3, "High": 2, "Very limited": 3, "Limited": 3, "Flexible": 2, "Not a concern": 2},
        maintainability=_all_tier(3),
        deployment={
            "Cloud": 3,
            "Cloud deployment": 3,
            "Docker/containerized": 3,
            "Shared hosting": 2,
            "Local only": 2,
            "Local": 2,
            "Not sure": 2,
        },
        goal_keywords=("automation", "data", "api", "student", "analytics", "machine learning", "ai"),
    ),
    LanguageTechProfile(
        name="PHP",
        sources=("Official PHP documentation", "W3Schools", "GeeksforGeeks"),
        project_types={
            "Web Application": 3,
            "E-commerce System": 3,
            "Information System": 3,
            "API / Backend System": 2,
            "Portfolio / Personal Project": 3,
            "Capstone / Thesis Project": 3,
        },
        features={
            "Authentication": 3,
            "CRUD Operations": 3,
            "CRUD": 3,
            "Admin Dashboard": 3,
            "Dashboard": 3,
            "Reports / Analytics": 2,
            "Payments": 2,
            "API / Integrations": 2,
            "Role-based Access": 3,
        },
        platforms={"Web": 3, "Backend/API": 2, "Cross-platform": 1},
        experience={"Beginner": 3, "Intermediate": 3, "Advanced": 2, "Team has mixed experience": 3},
        scalability=_tier_map(2, 2, 1),
        performance=_tier_map(2, 2, 1),
        security=_tier_map(2, 2, 2),
        budget={"Low": 3, "Medium": 3, "High": 1, "Very limited": 3, "Limited": 3},
        maintainability=_all_tier(2),
        deployment={"Cloud": 2, "Cloud deployment": 2, "Shared hosting": 3, "Local": 2},
        goal_keywords=("crud", "admin", "laravel", "student", "business", "web"),
    ),
    LanguageTechProfile(
        name="JavaScript / TypeScript",
        sources=("MDN Web Docs", "Official framework documentation", "W3Schools"),
        project_types={
            "Web Application": 3,
            "Mobile Application": 2,
            "Desktop Application": 2,
            "API / Backend System": 3,
            "E-commerce System": 3,
            "Information System": 2,
            "Portfolio / Personal Project": 3,
            "Capstone / Thesis Project": 3,
        },
        features={
            "Authentication": 3,
            "CRUD Operations": 3,
            "CRUD": 3,
            "Admin Dashboard": 3,
            "Dashboard": 3,
            "Reports / Analytics": 2,
            "Real-time Updates": 3,
            "API / Integrations": 3,
            "Search / Filtering": 3,
            "Chat / Messaging": 3,
            "Notifications": 3,
            "Payments": 2,
            "Offline-first Mode": 2,
            "Role-based Access": 2,
        },
        platforms={"Web": 3, "Mobile": 2, "Desktop": 2, "Cross-platform": 3, "Backend/API": 3},
        experience={"Beginner": 2, "Intermediate": 3, "Advanced": 3, "Team has mixed experience": 3},
        scalability=_tier_map(3, 2, 2),
        performance=_tier_map(3, 2, 2),
        security=_tier_map(2, 2, 2),
        budget=_all_tier(2),
        maintainability=_all_tier(2),
        deployment={"Cloud": 3, "Cloud deployment": 3, "Docker/containerized": 3},
        goal_keywords=("saas", "dashboard", "interactive", "web", "frontend", "full stack"),
    ),
    LanguageTechProfile(
        name="Java",
        sources=("Oracle/OpenJDK Java documentation", "Official Spring documentation"),
        project_types={
            "Web Application": 2,
            "API / Backend System": 3,
            "E-commerce System": 3,
            "Information System": 3,
            "Mobile Application": 2,
            "Capstone / Thesis Project": 2,
        },
        features={
            "Authentication": 3,
            "CRUD Operations": 3,
            "CRUD": 3,
            "Role-based Access": 3,
            "Payments": 3,
            "Reports / Analytics": 2,
            "API / Integrations": 3,
        },
        platforms={"Web": 2, "Mobile": 2, "Backend/API": 3, "Cross-platform": 2},
        experience={"Beginner": 1, "Intermediate": 2, "Advanced": 3, "Team has mixed experience": 2},
        scalability=_tier_map(3, 2, 1),
        performance=_tier_map(3, 2, 1),
        security=_tier_map(3, 3, 2),
        budget=_all_tier(1),
        maintainability=_all_tier(3),
        deployment={"Cloud": 3, "Cloud deployment": 3, "Docker/containerized": 3},
        goal_keywords=("enterprise", "secure", "scalable", "android", "backend"),
    ),
    LanguageTechProfile(
        name="C#",
        sources=("Microsoft Learn", "Official ASP.NET Core documentation"),
        project_types={
            "Web Application": 3,
            "Desktop Application": 3,
            "API / Backend System": 3,
            "E-commerce System": 2,
            "Information System": 3,
        },
        features={
            "Authentication": 3,
            "CRUD Operations": 3,
            "CRUD": 3,
            "Admin Dashboard": 3,
            "Dashboard": 3,
            "Role-based Access": 3,
            "API / Integrations": 3,
        },
        platforms={"Web": 3, "Desktop": 3, "Cross-platform": 2, "Backend/API": 3},
        experience={"Beginner": 2, "Intermediate": 3, "Advanced": 3, "Team has mixed experience": 2},
        scalability=_tier_map(3, 2, 1),
        performance=_tier_map(3, 2, 2),
        security=_tier_map(3, 3, 2),
        budget=_all_tier(1),
        maintainability=_all_tier(3),
        deployment={"Cloud": 3, "Cloud deployment": 3, "Docker/containerized": 3},
        goal_keywords=("windows", "enterprise", "asp.net", "desktop"),
    ),
    LanguageTechProfile(
        name="Dart",
        sources=("Official Dart documentation", "Official Flutter documentation"),
        project_types={
            "Mobile Application": 3,
            "Web Application": 2,
            "Desktop Application": 2,
            "Cross-platform": 3,
        },
        platforms={"Mobile": 3, "Cross-platform": 3, "Web": 2, "Desktop": 2},
        experience={"Beginner": 2, "Intermediate": 3, "Advanced": 2, "Team has mixed experience": 2},
        scalability=_tier_map(2, 2, 1),
        performance=_tier_map(2, 2, 2),
        features={
            "Authentication": 2,
            "CRUD": 2,
            "CRUD Operations": 2,
            "Offline-first Mode": 3,
            "Notifications": 2,
            "Maps / Location": 2,
        },
        budget=_all_tier(2),
        maintainability=_all_tier(2),
        deployment={"Cloud": 2, "Mobile": 3},
        goal_keywords=("flutter", "mobile", "cross-platform", "ios", "android"),
    ),
    LanguageTechProfile(
        name="Kotlin",
        sources=("Official Kotlin documentation", "Android developer documentation"),
        project_types={"Mobile Application": 3, "API / Backend System": 2, "Information System": 2},
        platforms={"Mobile": 3, "Backend/API": 2, "Cross-platform": 2},
        experience={"Beginner": 2, "Intermediate": 3, "Advanced": 3, "Team has mixed experience": 2},
        scalability=_tier_map(3, 2, 1),
        performance=_tier_map(3, 2, 2),
        security=_tier_map(3, 2, 2),
        features={"Authentication": 2, "CRUD": 2, "API / Integrations": 2, "Offline-first Mode": 2},
        budget=_all_tier(2),
        maintainability=_all_tier(3),
        deployment={"Cloud": 3, "Docker/containerized": 3},
        goal_keywords=("android", "jvm", "backend", "mobile"),
    ),
    LanguageTechProfile(
        name="Swift",
        sources=("Official Swift documentation", "Apple developer documentation"),
        project_types={"Mobile Application": 3, "Desktop Application": 2},
        platforms={"Mobile": 3, "Desktop": 2},
        experience={"Beginner": 2, "Intermediate": 3, "Advanced": 3, "Team has mixed experience": 2},
        scalability=_tier_map(2, 2, 1),
        performance=_tier_map(3, 2, 2),
        security=_tier_map(3, 2, 2),
        features={"Authentication": 2, "Offline-first Mode": 3, "Maps / Location": 3, "Payments": 2},
        budget=_all_tier(1),
        maintainability=_all_tier(2),
        deployment={"Cloud": 2, "Local": 2},
        goal_keywords=("ios", "iphone", "ipad", "apple", "native"),
    ),
    LanguageTechProfile(
        name="Ruby",
        sources=("Official Ruby documentation", "Official Rails documentation", "GeeksforGeeks"),
        project_types={
            "Web Application": 3,
            "E-commerce System": 2,
            "Portfolio / Personal Project": 3,
            "Capstone / Thesis Project": 2,
        },
        features={"Authentication": 3, "CRUD": 3, "CRUD Operations": 3, "Admin Dashboard": 2},
        platforms={"Web": 3, "Backend/API": 2},
        experience={"Beginner": 2, "Intermediate": 3, "Advanced": 2, "Team has mixed experience": 2},
        scalability=_tier_map(2, 2, 1),
        performance=_tier_map(1, 2, 2),
        security=_tier_map(2, 2, 2),
        budget={"Low": 2, "Medium": 3, "High": 1},
        maintainability=_all_tier(2),
        deployment={"Cloud": 3, "Cloud deployment": 3},
        goal_keywords=("mvp", "startup", "rapid", "rails", "prototype"),
    ),
    LanguageTechProfile(
        name="Go",
        sources=("Official Go documentation", "GeeksforGeeks"),
        project_types={"API / Backend System": 3, "Web Application": 2, "Information System": 2},
        platforms={"Backend/API": 3, "Web": 2, "Cross-platform": 2},
        experience={"Beginner": 2, "Intermediate": 3, "Advanced": 3, "Team has mixed experience": 2},
        scalability=_tier_map(3, 3, 2),
        performance=_tier_map(3, 3, 2),
        security=_tier_map(3, 2, 2),
        features={"API / Integrations": 3, "Authentication": 2, "Real-time Updates": 2},
        budget=_all_tier(2),
        maintainability=_all_tier(2),
        deployment={"Cloud": 3, "Docker/containerized": 3, "Cloud deployment": 3},
        goal_keywords=("microservice", "api", "backend", "performance", "scalable"),
    ),
    LanguageTechProfile(
        name="Rust",
        sources=("Official Rust documentation", "GeeksforGeeks"),
        project_types={
            "Desktop Application": 3,
            "API / Backend System": 2,
            "Web Application": 1,
        },
        platforms={"Desktop": 3, "Cross-platform": 3, "Backend/API": 2},
        experience={"Beginner": 0, "Intermediate": 2, "Advanced": 3, "Team has mixed experience": 1},
        scalability=_tier_map(3, 2, 1),
        performance=_tier_map(3, 3, 3),
        security=_tier_map(3, 3, 3),
        features={"API / Integrations": 2, "Offline-first Mode": 2},
        budget=_all_tier(2),
        maintainability=_all_tier(2),
        deployment={"Cloud": 2, "Docker/containerized": 3, "Local": 2},
        goal_keywords=("performance", "systems", "safe", "desktop", "cross-platform"),
    ),
    LanguageTechProfile(
        name="SQL",
        sources=("W3Schools SQL reference", "GeeksforGeeks"),
        project_types={
            "Information System": 3,
            "E-commerce System": 2,
            "AI / Machine Learning Project": 2,
            "API / Backend System": 1,
        },
        features={
            "Reports / Analytics": 3,
            "CRUD": 3,
            "CRUD Operations": 3,
            "Search / Filtering": 3,
            "Role-based Access": 2,
        },
        platforms={"Backend/API": 3, "Web": 1},
        experience={"Beginner": 2, "Intermediate": 3, "Advanced": 3, "Team has mixed experience": 2},
        scalability=_tier_map(3, 2, 1),
        performance=_tier_map(2, 3, 2),
        security=_tier_map(3, 2, 2),
        budget=_all_tier(3),
        maintainability=_all_tier(3),
        deployment={"Cloud": 2, "Local": 3, "Shared hosting": 2},
        goal_keywords=("database", "analytics", "reporting", "data warehouse", "sql"),
    ),
]


# ---------------------------------------------------------------------------
# Framework profiles (language-locked)
# ---------------------------------------------------------------------------

FRAMEWORK_PROFILES: list[FrameworkTechProfile] = [
    FrameworkTechProfile(
        name="FastAPI",
        language="Python",
        sources=("Official Python documentation", "Official FastAPI documentation"),
        project_types={"API / Backend System": 3, "Web Application": 2, "AI / Machine Learning Project": 3},
        features={"API / Integrations": 3, "Authentication": 2, "CRUD": 3, "AI / ML Features": 3},
        platforms={"Backend/API": 3, "Web": 2},
        experience={"Beginner": 3, "Intermediate": 3, "Advanced": 3, "Team has mixed experience": 3},
        scalability=_tier_map(3, 2, 1),
        performance=_tier_map(3, 2, 2),
        deployment={"Cloud": 3, "Docker/containerized": 3},
    ),
    FrameworkTechProfile(
        name="Django",
        language="Python",
        sources=("Official Django documentation", "Official Python documentation"),
        project_types={"Web Application": 3, "Information System": 3, "E-commerce System": 2},
        features={
            "Authentication": 3,
            "CRUD": 3,
            "Admin Dashboard": 3,
            "Dashboard": 3,
            "Role-based Access": 3,
        },
        platforms={"Web": 3, "Backend/API": 2},
        experience={"Beginner": 2, "Intermediate": 3, "Advanced": 3, "Team has mixed experience": 2},
        scalability=_tier_map(2, 2, 1),
        security=_tier_map(3, 3, 2),
        maintainability=_all_tier(3),
    ),
    FrameworkTechProfile(
        name="Flask",
        language="Python",
        sources=("Official Flask documentation", "Official Python documentation"),
        project_types={"Web Application": 2, "API / Backend System": 2, "Portfolio / Personal Project": 3},
        features={"CRUD": 2, "Authentication": 2, "API / Integrations": 2},
        experience={"Beginner": 3, "Intermediate": 3, "Advanced": 2, "Team has mixed experience": 3},
        budget={"Low": 3, "Very limited": 3, "Limited": 3},
        deployment={"Cloud": 2, "Shared hosting": 3},
    ),
    FrameworkTechProfile(
        name="Laravel",
        language="PHP",
        sources=("Official Laravel documentation", "Official PHP documentation"),
        project_types={"Web Application": 3, "Information System": 3, "E-commerce System": 3},
        features={
            "Authentication": 3,
            "CRUD": 3,
            "Admin Dashboard": 3,
            "Dashboard": 3,
            "Role-based Access": 3,
        },
        platforms={"Web": 3},
        experience={"Beginner": 3, "Intermediate": 3, "Advanced": 2, "Team has mixed experience": 3},
        budget={"Low": 3, "Limited": 3},
    ),
    FrameworkTechProfile(
        name="Next.js",
        language="JavaScript / TypeScript",
        sources=("MDN Web Docs", "Official Next.js documentation"),
        project_types={"Web Application": 3, "E-commerce System": 3, "Portfolio / Personal Project": 3},
        features={"Dashboard": 3, "Authentication": 3, "SEO": 2, "CRUD": 3, "Real-time Updates": 2},
        platforms={"Web": 3},
        experience={"Beginner": 2, "Intermediate": 3, "Advanced": 3, "Team has mixed experience": 2},
        scalability=_tier_map(3, 2, 1),
        deployment={"Cloud": 3, "Cloud deployment": 3},
    ),
    FrameworkTechProfile(
        name="React",
        language="JavaScript / TypeScript",
        sources=("MDN Web Docs", "Official React documentation"),
        project_types={"Web Application": 3, "Portfolio / Personal Project": 3},
        features={"Dashboard": 3, "Real-time Updates": 3, "Search / Filtering": 2},
        platforms={"Web": 3},
        experience={"Beginner": 2, "Intermediate": 3, "Advanced": 3, "Team has mixed experience": 2},
    ),
    FrameworkTechProfile(
        name="Express",
        language="JavaScript / TypeScript",
        sources=("MDN Web Docs", "Official Express documentation"),
        project_types={"API / Backend System": 3, "Web Application": 2},
        features={"API / Integrations": 3, "Authentication": 2, "CRUD": 3},
        platforms={"Backend/API": 3, "Web": 2},
        experience={"Beginner": 3, "Intermediate": 3, "Advanced": 3, "Team has mixed experience": 3},
    ),
    FrameworkTechProfile(
        name="NestJS",
        language="JavaScript / TypeScript",
        sources=("Official NestJS documentation", "MDN Web Docs"),
        project_types={"API / Backend System": 3, "E-commerce System": 2, "Information System": 2},
        features={"Authentication": 3, "Role-based Access": 3, "API / Integrations": 3},
        experience={"Beginner": 1, "Intermediate": 3, "Advanced": 3, "Team has mixed experience": 2},
        scalability=_tier_map(3, 2, 1),
        security=_tier_map(3, 3, 2),
    ),
    FrameworkTechProfile(
        name="Spring Boot",
        language="Java",
        sources=("Official Spring documentation", "Oracle/OpenJDK Java documentation"),
        project_types={"API / Backend System": 3, "Information System": 3, "E-commerce System": 3},
        features={"Authentication": 3, "CRUD": 3, "Role-based Access": 3, "Payments": 3},
        scalability=_tier_map(3, 3, 2),
        security=_tier_map(3, 3, 3),
        experience={"Beginner": 1, "Intermediate": 2, "Advanced": 3, "Team has mixed experience": 2},
    ),
    FrameworkTechProfile(
        name="ASP.NET Core",
        language="C#",
        sources=("Microsoft Learn", "Official ASP.NET Core documentation"),
        project_types={"Web Application": 3, "API / Backend System": 3, "Information System": 3},
        features={"Authentication": 3, "CRUD": 3, "Admin Dashboard": 3, "Role-based Access": 3},
        security=_tier_map(3, 3, 3),
        experience={"Beginner": 2, "Intermediate": 3, "Advanced": 3, "Team has mixed experience": 2},
    ),
    FrameworkTechProfile(
        name="Flutter",
        language="Dart",
        sources=("Official Flutter documentation", "Official Dart documentation"),
        project_types={"Mobile Application": 3, "Web Application": 2, "Desktop Application": 2},
        features={"Offline-first Mode": 3, "Authentication": 2, "Maps / Location": 2},
        platforms={"Mobile": 3, "Cross-platform": 3},
        experience={"Beginner": 2, "Intermediate": 3, "Advanced": 2, "Team has mixed experience": 2},
    ),
    FrameworkTechProfile(
        name="Android/Ktor",
        language="Kotlin",
        sources=("Official Kotlin documentation", "Android developer documentation"),
        project_types={"Mobile Application": 3, "API / Backend System": 2},
        platforms={"Mobile": 3, "Backend/API": 2},
        experience={"Beginner": 2, "Intermediate": 3, "Advanced": 3, "Team has mixed experience": 2},
    ),
    FrameworkTechProfile(
        name="SwiftUI",
        language="Swift",
        sources=("Apple developer documentation", "Official Swift documentation"),
        project_types={"Mobile Application": 3, "Desktop Application": 2},
        platforms={"Mobile": 3},
        experience={"Beginner": 2, "Intermediate": 3, "Advanced": 3, "Team has mixed experience": 2},
    ),
    FrameworkTechProfile(
        name="Rails",
        language="Ruby",
        sources=("Official Rails documentation", "Official Ruby documentation"),
        project_types={"Web Application": 3, "E-commerce System": 2, "Portfolio / Personal Project": 3},
        features={"Authentication": 3, "CRUD": 3, "Admin Dashboard": 2},
        experience={"Beginner": 2, "Intermediate": 3, "Advanced": 2, "Team has mixed experience": 2},
        deployment={"Cloud": 3, "Cloud deployment": 3},
    ),
    FrameworkTechProfile(
        name="Gin",
        language="Go",
        sources=("Official Go documentation", "Official Gin documentation"),
        project_types={"API / Backend System": 3},
        features={"API / Integrations": 3, "Authentication": 2},
        scalability=_tier_map(3, 3, 2),
        performance=_tier_map(3, 3, 3),
        experience={"Intermediate": 3, "Advanced": 3, "Beginner": 2, "Team has mixed experience": 2},
    ),
    FrameworkTechProfile(
        name="Tauri",
        language="Rust",
        sources=("Official Rust documentation", "Official Tauri documentation"),
        project_types={"Desktop Application": 3, "Web Application": 2},
        platforms={"Desktop": 3, "Cross-platform": 3},
        performance=_tier_map(3, 3, 3),
        experience={"Intermediate": 2, "Advanced": 3, "Beginner": 0, "Team has mixed experience": 1},
    ),
    FrameworkTechProfile(
        name="Flet",
        language="Python",
        sources=(
            "Official Flet documentation",
            "Official Flet GitHub",
            "Official Flet build documentation",
        ),
        project_types={
            "Desktop Application": 3,
            "Web Application": 2,
            "Information System": 2,
            "Machine Learning / AI": 2,
        },
        features={
            "Admin Dashboard": 3,
            "Reports / Analytics": 3,
            "AI / ML Features": 2,
            "Chat / Messaging": 2,
            "Offline-first Mode": 2,
        },
        platforms={"Desktop": 3, "Web": 2, "Cross-platform": 3},
        experience={"Beginner": 3, "Intermediate": 3, "Advanced": 2, "Team has mixed experience": 2},
        deployment={"Local only": 3, "Cloud deployment": 2},
    ),
]

LANGUAGE_FRAMEWORK_MAP: dict[str, list[str]] = {
    "Python": ["FastAPI", "Django", "Flask", "Flet"],
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

SQL_FRAMEWORK_LABEL = "Database-focused stack"


# ---------------------------------------------------------------------------
# SDLC profiles — ISO/IEC/IEEE 12207 & PMBOK tailoring
# ---------------------------------------------------------------------------

SDLC_PROFILES: list[SDLCTechProfile] = [
    SDLCTechProfile(
        name="Agile",
        sources=("ISO/IEC/IEEE 12207", "PMBOK tailoring"),
        requirements_stability={"Changing": 3, "Experimental": 3, "Fixed": 1},
        timeline={"Short": 3, "Medium": 2, "Long": 2},
        team_size_band={"Small": 3, "Medium": 3, "Large": 2, "Solo": 2},
        stakeholder={"High": 3, "Very High": 3, "Medium": 2, "Low": 1},
        complexity={"High": 2, "Very High": 2, "Medium": 3, "Low": 3},
    ),
    SDLCTechProfile(
        name="Waterfall",
        sources=("ISO/IEC/IEEE 12207", "PMBOK tailoring"),
        requirements_stability={"Fixed": 3, "Changing": 0, "Experimental": 0},
        timeline={"Long": 3, "Medium": 2, "Short": 0},
        team_size_band={"Large": 3, "Medium": 2, "Small": 1, "Solo": 0},
        stakeholder={"Low": 2, "Medium": 2, "High": 1, "Very High": 1},
        complexity={"High": 2, "Very High": 3, "Medium": 2, "Low": 2},
    ),
    SDLCTechProfile(
        name="Iterative",
        sources=("ISO/IEC/IEEE 12207",),
        requirements_stability={"Changing": 3, "Fixed": 2, "Experimental": 2},
        timeline={"Medium": 3, "Short": 2, "Long": 2},
        complexity={"High": 3, "Very High": 3, "Medium": 2, "Low": 2},
        stakeholder={"High": 2, "Medium": 3, "Low": 2, "Very High": 2},
    ),
    SDLCTechProfile(
        name="Incremental",
        sources=("ISO/IEC/IEEE 12207",),
        requirements_stability={"Fixed": 2, "Changing": 2, "Experimental": 1},
        timeline={"Medium": 3, "Long": 3, "Short": 1},
        team_size_band={"Medium": 3, "Large": 3, "Small": 2, "Solo": 1},
    ),
    SDLCTechProfile(
        name="Spiral",
        sources=("ISO/IEC/IEEE 12207", "PMBOK risk tailoring"),
        requirements_stability={"Changing": 2, "Fixed": 2, "Experimental": 3},
        complexity={"Very High": 3, "High": 3, "Medium": 2, "Low": 1},
        stakeholder={"Medium": 2, "High": 2, "Low": 2, "Very High": 2},
        timeline={"Long": 3, "Medium": 2, "Short": 0},
    ),
    SDLCTechProfile(
        name="V-Model",
        sources=("ISO/IEC/IEEE 12207",),
        requirements_stability={"Fixed": 3, "Changing": 0, "Experimental": 0},
        complexity={"High": 3, "Very High": 3, "Medium": 2, "Low": 1},
        stakeholder={"Low": 2, "Medium": 2, "High": 1, "Very High": 1},
        maintenance={"High": 3, "Medium": 2, "Low": 1},
    ),
    SDLCTechProfile(
        name="RAD",
        sources=("PMBOK tailoring",),
        timeline={"Short": 3, "Medium": 2, "Long": 0},
        requirements_stability={"Changing": 2, "Fixed": 1, "Experimental": 2},
        team_size_band={"Small": 3, "Medium": 2, "Solo": 2, "Large": 1},
        stakeholder={"High": 2, "Medium": 2, "Low": 2, "Very High": 2},
    ),
    SDLCTechProfile(
        name="Prototype",
        sources=("PMBOK tailoring", "ISO/IEC/IEEE 12207"),
        requirements_stability={"Changing": 3, "Experimental": 3, "Fixed": 1},
        timeline={"Short": 3, "Medium": 2, "Long": 1},
        stakeholder={"High": 3, "Very High": 3, "Medium": 2, "Low": 1},
        team_size_band={"Small": 3, "Solo": 3, "Medium": 2, "Large": 1},
    ),
    SDLCTechProfile(
        name="Scrum",
        sources=("PMBOK tailoring", "ISO/IEC/IEEE 12207"),
        requirements_stability={"Changing": 3, "Experimental": 2, "Fixed": 1},
        timeline={"Short": 3, "Medium": 2, "Long": 1},
        team_size_band={"Small": 3, "Medium": 3, "Large": 2, "Solo": 1},
        stakeholder={"High": 3, "Very High": 3, "Medium": 2, "Low": 1},
    ),
    SDLCTechProfile(
        name="Kanban",
        sources=("PMBOK tailoring",),
        requirements_stability={"Changing": 3, "Fixed": 1, "Experimental": 2},
        timeline={"Short": 3, "Medium": 3, "Long": 2},
        team_size_band={"Small": 3, "Solo": 3, "Medium": 2, "Large": 2},
        stakeholder={"Medium": 2, "High": 2, "Low": 2, "Very High": 2},
    ),
    SDLCTechProfile(
        name="DevOps",
        sources=("ISO/IEC/IEEE 12207", "PMBOK tailoring"),
        requirements_stability={"Changing": 2, "Fixed": 1, "Experimental": 2},
        deployment={"Cloud": 3, "Cloud deployment": 3, "Docker/containerized": 3},
        complexity={"High": 3, "Very High": 3, "Medium": 2, "Low": 1},
        maintenance={"High": 3, "Medium": 2, "Low": 1},
        timeline={"Medium": 2, "Short": 2, "Long": 2},
    ),
    SDLCTechProfile(
        name="Lean Startup",
        sources=("PMBOK tailoring",),
        requirements_stability={"Changing": 3, "Experimental": 3, "Fixed": 0},
        timeline={"Short": 3, "Medium": 2, "Long": 0},
        team_size_band={"Solo": 3, "Small": 3, "Medium": 1, "Large": 0},
        stakeholder={"High": 3, "Very High": 3, "Medium": 2, "Low": 2},
    ),
    SDLCTechProfile(
        name="Big Bang",
        sources=("PMBOK tailoring",),
        requirements_stability={"Fixed": 1, "Changing": 2, "Experimental": 2},
        timeline={"Short": 3, "Medium": 1, "Long": 0},
        team_size_band={"Solo": 3, "Small": 3, "Medium": 1, "Large": 0},
        complexity={"Low": 3, "Medium": 2, "High": 0, "Very High": 0},
    ),
    SDLCTechProfile(
        name="FDD",
        sources=("ISO/IEC/IEEE 12207",),
        requirements_stability={"Fixed": 2, "Changing": 2, "Experimental": 1},
        team_size_band={"Large": 3, "Medium": 3, "Small": 1, "Solo": 0},
        complexity={"High": 3, "Very High": 2, "Medium": 2, "Low": 1},
        timeline={"Long": 3, "Medium": 2, "Short": 0},
    ),
    SDLCTechProfile(
        name="XP",
        sources=("PMBOK tailoring", "ISO/IEC/IEEE 12207"),
        requirements_stability={"Changing": 3, "Experimental": 2, "Fixed": 0},
        timeline={"Short": 3, "Medium": 2, "Long": 1},
        stakeholder={"High": 3, "Very High": 3, "Medium": 2, "Low": 1},
        team_size_band={"Small": 3, "Medium": 2, "Solo": 2, "Large": 1},
    ),
]
