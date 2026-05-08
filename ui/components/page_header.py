"""PageHeader — page title block with eyebrow tag and optional CTA."""

from __future__ import annotations

from typing import Optional

import flet as ft

from ui.themes.app_theme import Colors, Radii, Spacing, Typography


def page_header(
    *,
    eyebrow: str,
    title: str,
    subtitle: Optional[str] = None,
    trailing: Optional[ft.Control] = None,
) -> ft.Row:
    eyebrow_pill = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.icons.AUTO_AWESOME, size=12, color=Colors.primary_glow),
                ft.Text(
                    eyebrow,
                    style=ft.TextStyle(
                        size=11, weight=ft.FontWeight.W_700,
                        color=Colors.primary_glow, letter_spacing=1.4,
                    ),
                ),
            ],
            spacing=6, tight=True,
        ),
        bgcolor=ft.colors.with_opacity(0.14, Colors.primary),
        border=ft.border.all(1, ft.colors.with_opacity(0.4, Colors.primary)),
        border_radius=Radii.pill,
        padding=ft.padding.symmetric(horizontal=10, vertical=5),
    )

    return ft.Row(
        controls=[
            ft.Column(
                controls=[
                    eyebrow_pill,
                    ft.Container(height=Spacing.sm),
                    ft.Text(title, style=Typography.display(size=30)),
                    *( [ft.Text(subtitle, style=Typography.body(size=14))] if subtitle else [] ),
                ],
                spacing=4, tight=True,
            ),
            ft.Container(expand=1),
            *( [trailing] if trailing else [] ),
        ],
        vertical_alignment=ft.CrossAxisAlignment.START,
    )
