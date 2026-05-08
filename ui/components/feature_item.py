"""FeatureItem — landing feature highlight row."""

from __future__ import annotations

import flet as ft

from ui.themes.app_theme import Colors, Radii, Spacing, Typography


def feature_item(*, icon: str, title: str, body: str) -> ft.Control:
    return ft.Row(
        spacing=Spacing.md,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[
            ft.Container(
                width=36,
                height=36,
                border_radius=10,
                bgcolor=ft.colors.with_opacity(0.12, Colors.primary),
                border=ft.border.all(1, ft.colors.with_opacity(0.55, Colors.border)),
                alignment=ft.alignment.center,
                content=ft.Icon(icon, size=18, color=Colors.primary_glow),
            ),
            ft.Column(
                spacing=3,
                tight=True,
                expand=True,
                controls=[
                    ft.Text(title, style=Typography.subheading(size=14)),
                    ft.Text(body, style=Typography.body(size=12.5)),
                ],
            ),
        ],
    )

