"""TrendChart — minimalist sparkline for the dashboard."""

from __future__ import annotations

import flet as ft

from ui.components.glass_card import glass_card
from ui.themes.app_theme import Colors, Spacing, Typography


def trend_chart(points: list[tuple[str, int]]) -> ft.Control:
    if not points:
        return glass_card(
            ft.Column(
                spacing=Spacing.sm,
                controls=[
                    ft.Text("Recommendation activity", style=Typography.subheading(size=15)),
                    ft.Text("No history yet — generate your first recommendation.",
                            style=Typography.body()),
                ],
            )
        )

    max_val = max((v for _, v in points), default=1)
    bars = []
    for label, val in points:
        h = max(8, int((val / max(1, max_val)) * 110))
        bars.append(
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
                controls=[
                    ft.Container(
                        width=22, height=h,
                        gradient=ft.LinearGradient(
                            begin=ft.alignment.bottom_center,
                            end=ft.alignment.top_center,
                            colors=[Colors.primary, Colors.accent_cyan],
                        ),
                        border_radius=6,
                    ),
                    ft.Text(str(val), size=11, color=Colors.text_secondary),
                    ft.Text(label.split("-")[-1] if "-" in label else label,
                            size=10, color=Colors.text_muted),
                ],
            )
        )

    return glass_card(
        ft.Column(
            spacing=Spacing.md,
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Activity (recent weeks)", style=Typography.subheading(size=15)),
                        ft.Container(expand=1),
                        ft.Container(
                            content=ft.Row(
                                spacing=6,
                                controls=[
                                    ft.Container(
                                        width=8, height=8, border_radius=999,
                                        gradient=ft.LinearGradient(
                                            begin=ft.alignment.top_left, end=ft.alignment.bottom_right,
                                            colors=[Colors.primary, Colors.accent_cyan],
                                        ),
                                    ),
                                    ft.Text("Recommendations", size=11, color=Colors.text_secondary),
                                ],
                            ),
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(
                    content=ft.Row(
                        controls=bars, spacing=12,
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                    ),
                    height=160,
                ),
            ],
        )
    )
