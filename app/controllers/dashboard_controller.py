"""DashboardController."""

from __future__ import annotations

import flet as ft

from app.controllers._layout_helper import wrap_with_layout
from app.controllers.base_controller import BaseController
from app.controllers.recommendation_controller import generate_recommendation_from_request
from app.models.recommendation import Recommendation
from app.utils.constants import (
    Routes,
    SESSION_RECOMMENDATION_INPUT,
    SESSION_RECOMMENDATION_RESULT,
    SESSION_SELECTED_RECOMMENDATION_ID,
    recommendation_result_route,
)
from ui.components.toast import show_toast
from ui.pages.dashboard_page import build_dashboard_page
from ui.theme import get_theme, is_dark_mode


class DashboardController(BaseController):
    def build(self) -> ft.Control:
        user = self.container.session.user
        assert user is not None

        snapshot = self.container.analytics_service.snapshot_for_user(user.id)
        recent = self.container.recommendation_repository.latest_for_user(user.id, limit=5)

        theme = get_theme(is_dark_mode(self.page))
        body = build_dashboard_page(
            user=user,
            snapshot=snapshot,
            recent=recent,
            on_new_recommendation=lambda _e: self.navigation.to_recommendation(),
            on_open_history=lambda _e: self.navigation.to_history(),
            on_open_chatbot=lambda _e: self.navigation.to_chatbot(),
            on_view_recommendation=self._show_detail,
            on_regenerate=self._regenerate,
            theme=theme,
        )

        return wrap_with_layout(self, current_route=Routes.DASHBOARD, body=body, theme=theme)

    def _show_detail(self, rec: Recommendation) -> None:
        self.navigation.to_recommendation_result(rec.id)

    def _regenerate(self, rec: Recommendation) -> None:
        user = self.container.session.user
        if user is None:
            show_toast(self.page, "Please sign in again.", kind="warning")
            return
        input_data = (
            self.container.recommendation_persistence.input_data_from_recommendation(rec)
        )
        response = generate_recommendation_from_request(input_data)
        if not response.get("success"):
            show_toast(
                self.page,
                response.get("error") or "Regeneration could not be completed.",
                kind="warning",
            )
            return
        try:
            new_rec = self.container.recommendation_persistence.save_engine_result(
                user.id,
                input_data,
                response["data"],
            )
        except Exception:
            show_toast(
                self.page,
                "Regeneration succeeded but could not be saved to the database.",
                kind="warning",
            )
            return
        self.page.session.set(SESSION_RECOMMENDATION_INPUT, input_data)
        self.page.session.set(SESSION_RECOMMENDATION_RESULT, response["data"])
        self.page.session.set(SESSION_SELECTED_RECOMMENDATION_ID, new_rec.id)
        show_toast(self.page, "Recommendation regenerated.", kind="success")
        self.page.go(recommendation_result_route(new_rec.id))
