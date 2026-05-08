"""Project-wide constants, enumerations, and option lists.

Centralizing these values prevents magic strings from leaking into UI/services
and keeps the recommendation engine and forms in lock-step.
"""

from __future__ import annotations


# ---------- Routes ----------

class Routes:
    HOME = "/"
    LOGIN = "/login"
    REGISTER = "/register"
    DASHBOARD = "/dashboard"
    RECOMMENDATION = "/recommendation"
    HISTORY = "/history"
    CHATBOT = "/chatbot"
    LEARNING = "/learning"
    SETTINGS = "/settings"


# ---------- Recommendation form options ----------

PROJECT_TYPES: list[str] = [
    "Web Application",
    "Mobile Application",
    "Desktop Application",
    "API / Backend Service",
    "Data Science / Analytics",
    "Machine Learning / AI",
    "DevOps / Infrastructure",
    "Game Development",
    "Embedded / IoT",
    "Enterprise System",
]

PROJECT_GOALS: list[str] = [
    "MVP / Prototype",
    "Production SaaS Product",
    "Internal Tool",
    "Learning / Educational",
    "Research",
    "Open Source Library",
    "Client Project",
    "Startup Launch",
]

COMPLEXITY_LEVELS: list[str] = ["Simple", "Moderate", "Complex", "Highly Complex"]

TEAM_SIZES: list[str] = [
    "Solo (1)",
    "Small (2–4)",
    "Medium (5–10)",
    "Large (11–25)",
    "Enterprise (25+)",
]

TIMELINES: list[str] = [
    "Less than 1 month",
    "1–3 months",
    "3–6 months",
    "6–12 months",
    "More than 12 months",
]

SCALABILITY_LEVELS: list[str] = ["Low", "Medium", "High", "Massive"]

SECURITY_LEVELS: list[str] = ["Standard", "Elevated", "High", "Critical"]

EXPERIENCE_LEVELS: list[str] = ["Beginner", "Intermediate", "Advanced", "Expert"]

PLATFORMS: list[str] = [
    "Web",
    "Cross-Platform",
    "iOS",
    "Android",
    "Windows",
    "macOS",
    "Linux",
    "Cloud / Server",
]


# ---------- Recommendation engine ----------

CONFIDENCE_LEVELS: dict[str, tuple[int, int]] = {
    "Low": (0, 49),
    "Moderate": (50, 69),
    "High": (70, 84),
    "Very High": (85, 100),
}


def confidence_label(score: int) -> str:
    for label, (lo, hi) in CONFIDENCE_LEVELS.items():
        if lo <= score <= hi:
            return label
    return "Moderate"


# ---------- UI / Brand ----------

BRAND_NAME = "StackWise AI"
BRAND_INITIALS = "SW"
