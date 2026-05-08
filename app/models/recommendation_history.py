"""RecommendationHistory entry — an audit row for actions on a recommendation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping

from app.helpers.date_helper import from_db


@dataclass
class RecommendationHistory:
    id: int
    user_id: int
    recommendation_id: int
    action: str  # 'created' | 'viewed' | 'regenerated' | 'compared'
    created_at: datetime

    @staticmethod
    def from_row(row: Mapping[str, Any]) -> "RecommendationHistory":
        return RecommendationHistory(
            id=int(row["id"]),
            user_id=int(row["user_id"]),
            recommendation_id=int(row["recommendation_id"]),
            action=row["action"],
            created_at=from_db(row["created_at"]),
        )
