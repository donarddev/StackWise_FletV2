"""RecommendationRequest — validates the project profile form."""

from __future__ import annotations

from dataclasses import dataclass

from app.requests.base_request import BaseRequest, Rule
from app.utils.validators import is_in, is_non_empty, max_length, min_length, sanitize

PROJECT_TYPES = [
    "Web Application",
    "Mobile Application",
    "Desktop Application",
    "API / Backend System",
    "AI / Machine Learning Project",
    "E-commerce System",
    "Information System",
    "Portfolio / Personal Project",
    "Capstone / Thesis Project",
]
COMPLEXITY_LEVELS = ["Low", "Medium", "High", "Very High"]
TIMELINES = ["Less than 1 month", "1–2 months", "3–4 months", "5–6 months", "More than 6 months"]
REQUIREMENTS_STABILITY_LEVELS = [
    "Very Stable",
    "Mostly Stable",
    "Somewhat Changing",
    "Frequently Changing",
    "Unknown / Experimental",
]
STAKEHOLDER_INVOLVEMENT_LEVELS = ["Low", "Medium", "High", "Frequent Review Needed"]
PREFERRED_PLATFORMS = ["Web", "Mobile", "Desktop", "Cross-platform", "Backend/API", "Not sure"]
DEVELOPMENT_EXPERIENCE_LEVELS = [
    "Beginner",
    "Intermediate",
    "Advanced",
    "Team has mixed experience",
]
SCALABILITY_NEEDS_LEVELS = [
    "Small user base",
    "Medium user base",
    "Large user base",
    "Expected to grow fast",
    "Not sure",
]
PERFORMANCE_REQUIREMENTS_LEVELS = ["Basic", "Moderate", "High", "Real-time / Low latency", "Not sure"]
SECURITY_REQUIREMENTS_LEVELS = ["Basic", "Moderate", "High", "Sensitive user data", "Payment or financial data"]
BUDGET_CONSTRAINTS_LEVELS = ["Very limited", "Limited", "Flexible", "Not a concern"]
MAINTENANCE_EXPECTATIONS_LEVELS = [
    "Short-term school project",
    "Long-term maintainable project",
    "Production-ready system",
    "Prototype only",
]
DEPLOYMENT_PREFERENCES = ["Local only", "Shared hosting", "Cloud deployment", "Docker/containerized", "Not sure"]
PREFERRED_STACK_NONE = "None / Not sure"

PREFERRED_LANGUAGE_OPTIONS = [
    PREFERRED_STACK_NONE,
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
]

PREFERRED_FRAMEWORK_OPTIONS = [
    PREFERRED_STACK_NONE,
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
]

PREFERRED_SDLC_OPTIONS = [
    PREFERRED_STACK_NONE,
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
]

FEATURE_OPTIONS = [
    "Authentication",
    "CRUD Operations",
    "Admin Dashboard",
    "Reports / Analytics",
    "Payments",
    "Chat / Messaging",
    "Notifications",
    "File Uploads",
    "API / Integrations",
    "Real-time Updates",
    "AI / ML Features",
    "Offline-first Mode",
    "Search / Filtering",
    "Role-based Access",
    "Maps / Location",
]


