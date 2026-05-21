"""Recommendation entity."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping, Optional

from app.helpers.date_helper import from_db


@dataclass
class Recommendation:
    id: int
    user_id: int

    # request snapshot
    project_name: str
    project_type: str
    project_goal: str
    complexity: str
    team_size: str
    timeline: str
    scalability: str
    security: str
    platform: str
    experience: str

    # result
    recommended_language: str
    recommended_framework: str
    recommended_sdlc: str
    confidence_score: int
    explanation: dict = field(default_factory=dict)
    alternatives: dict = field(default_factory=dict)
    project_profile: dict = field(default_factory=dict)

    created_at: datetime = field(default_factory=datetime.now)
    deleted_at: Optional[datetime] = None

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    @staticmethod
    def from_row(row: Mapping[str, Any]) -> "Recommendation":
        return Recommendation(
            id=int(row["id"]),
            user_id=int(row["user_id"]),
            project_name=row["project_name"],
            project_type=row["project_type"],
            project_goal=row["project_goal"],
            complexity=row["complexity"],
            team_size=row["team_size"],
            timeline=row["timeline"],
            scalability=row["scalability"],
            security=row["security"],
            platform=row["platform"],
            experience=row["experience"],
            recommended_language=row["recommended_language"],
            recommended_framework=row["recommended_framework"],
            recommended_sdlc=row["recommended_sdlc"],
            confidence_score=int(row["confidence_score"]),
            explanation=json.loads(row["explanation_json"] or "{}"),
            alternatives=json.loads(row["alternatives_json"] or "{}"),
            project_profile=json.loads(row.get("project_profile_json") or "{}"),
            created_at=from_db(row["created_at"]),
            deleted_at=(
                from_db(row["deleted_at"])
                if row.get("deleted_at") is not None
                else None
            ),
        )

    @staticmethod
    def from_row_optional(row: Optional[Mapping[str, Any]]) -> Optional["Recommendation"]:
        return Recommendation.from_row(row) if row is not None else None
