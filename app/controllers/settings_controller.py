"""SettingsController."""

from __future__ import annotations

import flet as ft

from app.controllers._layout_helper import wrap_with_layout
from app.controllers.base_controller import BaseController
from app.utils.constants import Routes
from ui.components.toast import show_toast
from ui.dialogs.confirm_dialog import show_confirmation_dialog, show_sign_out_dialog
from ui.pages.settings_page import build_settings_page
from ui.theme import get_theme, is_dark_mode, toggle_theme_mode


class SettingsController(BaseController):
    def build(self) -> ft.Control:
        user = self.container.session.user
        assert user is not None

        is_available = self.container.chatbot_service.is_available()

        def perform_logout() -> None:
            self.container.session.logout()
            self.navigation.to_home()

        def perform_clear_chat() -> None:
            self.container.chatbot_log_repository.clear_for_user(user.id)
            show_toast(self.page, "Chat history cleared.", kind="success")

        def on_logout(_e: ft.ControlEvent) -> None:
            show_sign_out_dialog(
                self.page,
                theme=get_theme(is_dark_mode(self.page)),
                on_confirm=perform_logout,
            )

        def on_clear_chat(_e: ft.ControlEvent) -> None:
            show_confirmation_dialog(
                self.page,
                theme=get_theme(is_dark_mode(self.page)),
                title="Clear chat history?",
                message=(
                    "Are you sure you want to clear saved chatbot conversations? "
                    "Recommendation history will remain."
                ),
                icon=ft.icons.DELETE_SWEEP_ROUNDED,
                confirm_label="Clear chat history",
                confirm_icon=ft.icons.DELETE_SWEEP_ROUNDED,
                confirm_kind="warning",
                on_confirm=perform_clear_chat,
            )

        def on_theme_toggle(_e: ft.ControlEvent) -> None:
            toggle_theme_mode(self.page)
            router = getattr(self.page, "_stackwise_router", None)
            if router is not None:
                router.reload_current_view()

        theme = get_theme(is_dark_mode(self.page))
        body = build_settings_page(
            theme=theme,
            user=user,
            ai_config=self.container.ai_config,
            is_ollama_available=is_available,
            is_dark_mode_enabled=is_dark_mode(self.page),
            on_theme_toggle=on_theme_toggle,
            on_logout=on_logout,
            on_clear_chat=on_clear_chat,
        )
        return wrap_with_layout(self, current_route=Routes.SETTINGS, body=body, theme=theme)