@dataclass
class RecommendationRequest(BaseRequest):
    project_name: str = ""
    project_type: str = ""
    selected_features: str = ""
    project_goal: str = ""
    team_size: str = ""
    complexity: str = ""
    timeline: str = ""
    requirements_stability: str = ""
    stakeholder_involvement: str = ""
    preferred_platform: str = ""
    development_experience: str = ""
    scalability_needs: str = ""
    performance_requirements: str = ""
    security_requirements: str = ""
    budget_constraints: str = ""
    maintenance_expectations: str = ""
    deployment_preference: str = ""

    def sanitize(self) -> None:
        for fname in (
            "project_name",
            "project_type",
            "selected_features",
            "project_goal",
            "team_size",
            "complexity",
            "timeline",
            "requirements_stability",
            "stakeholder_involvement",
            "preferred_platform",
            "development_experience",
            "scalability_needs",
            "performance_requirements",
            "security_requirements",
            "budget_constraints",
            "maintenance_expectations",
            "deployment_preference",
        ):
            value = getattr(self, fname, "")
            setattr(self, fname, sanitize(value or ""))

    def selected_features_list(self) -> list[str]:
        if not self.selected_features:
            return []
        values = [sanitize(v) for v in self.selected_features.split("|")]
        return [v for v in values if v]

    def rules(self) -> list[Rule]:
        return [
            ("project_name", is_non_empty, "Project name is required."),
            ("project_name", lambda v: min_length(v, 2), "Project name is too short."),
            ("project_name", lambda v: max_length(v, 80), "Project name is too long."),
            ("project_type", lambda v: is_in(v, PROJECT_TYPES), "Choose a valid project type."),
            ("selected_features", lambda _v: len(self.selected_features_list()) > 0, "Select at least one feature."),
            (
                "selected_features",
                lambda _v: all(f in FEATURE_OPTIONS for f in self.selected_features_list()),
                "One or more selected features are invalid.",
            ),
            ("project_goal", is_non_empty, "Project goal is required."),
            ("project_goal", lambda v: min_length(v, 12), "Project goal is too short."),
            ("project_goal", lambda v: max_length(v, 1200), "Project goal is too long."),
            ("team_size", lambda v: str(v).isdigit(), "Team size must be numeric."),
            ("team_size", lambda v: int(v) >= 1 if str(v).isdigit() else False, "Team size must be at least 1."),
            ("complexity", lambda v: is_in(v, COMPLEXITY_LEVELS), "Choose a complexity level."),
            ("timeline", lambda v: is_in(v, TIMELINES), "Choose a timeline."),
            (
                "requirements_stability",
                lambda v: is_in(v, REQUIREMENTS_STABILITY_LEVELS),
                "Choose requirements stability.",
            ),
            (
                "stakeholder_involvement",
                lambda v: is_in(v, STAKEHOLDER_INVOLVEMENT_LEVELS),
                "Choose stakeholder involvement.",
            ),
            ("preferred_platform", lambda v: is_in(v, PREFERRED_PLATFORMS), "Choose a preferred platform."),
            (
                "development_experience",
                lambda v: is_in(v, DEVELOPMENT_EXPERIENCE_LEVELS),
                "Choose development experience.",
            ),
            ("scalability_needs", lambda v: is_in(v, SCALABILITY_NEEDS_LEVELS), "Choose scalability needs."),
            (
                "performance_requirements",
                lambda v: is_in(v, PERFORMANCE_REQUIREMENTS_LEVELS),
                "Choose performance requirements.",
            ),
            (
                "security_requirements",
                lambda v: is_in(v, SECURITY_REQUIREMENTS_LEVELS),
                "Choose security requirements.",
            ),
            ("budget_constraints", lambda v: is_in(v, BUDGET_CONSTRAINTS_LEVELS), "Choose budget constraints."),
            (
                "maintenance_expectations",
                lambda v: is_in(v, MAINTENANCE_EXPECTATIONS_LEVELS),
                "Choose maintenance expectations.",
            ),
            ("deployment_preference", lambda v: is_in(v, DEPLOYMENT_PREFERENCES), "Choose deployment preference."),
        ]

    def to_dict(self) -> dict:
        return {
            "project_name": self.project_name,
            "project_type": self.project_type,
            "selected_features": self.selected_features_list(),
            "project_goal": self.project_goal,
            "team_size": self.team_size,
            "complexity": self.complexity,
            "timeline": self.timeline,
            "requirements_stability": self.requirements_stability,
            "stakeholder_involvement": self.stakeholder_involvement,
            "preferred_platform": self.preferred_platform,
            "development_experience": self.development_experience,
            "scalability_needs": self.scalability_needs,
            "performance_requirements": self.performance_requirements,
            "security_requirements": self.security_requirements,
            "budget_constraints": self.budget_constraints,
            "maintenance_expectations": self.maintenance_expectations,
            "deployment_preference": self.deployment_preference,
        }
