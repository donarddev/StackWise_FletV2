"""Recommendation history operations — soft delete and restore."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from app.models.recommendation import Recommendation
from app.utils.logger import get_logger

if TYPE_CHECKING:
    from app.repositories.recommendation_repository import RecommendationRepository

log = get_logger(__name__)


class RecommendationHistoryService:
    def __init__(self, recommendation_repository: "RecommendationRepository") -> None:
        self._repo = recommendation_repository

    def get_active_recommendations(
        self, user_id: int, *, limit: int = 500
    ) -> list[Recommendation]:
        return self._repo.list_active_for_user(user_id, limit=limit)

    def get_deleted_recommendations(
        self, user_id: int, *, limit: int = 500
    ) -> list[Recommendation]:
        return self._repo.list_deleted_for_user(user_id, limit=limit)

    def soft_delete(self, user_id: int, recommendation_id: int) -> bool:
        rec = self._repo.find_by_id(recommendation_id)
        if rec is None or rec.user_id != user_id:
            return False
        if rec.deleted_at is not None:
            return False
        try:
            updated = self._repo.soft_delete(recommendation_id, user_id)
            if updated:
                self._repo.add_history(user_id, recommendation_id, "soft_deleted")
            return updated
        except Exception:
            log.exception(
                "soft_delete failed user_id=%s recommendation_id=%s",
                user_id,
                recommendation_id,
            )
            raise

    def restore(self, user_id: int, recommendation_id: int) -> bool:
        rec = self._repo.find_by_id(recommendation_id)
        if rec is None or rec.user_id != user_id:
            return False
        if rec.deleted_at is None:
            return False
        try:
            updated = self._repo.restore(recommendation_id, user_id)
            if updated:
                self._repo.add_history(user_id, recommendation_id, "restored")
            return updated
        except Exception:
            log.exception(
                "restore failed user_id=%s recommendation_id=%s",
                user_id,
                recommendation_id,
            )
            raise
