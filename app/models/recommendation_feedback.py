"""Recommendation feedback entity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping, Optional

from app.helpers.date_helper import from_db


@dataclass
class RecommendationFeedback:
    id: int
    recommendation_id: int
    user_id: int
    rating: int
    comment: str
    created_at: datetime

    @staticmethod
    def from_row(row: Mapping[str, Any]) -> "RecommendationFeedback":
        return RecommendationFeedback(
            id=int(row["id"]),
            recommendation_id=int(row["recommendation_id"]),
            user_id=int(row["user_id"]),
            rating=int(row["rating"]),
            comment=str(row.get("comment") or ""),
            created_at=from_db(row["created_at"]),
        )

    @staticmethod
    def from_row_optional(row: Optional[Mapping[str, Any]]) -> Optional["RecommendationFeedback"]:
        return RecommendationFeedback.from_row(row) if row is not None else None
