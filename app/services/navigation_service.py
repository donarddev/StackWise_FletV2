"""NavigationService — thin wrapper around router/page.go for testability.

Controllers/views call this instead of touching ``page.go`` directly so we
can swap navigation strategies (e.g. tab-based, modal stacks) without
spelunking through every page.
"""

from __future__ import annotations

import flet as ft

from app.utils.constants import Routes, recommendation_result_route


class NavigationService:
    def __init__(self, page: ft.Page) -> None:
        self.page = page

    def go(self, route: str) -> None:
        self.page.go(route)

    def to_home(self) -> None:
        self.page.go(Routes.HOME)

    def to_login(self) -> None:
        self.page.go(Routes.LOGIN)

    def to_register(self) -> None:
        self.page.go(Routes.REGISTER)

    def to_dashboard(self) -> None:
        self.page.go(Routes.DASHBOARD)

    def to_recommendation(self) -> None:
        self.page.go(Routes.RECOMMENDATION)

    def to_recommendation_result(self, recommendation_id: int) -> None:
        self.page.go(recommendation_result_route(recommendation_id))

    def to_history(self) -> None:
        self.page.go(Routes.HISTORY)

    def to_chatbot(self) -> None:
        self.page.go(Routes.CHATBOT)

    def to_learning(self) -> None:
        self.page.go(Routes.LEARNING)

    def to_settings(self) -> None:
        self.page.go(Routes.SETTINGS)
