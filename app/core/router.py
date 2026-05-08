"""Application router.

Routes are declarative ``(path -> controller_factory)`` pairs. Controllers
are responsible for building the actual page view, but the router handles
auth gating, route resolution, and transition orchestration.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional

import flet as ft

from app.controllers.auth_controller import AuthController
from app.controllers.chatbot_controller import ChatbotController
from app.controllers.dashboard_controller import DashboardController
from app.controllers.history_controller import HistoryController
from app.controllers.learning_controller import LearningController
from app.controllers.public_controller import PublicController
from app.controllers.recommendation_controller import RecommendationController
from app.controllers.settings_controller import SettingsController
from app.core.container import Container
from app.utils.constants import Routes
from app.utils.logger import get_logger

log = get_logger(__name__)


PUBLIC_ROUTES = {Routes.HOME, Routes.LOGIN, Routes.REGISTER}


@dataclass
class RouteResolution:
    builder: Callable[[], ft.Control]
    requires_auth: bool


class Router:
    def __init__(self, page: ft.Page, container: Container) -> None:
        self.page = page
        self.container = container

        self.auth_controller = AuthController(page, container)
        self.public_controller = PublicController(page, container)
        self.dashboard_controller = DashboardController(page, container)
        self.recommendation_controller = RecommendationController(page, container)
        self.history_controller = HistoryController(page, container)
        self.chatbot_controller = ChatbotController(page, container)
        self.learning_controller = LearningController(page, container)
        self.settings_controller = SettingsController(page, container)

        self._routes: Dict[str, RouteResolution] = {
            Routes.HOME: RouteResolution(self.public_controller.build, False),
            Routes.LOGIN: RouteResolution(self.auth_controller.build_login, False),
            Routes.REGISTER: RouteResolution(self.auth_controller.build_register, False),
            Routes.DASHBOARD: RouteResolution(self.dashboard_controller.build, True),
            Routes.RECOMMENDATION: RouteResolution(self.recommendation_controller.build, True),
            Routes.HISTORY: RouteResolution(self.history_controller.build, True),
            Routes.CHATBOT: RouteResolution(self.chatbot_controller.build, True),
            Routes.LEARNING: RouteResolution(self.learning_controller.build, True),
            Routes.SETTINGS: RouteResolution(self.settings_controller.build, True),
        }

    # ---------- lifecycle ----------

    def attach(self) -> None:
        self.page.on_route_change = self._on_route_change
        self.page.on_view_pop = self._on_view_pop

    def start(self, initial: Optional[str] = None) -> None:
        target = initial or self._initial_route()
        self.page.go(target)

    def navigate(self, route: str) -> None:
        self.page.go(route)

    # ---------- internals ----------

    def _initial_route(self) -> str:
        if self.container.session.is_authenticated:
            return Routes.DASHBOARD
        return Routes.HOME

    def _on_route_change(self, e: ft.RouteChangeEvent) -> None:
        target = e.route or Routes.HOME
        resolution = self._routes.get(target)

        if resolution is None:
            log.warning("Unknown route '%s', redirecting to dashboard.", target)
            self.page.go(self._initial_route())
            return

        if resolution.requires_auth and not self.container.session.is_authenticated:
            log.info("Route '%s' requires auth — redirecting to login.", target)
            self.page.go(Routes.HOME)
            return

        if not resolution.requires_auth and self.container.session.is_authenticated:
            self.page.go(Routes.DASHBOARD)
            return

        view = ft.View(
            route=target,
            padding=0,
            bgcolor=None,
            controls=[resolution.builder()],
        )
        self.page.views.clear()
        self.page.views.append(view)
        self.page.update()

    def _on_view_pop(self, e: ft.ViewPopEvent) -> None:
        if len(self.page.views) <= 1:
            return
        self.page.views.pop()
        top = self.page.views[-1]
        self.page.go(top.route or self._initial_route())
