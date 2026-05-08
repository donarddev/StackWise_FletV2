"""StatCard — analytics tile used on the dashboard."""

from __future__ import annotations

from typing import Optional

import flet as ft

from ui.components.glass_card import glass_card
from ui.themes.app_theme import Colors, Spacing, Typography


def stat_card(
    *,
    title: str,
    value: str,
    subtitle: Optional[str] = None,
    icon: str = ft.icons.AUTO_AWESOME_OUTLINED,
    accent: str = Colors.primary,
) -> ft.Control:
    body = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Icon(icon, color=accent, size=20),
                        bgcolor=ft.colors.with_opacity(0.12, accent),
                        padding=10,
                        border_radius=12,
                    ),
                    ft.Text(title, style=Typography.caption()),
                ],
                spacing=Spacing.md,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Container(height=Spacing.md),
            ft.Text(value, style=Typography.display(size=30)),
            ft.Text(subtitle or "", style=Typography.body()),
        ],
        spacing=2,
    )
    return glass_card(body)
