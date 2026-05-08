"""AuthBrandHeader — centered logo + wordmark for auth forms."""

from __future__ import annotations

import flet as ft

from app.utils.constants import BRAND_NAME
from ui.components.brand_logo import brand_icon
from ui.themes.app_theme import Colors, Spacing, Typography


def auth_brand_header() -> ft.Control:
    return ft.Column(
        spacing=Spacing.md,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            brand_icon(size=62, radius=18),
            ft.Text(
                spans=[
                    ft.TextSpan("StackWise ", style=ft.TextStyle(color="#f5f7ff")),
                    ft.TextSpan(
                        "AI",
                        style=ft.TextStyle(
                            color="#6FE8FF",
                            weight=ft.FontWeight.W_800,
                            shadow=ft.BoxShadow(
                                blur_radius=14,
                                spread_radius=0,
                                color=ft.colors.with_opacity(0.26, "#6FE8FF"),
                                offset=ft.Offset(0, 0),
                            ),
                        ),
                    ),
                ],
                style=Typography.heading(size=31, weight=ft.FontWeight.W_800),
                text_align=ft.TextAlign.CENTER,
            ),
        ],
    )
