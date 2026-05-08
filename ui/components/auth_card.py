"""AuthCard — consistent premium form container for auth pages."""

from __future__ import annotations

import flet as ft

from ui.components.glass_card import glass_card
from ui.themes.app_theme import Colors, Spacing


def auth_card(content: ft.Control, *, width: int = 460) -> ft.Control:
    return glass_card(
        content=content,
        width=width,
        padding=ft.padding.symmetric(horizontal=36, vertical=30),
        glow=True,
        border_color=ft.colors.with_opacity(0.85, Colors.border),
    )

