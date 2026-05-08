"""AppLayout — authenticated shell: sidebar + topbar + scrollable content."""

from __future__ import annotations

from typing import Callable, Optional

import flet as ft

from app.utils.constants import BRAND_NAME
from ui.components.nav_rail import nav_rail
from ui.themes.app_theme import Colors, Gradients, Radii, Spacing, Typography


def app_layout(
    *,
    current_route: str,
    user_name: str,
    user_email: str,
    on_navigate: Callable[[str], None],
    on_logout: Callable[[ft.ControlEvent], None],
    body: ft.Control,
    topbar_actions: Optional[list[ft.Control]] = None,
) -> ft.Control:
    sidebar = nav_rail(
        current_route=current_route,
        on_navigate=on_navigate,
        on_logout=on_logout,
        user_name=user_name,
        user_email=user_email,
    )

    topbar = ft.Container(
        height=64,
        bgcolor=ft.colors.with_opacity(0.65, Colors.surface),
        border=ft.border.only(bottom=ft.BorderSide(1, Colors.border)),
        padding=ft.padding.symmetric(horizontal=Spacing.xxl, vertical=Spacing.md),
        content=ft.Row(
            controls=[
                ft.Row(
                    spacing=Spacing.sm,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=8, height=8, border_radius=999,
                            gradient=ft.LinearGradient(
                                begin=ft.alignment.top_left, end=ft.alignment.bottom_right,
                                colors=[Colors.primary, Colors.accent_cyan],
                            ),
                        ),
                        ft.Text(BRAND_NAME, size=13, weight=ft.FontWeight.W_700, color=Colors.text_primary),
                        ft.Container(width=Spacing.md),
                        ft.Text(
                            _route_breadcrumb(current_route),
                            style=Typography.caption(),
                        ),
                    ],
                ),
                ft.Container(expand=1),
                ft.Row(
                    spacing=Spacing.md,
                    controls=topbar_actions or [],
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    content_area = ft.Container(
        expand=True,
        padding=ft.padding.only(left=Spacing.xxxl, right=Spacing.xxxl, top=Spacing.xxl, bottom=Spacing.xxl),
        content=ft.Column(
            scroll=ft.ScrollMode.ADAPTIVE,
            controls=[body],
            expand=True,
        ),
    )

    main_column = ft.Column(
        controls=[topbar, content_area],
        spacing=0,
        expand=True,
    )

    aura = ft.Container(
        width=420, height=420,
        gradient=ft.RadialGradient(
            center=ft.alignment.center,
            radius=0.9,
            colors=["#8b5cf633", "#020617"],
        ),
        border_radius=999,
        right=-180, top=-160,
    )

    layout_row = ft.Row(
        controls=[sidebar, main_column],
        spacing=0, expand=True,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )

    background = ft.Container(
        expand=True,
        bgcolor=Colors.background,
        content=ft.Stack(
            controls=[
                aura,
                layout_row,
            ],
            expand=True,
        ),
    )

    return background


def _route_breadcrumb(route: str) -> str:
    crumb = route.strip("/").replace("-", " ").title() or "Dashboard"
    return f"  /  {crumb}"
