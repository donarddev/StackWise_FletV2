"""RecommendationRequest — validates the project profile form."""

from __future__ import annotations

from dataclasses import dataclass

from app.requests.base_request import BaseRequest, Rule
from app.utils.constants import (
    COMPLEXITY_LEVELS,
    EXPERIENCE_LEVELS,
    PLATFORMS,
    PROJECT_GOALS,
    PROJECT_TYPES,
    SCALABILITY_LEVELS,
    SECURITY_LEVELS,
    TEAM_SIZES,
    TIMELINES,
)
from app.utils.validators import is_in, is_non_empty, max_length, min_length, sanitize


@dataclass
class RecommendationRequest(BaseRequest):
    project_name: str = ""
    project_type: str = ""
    project_goal: str = ""
    complexity: str = ""
    team_size: str = ""
    timeline: str = ""
    scalability: str = ""
    security: str = ""
    platform: str = ""
    experience: str = ""

    def sanitize(self) -> None:
        for fname in (
            "project_name",
            "project_type",
            "project_goal",
            "complexity",
            "team_size",
            "timeline",
            "scalability",
            "security",
            "platform",
            "experience",
        ):
            value = getattr(self, fname, "")
            setattr(self, fname, sanitize(value or ""))

    def rules(self) -> list[Rule]:
        return [
            ("project_name", is_non_empty, "Project name is required."),
            ("project_name", lambda v: min_length(v, 2), "Project name is too short."),
            ("project_name", lambda v: max_length(v, 80), "Project name is too long."),
            ("project_type", lambda v: is_in(v, PROJECT_TYPES), "Choose a valid project type."),
            ("project_goal", lambda v: is_in(v, PROJECT_GOALS), "Choose a valid project goal."),
            ("complexity", lambda v: is_in(v, COMPLEXITY_LEVELS), "Choose a complexity level."),
            ("team_size", lambda v: is_in(v, TEAM_SIZES), "Choose a team size."),
            ("timeline", lambda v: is_in(v, TIMELINES), "Choose a timeline."),
            ("scalability", lambda v: is_in(v, SCALABILITY_LEVELS), "Choose scalability level."),
            ("security", lambda v: is_in(v, SECURITY_LEVELS), "Choose security level."),
            ("platform", lambda v: is_in(v, PLATFORMS), "Choose a target platform."),
            ("experience", lambda v: is_in(v, EXPERIENCE_LEVELS), "Choose an experience level."),
        ]

    def to_dict(self) -> dict:
        return {
            "project_name": self.project_name,
            "project_type": self.project_type,
            "project_goal": self.project_goal,
            "complexity": self.complexity,
            "team_size": self.team_size,
            "timeline": self.timeline,
            "scalability": self.scalability,
            "security": self.security,
            "platform": self.platform,
            "experience": self.experience,
        }
