"""Lightweight dependency-injection container.

Wires together repositories, services, and controllers in one place so the
rest of the codebase can depend on abstractions instead of constructing
their own collaborators. Lifecycle is per-page (per ``ft.Page``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property

import flet as ft

from app.config.ai_config import AIConfig, get_ai_config
from app.config.app_config import AppConfig, get_app_config
from app.config.database_config import DatabaseConfig, get_database_config
from app.core.session import Session
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.chatbot_log_repository import ChatbotLogRepository
from app.repositories.learning_repository import LearningRepository
from app.repositories.recommendation_repository import RecommendationRepository
from app.repositories.user_repository import UserRepository
from app.services.alternative_recommendation_service import AlternativeRecommendationService
from app.services.analytics_service import AnalyticsService
from app.services.authentication_service import AuthenticationService
from app.services.chatbot_service import ChatbotService
from app.services.confidence_score_service import ConfidenceScoreService
from app.services.database_service import DatabaseService
from app.services.explanation_service import ExplanationService
from app.services.recommendation_service import RecommendationService


@dataclass
class Container:
    """Per-page container of singletons.

    Cached properties make this thread-safe-enough for Flet's single-page model
    while remaining trivially mockable in tests (just construct a Container with
    fakes and override attributes).
    """

    page: ft.Page

    app_config: AppConfig = field(default_factory=get_app_config)
    db_config: DatabaseConfig = field(default_factory=get_database_config)
    ai_config: AIConfig = field(default_factory=get_ai_config)

    # ---------- infrastructure ----------

    @cached_property
    def database(self) -> DatabaseService:
        service = DatabaseService(self.db_config)
        service.connect()
        return service

    @cached_property
    def session(self) -> Session:
        return Session(page=self.page)

    # ---------- repositories ----------

    @cached_property
    def user_repository(self) -> UserRepository:
        return UserRepository(self.database)

    @cached_property
    def recommendation_repository(self) -> RecommendationRepository:
        return RecommendationRepository(self.database)

    @cached_property
    def analytics_repository(self) -> AnalyticsRepository:
        return AnalyticsRepository(self.database)

    @cached_property
    def chatbot_log_repository(self) -> ChatbotLogRepository:
        return ChatbotLogRepository(self.database)

    @cached_property
    def learning_repository(self) -> LearningRepository:
        return LearningRepository(self.database)

    # ---------- services ----------

    @cached_property
    def authentication_service(self) -> AuthenticationService:
        return AuthenticationService(self.user_repository)

    @cached_property
    def confidence_score_service(self) -> ConfidenceScoreService:
        return ConfidenceScoreService()

    @cached_property
    def alternative_recommendation_service(self) -> AlternativeRecommendationService:
        return AlternativeRecommendationService()

    @cached_property
    def explanation_service(self) -> ExplanationService:
        return ExplanationService()

    @cached_property
    def chatbot_service(self) -> ChatbotService:
        return ChatbotService(self.ai_config, self.chatbot_log_repository)

    @cached_property
    def recommendation_service(self) -> RecommendationService:
        return RecommendationService(
            recommendation_repository=self.recommendation_repository,
            confidence_score_service=self.confidence_score_service,
            alternative_service=self.alternative_recommendation_service,
            explanation_service=self.explanation_service,
            chatbot_service=self.chatbot_service,
        )

    @cached_property
    def analytics_service(self) -> AnalyticsService:
        return AnalyticsService(
            recommendation_repository=self.recommendation_repository,
            analytics_repository=self.analytics_repository,
        )
