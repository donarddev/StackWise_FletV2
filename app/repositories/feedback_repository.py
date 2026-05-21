"""Feedback repository — persistence for recommendation_feedback rows."""

from __future__ import annotations

from typing import Optional

from app.models.recommendation_feedback import RecommendationFeedback
from app.repositories.base_repository import BaseRepository


class FeedbackRepository(BaseRepository):
    def create(
        self,
        user_id: int,
        recommendation_id: int,
        rating: int,
        comment: str = "",
    ) -> RecommendationFeedback:
        new_id = self.db.execute(
            """
            INSERT INTO recommendation_feedback (
                user_id, recommendation_id, rating, comment
            ) VALUES (%s, %s, %s, %s)
            """,
            (user_id, recommendation_id, int(rating), comment or None),
        )
        row = self.db.fetch_one(
            "SELECT * FROM recommendation_feedback WHERE id = %s LIMIT 1",
            (new_id,),
        )
        return RecommendationFeedback.from_row(row)  # type: ignore[arg-type]

    def find_for_user_and_recommendation(
        self,
        user_id: int,
        recommendation_id: int,
    ) -> Optional[RecommendationFeedback]:
        row = self.db.fetch_one(
            """
            SELECT * FROM recommendation_feedback
            WHERE user_id = %s AND recommendation_id = %s
            LIMIT 1
            """,
            (user_id, recommendation_id),
        )
        return RecommendationFeedback.from_row_optional(row)

    def count_for_user(self, user_id: int) -> int:
        row = self.db.fetch_one(
            "SELECT COUNT(*) AS c FROM recommendation_feedback WHERE user_id = %s",
            (user_id,),
        )
        return int(row["c"]) if row else 0

    def average_rating_for_user(self, user_id: int) -> float:
        row = self.db.fetch_one(
            "SELECT AVG(rating) AS avg_rating FROM recommendation_feedback WHERE user_id = %s",
            (user_id,),
        )
        return float((row or {}).get("avg_rating") or 0.0)
