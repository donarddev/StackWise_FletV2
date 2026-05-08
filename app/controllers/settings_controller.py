"""SettingsController."""

from __future__ import annotations

import flet as ft

from app.controllers._layout_helper import wrap_with_layout
from app.controllers.base_controller import BaseController
from app.utils.constants import Routes
from ui.components.toast import show_toast
from ui.pages.settings_page import build_settings_page


class SettingsController(BaseController):
    def build(self) -> ft.Control:
        user = self.container.session.user
        assert user is not None

        is_available = self.container.chatbot_service.is_available()

        def on_logout(_e: ft.ControlEvent) -> None:
            self.container.session.logout()
            self.navigation.to_home()

        def on_clear_chat(_e: ft.ControlEvent) -> None:
            self.container.chatbot_log_repository.clear_for_user(user.id)
            show_toast(self.page, "Chat history cleared.", kind="success")

        body = build_settings_page(
            user=user,
            ai_config=self.container.ai_config,
            is_ollama_available=is_available,
            on_logout=on_logout,
            on_clear_chat=on_clear_chat,
        )
        return wrap_with_layout(self, current_route=Routes.SETTINGS, body=body)
