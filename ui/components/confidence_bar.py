"""ConfidenceBar — animated horizontal progress with label."""

from __future__ import annotations

from typing import Any, Mapping, Optional

import flet as ft

from app.utils.constants import confidence_label
from ui.themes.app_theme import Colors, Radii, Spacing, Typography
from ui.theme import caption_style


def confidence_bar(score: int, *, theme: Optional[Mapping[str, Any]] = None) -> ft.Control:
    score = max(0, min(100, int(score)))
    label = confidence_label(score)

    if theme is not None:
        color = (
            theme["confidence_high"] if score >= 80
            else theme["confidence_band_mid"] if score >= 60
            else theme["confidence_mid"] if score >= 45
            else theme["confidence_low"]
        )
        cap = caption_style(theme, size=12)
    else:
        color = (
            Colors.success if score >= 80
            else Colors.primary if score >= 60
            else Colors.warning if score >= 45
            else Colors.danger
        )
        cap = Typography.caption()

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
                    ft.Text("Confidence", style=cap),
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
