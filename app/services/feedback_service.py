"""FeedbackService — validation and submission rules for recommendation feedback."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from app.utils.logger import get_logger

if TYPE_CHECKING:
    from app.models.recommendation_feedback import RecommendationFeedback
    from app.repositories.feedback_repository import FeedbackRepository
    from app.repositories.recommendation_repository import RecommendationRepository


@dataclass
class FeedbackSubmitResult:
    success: bool
    message: str
    feedback: Optional["RecommendationFeedback"] = None


log = get_logger(__name__)


class FeedbackService:
    def __init__(
        self,
        feedback_repository: "FeedbackRepository",
        recommendation_repository: "RecommendationRepository",
    ) -> None:
        self._feedback = feedback_repository
        self._recommendations = recommendation_repository

    def get_for_recommendation(
        self,
        user_id: int,
        recommendation_id: int,
    ) -> Optional["RecommendationFeedback"]:
        return self._feedback.find_for_user_and_recommendation(user_id, recommendation_id)

    def submit(
        self,
        user_id: int,
        recommendation_id: int,
        rating: int | str | None,
        comment: str = "",
    ) -> FeedbackSubmitResult:
        rec = self._recommendations.find_by_id(recommendation_id)
        if rec is None or rec.user_id != user_id:
            return FeedbackSubmitResult(
                success=False,
                message="Recommendation not found.",
            )

        existing = self._feedback.find_for_user_and_recommendation(
            user_id, recommendation_id
        )
        if existing is not None:
            return FeedbackSubmitResult(
                success=False,
                message="You have already submitted feedback for this recommendation.",
            )

        try:
            rating_int = int(rating) if rating is not None else 0
        except (TypeError, ValueError):
            rating_int = 0

        if rating_int < 1 or rating_int > 5:
            return FeedbackSubmitResult(
                success=False,
                message="Please select a rating before submitting.",
            )

        text = (comment or "").strip()
        if len(text) > 2000:
            return FeedbackSubmitResult(
                success=False,
                message="Comment is too long (maximum 2000 characters).",
            )

        try:
            saved = self._feedback.create(
                user_id=user_id,
                recommendation_id=recommendation_id,
                rating=rating_int,
                comment=text,
            )
        except Exception:
            log.exception(
                "Failed to save feedback user_id=%s recommendation_id=%s",
                user_id,
                recommendation_id,
            )
            return FeedbackSubmitResult(
                success=False,
                message="Feedback could not be saved. Please try again.",
            )

        return FeedbackSubmitResult(
            success=True,
            message="Feedback submitted successfully.",
            feedback=saved,
        )

    def stats_for_user(self, user_id: int) -> tuple[int, float]:
        return (
            self._feedback.count_for_user(user_id),
            round(self._feedback.average_rating_for_user(user_id), 1),
        )
