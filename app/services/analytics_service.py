"""AnalyticsService — aggregate metrics for the dashboard."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.repositories.analytics_repository import AnalyticsRepository
    from app.repositories.recommendation_repository import RecommendationRepository


@dataclass
class DashboardSnapshot:
    total_recommendations: int
    average_confidence: float
    top_languages: list[tuple[str, int]] = field(default_factory=list)
    top_frameworks: list[tuple[str, int]] = field(default_factory=list)
    top_sdlc: list[tuple[str, int]] = field(default_factory=list)
    weekly_trend: list[tuple[str, int]] = field(default_factory=list)
    insights: list[str] = field(default_factory=list)
    total_feedback: int = 0
    average_rating: float = 0.0


class AnalyticsService:
    def __init__(
        self,
        recommendation_repository: "RecommendationRepository",
        analytics_repository: "AnalyticsRepository",
    ) -> None:
        self.recommendations = recommendation_repository
        self.analytics = analytics_repository

    def snapshot_for_user(self, user_id: int) -> DashboardSnapshot:
        total = self.recommendations.count_for_user(user_id)
        avg = self.recommendations.average_confidence(user_id)
        top_languages = self.recommendations.top_languages(user_id, limit=5)
        top_frameworks = self.recommendations.top_frameworks(user_id, limit=5)
        top_sdlc = self.recommendations.top_sdlc(user_id, limit=5)
        trend = self.recommendations.trend_by_week(user_id, weeks=8)
        insights = self._build_insights(total, avg, top_languages, top_frameworks)

        return DashboardSnapshot(
            total_recommendations=total,
            average_confidence=round(avg, 1),
            top_languages=top_languages,
            top_frameworks=top_frameworks,
            top_sdlc=top_sdlc,
            weekly_trend=trend,
            insights=insights,
        )

    @staticmethod
    def _build_insights(
        total: int,
        avg_confidence: float,
        languages: list[tuple[str, int]],
        frameworks: list[tuple[str, int]],
    ) -> list[str]:
        items: list[str] = []
        if total == 0:
            items.append("Start by generating your first recommendation — try the Recommendation Generator.")
            items.append("StackWise will explain *why* each technology fits your specific project.")
            items.append("Use the AI Chatbot to ask follow-up questions about any recommendation.")
            return items

        if languages:
            top_lang, count = languages[0]
            items.append(f"You've leaned on **{top_lang}** in {count} of your recommendations.")
        if frameworks:
            top_fw, _ = frameworks[0]
            items.append(f"Your most-recommended framework is **{top_fw}** — a strong default.")
        if avg_confidence >= 80:
            items.append(f"Your average confidence ({avg_confidence:.0f}/100) suggests well-defined projects.")
        elif avg_confidence:
            items.append(
                f"Average confidence is {avg_confidence:.0f}/100 — adding more detail to your "
                "project profile usually improves it."
            )
        items.append("Try comparing two past recommendations side-by-side from the History page.")
        return items
