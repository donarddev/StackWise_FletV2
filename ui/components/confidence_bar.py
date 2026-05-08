"""ConfidenceBar — animated horizontal progress with label."""

from __future__ import annotations

import flet as ft

from app.utils.constants import confidence_label
from ui.themes.app_theme import Colors, Radii, Spacing, Typography


def confidence_bar(score: int) -> ft.Control:
    score = max(0, min(100, int(score)))
    label = confidence_label(score)

    color = (
        Colors.success if score >= 80
        else Colors.primary if score >= 60
        else Colors.warning if score >= 45
        else Colors.danger
    )

    bar = ft.ProgressBar(
        value=score / 100.0,
        bgcolor=ft.colors.with_opacity(0.12, color),
        color=color,
        bar_height=10,
        border_radius=Radii.pill,
    )

    return ft.Column(
        spacing=Spacing.sm,
        controls=[
            ft.Row(
                controls=[
                    ft.Text("Confidence", style=Typography.caption()),
                    ft.Container(expand=1),
                    ft.Text(
                        f"{score}/100 · {label}",
                        size=12, weight=ft.FontWeight.W_600,
                        color=color,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bar,
        ],
    )
