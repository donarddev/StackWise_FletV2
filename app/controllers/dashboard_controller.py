"""DashboardController."""

from __future__ import annotations

import flet as ft

from app.controllers._layout_helper import wrap_with_layout
from app.controllers.base_controller import BaseController
from app.models.recommendation import Recommendation
from app.utils.constants import Routes
from ui.dialogs.recommendation_detail_dialog import build_recommendation_detail_dialog
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
        user = self.container.session.user
        if user is None:
            return
        self.container.recommendation_repository.add_history(user.id, rec.id, "viewed")
        dialog = build_recommendation_detail_dialog(rec, on_close=lambda _e: self._close_dialog())
        self._open_dialog(dialog)

    def _regenerate(self, rec: Recommendation) -> None:
        user = self.container.session.user
        if user is None:
            return
        new_rec = self.container.recommendation_service.regenerate(user.id, rec.id)
        if new_rec is not None:
            from ui.components.toast import show_toast
            show_toast(self.page, "Recommendation regenerated.", kind="success")
            self.navigation.to_dashboard()

    # ---------- dialog plumbing ----------

    def _open_dialog(self, dialog: ft.AlertDialog) -> None:
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _close_dialog(self) -> None:
        if self.page.dialog is not None:
            self.page.dialog.open = False
            self.page.update()
