"""TopList — ranked list of (name, count) pairs (top languages/frameworks/sdlc)."""

from __future__ import annotations

import flet as ft

from ui.components.glass_card import glass_card
from ui.themes.app_theme import Colors, Radii, Spacing, Typography


def top_list(
    *,
    title: str,
    items: list[tuple[str, int]],
    icon: str = ft.icons.LEADERBOARD_OUTLINED,
    accent: str = Colors.primary,
    empty_text: str = "Nothing here yet.",
) -> ft.Control:
    if not items:
        body = ft.Column(
            spacing=Spacing.sm,
            controls=[
                ft.Row(
                    spacing=Spacing.sm,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(icon, size=18, color=accent),
                        ft.Text(title, style=Typography.subheading(size=15)),
                    ],
                ),
                ft.Text(empty_text, style=Typography.body()),
            ],
        )
        return glass_card(body)

    max_v = max(c for _, c in items) or 1
    rows: list[ft.Control] = []
    for i, (name, count) in enumerate(items):
        ratio = count / max_v
        rows.append(
            ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=Spacing.md,
                controls=[
                    ft.Container(
                        width=22, height=22, border_radius=8,
                        bgcolor=ft.colors.with_opacity(0.16, accent),
                        alignment=ft.alignment.center,
                        content=ft.Text(
                            str(i + 1), size=11, weight=ft.FontWeight.W_700, color=accent,
                        ),
                    ),
                    ft.Column(
                        spacing=4, expand=True,
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(name, size=13.5, weight=ft.FontWeight.W_600,
                                            color=Colors.text_primary),
                                    ft.Container(expand=1),
                                    ft.Text(f"{count}", style=Typography.caption()),
                                ],
                            ),
                            ft.ProgressBar(
                                value=ratio,
                                color=accent,
                                bgcolor=ft.colors.with_opacity(0.10, accent),
                                bar_height=6,
                                border_radius=Radii.pill,
                            ),
                        ],
                    ),
                ],
            )
        )

    body = ft.Column(
        spacing=Spacing.md,
        controls=[
            ft.Row(
                spacing=Spacing.sm,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(icon, size=18, color=accent),
                    ft.Text(title, style=Typography.subheading(size=15)),
                ],
            ),
            *rows,
        ],
    )
    return glass_card(body)
