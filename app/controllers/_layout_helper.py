"""Internal helper for controllers — wraps page bodies with AppLayout."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, Optional

import flet as ft

from ui.layouts.app_layout import app_layout
from ui.theme import get_theme, is_dark_mode

if TYPE_CHECKING:
    from app.controllers.base_controller import BaseController


def wrap_with_layout(
    controller: "BaseController",
    *,
    current_route: str,
    body: ft.Control,
    topbar_actions: Optional[list[ft.Control]] = None,
    theme: Optional[Mapping[str, Any]] = None,
) -> ft.Control:
    user = controller.container.session.user
    if user is None:
        return body  # router would have redirected — this is a safety net

    t = theme if theme is not None else get_theme(is_dark_mode(controller.page))

    return app_layout(
        page=controller.page,
        current_route=current_route,
        user_name=user.full_name,
        user_email=user.email,
        on_navigate=controller.navigation.go,
        on_logout=lambda _e: _logout(controller),
        body=body,
        topbar_actions=topbar_actions,
        theme=t,
    )


def _logout(controller: "BaseController") -> None:
    controller.container.session.logout()
    controller.navigation.to_home()
