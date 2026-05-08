"""NavRail — sidebar navigation used by AppLayout."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import flet as ft

from app.utils.constants import BRAND_INITIALS, BRAND_NAME, Routes
from ui.themes.app_theme import Colors, Radii, Spacing, Typography


@dataclass
class NavItem:
    route: str
    label: str
    icon: str
    icon_selected: str


NAV_ITEMS: list[NavItem] = [
    NavItem(Routes.DASHBOARD, "Dashboard", ft.icons.SPACE_DASHBOARD_OUTLINED, ft.icons.SPACE_DASHBOARD),
    NavItem(Routes.RECOMMENDATION, "Recommendation", ft.icons.AUTO_AWESOME_OUTLINED, ft.icons.AUTO_AWESOME),
    NavItem(Routes.HISTORY, "History", ft.icons.HISTORY_OUTLINED, ft.icons.HISTORY),
    NavItem(Routes.CHATBOT, "AI Chatbot", ft.icons.CHAT_BUBBLE_OUTLINE, ft.icons.CHAT_BUBBLE),
    NavItem(Routes.LEARNING, "Learning Hub", ft.icons.MENU_BOOK_OUTLINED, ft.icons.MENU_BOOK),
    NavItem(Routes.SETTINGS, "Settings", ft.icons.SETTINGS_OUTLINED, ft.icons.SETTINGS),
]


def nav_rail(
    *,
    current_route: str,
    on_navigate: Callable[[str], None],
    on_logout: Callable[[ft.ControlEvent], None],
    user_name: str,
    user_email: str,
) -> ft.Container:
    items: list[ft.Control] = []
    for it in NAV_ITEMS:
        items.append(_nav_item(it, selected=(it.route == current_route), on_navigate=on_navigate))

    brand = ft.Row(
        controls=[
            ft.Container(
                content=ft.Text(
                    BRAND_INITIALS, size=14, weight=ft.FontWeight.W_800,
                    color=Colors.text_primary, text_align=ft.TextAlign.CENTER,
                ),
                width=38, height=38,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left, end=ft.alignment.bottom_right,
                    colors=[Colors.primary, Colors.accent_cyan],
                ),
                border_radius=12,
                alignment=ft.alignment.center,
            ),
            ft.Column(
                controls=[
                    ft.Text(BRAND_NAME, size=15, weight=ft.FontWeight.W_700, color=Colors.text_primary),
                    ft.Text("AI workspace", size=11, color=Colors.text_muted),
                ],
                spacing=0, tight=True,
            ),
        ],
        spacing=Spacing.md, vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    user_block = ft.Container(
        padding=Spacing.md,
        bgcolor=Colors.surface,
        border=ft.border.all(1, Colors.border),
        border_radius=Radii.md,
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(
                        (user_name[:1] or "U").upper(),
                        size=14, weight=ft.FontWeight.W_700, color=Colors.text_primary,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    width=34, height=34,
                    bgcolor=Colors.surface_3,
                    border_radius=10,
                    alignment=ft.alignment.center,
                ),
                ft.Column(
                    controls=[
                        ft.Text(user_name, size=13, weight=ft.FontWeight.W_600, color=Colors.text_primary),
                        ft.Text(user_email, size=11, color=Colors.text_muted),
                    ],
                    spacing=0, tight=True, expand=True,
                ),
                ft.IconButton(
                    icon=ft.icons.LOGOUT_ROUNDED,
                    icon_size=18,
                    icon_color=Colors.text_secondary,
                    tooltip="Sign out",
                    on_click=on_logout,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=Spacing.md,
        ),
    )

    return ft.Container(
        width=260,
        bgcolor=Colors.surface,
        border=ft.border.only(right=ft.BorderSide(1, Colors.border)),
        padding=ft.padding.symmetric(horizontal=18, vertical=22),
        content=ft.Column(
            controls=[
                brand,
                ft.Container(height=Spacing.xl),
                ft.Text("NAVIGATION", style=Typography.caption()),
                ft.Container(height=Spacing.sm),
                *items,
                ft.Container(expand=1),
                user_block,
            ],
            spacing=4,
            expand=True,
        ),
    )


def _nav_item(item: NavItem, *, selected: bool, on_navigate: Callable[[str], None]) -> ft.Control:
    bgcolor = ft.colors.with_opacity(0.16, Colors.primary) if selected else "transparent"
    text_color = Colors.text_primary if selected else Colors.text_secondary
    icon_color = Colors.primary_glow if selected else Colors.text_secondary

    return ft.Container(
        on_click=lambda _e: on_navigate(item.route),
        ink=True,
        bgcolor=bgcolor,
        border_radius=Radii.md,
        padding=ft.padding.symmetric(horizontal=12, vertical=10),
        content=ft.Row(
            controls=[
                ft.Icon(item.icon_selected if selected else item.icon, size=18, color=icon_color),
                ft.Text(item.label, size=13.5, weight=ft.FontWeight.W_600, color=text_color),
                ft.Container(expand=1),
                *( [ft.Container(width=4, height=18, bgcolor=Colors.primary, border_radius=2)] if selected else [] ),
            ],
            spacing=Spacing.md,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )
