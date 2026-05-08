"""CompareDialog — side-by-side comparison of two recommendations."""

from __future__ import annotations

import flet as ft

from app.helpers.date_helper import humanize
from app.models.recommendation import Recommendation
from ui.components.confidence_bar import confidence_bar
from ui.themes.app_theme import Colors, Radii, Spacing, Typography


def build_compare_dialog(left: Recommendation, right: Recommendation, *, on_close) -> ft.AlertDialog:
    return ft.AlertDialog(
        modal=True,
        bgcolor=Colors.surface,
        shape=ft.RoundedRectangleBorder(radius=Radii.lg),
        content=ft.Container(
            width=860,
            content=ft.Column(
                spacing=Spacing.lg,
                scroll=ft.ScrollMode.ADAPTIVE,
                height=560,
                controls=[
                    ft.Text("Compare recommendations", style=Typography.heading(size=20)),
                    ft.Row(
                        spacing=Spacing.lg,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            _column_for(left, expand=True),
                            _column_for(right, expand=True),
                        ],
                    ),
                    _diff_table(left, right),
                ],
            ),
        ),
        actions=[ft.TextButton("Close", on_click=on_close)],
    )


def _column_for(rec: Recommendation, *, expand: bool) -> ft.Control:
    return ft.Container(
        expand=expand,
        padding=Spacing.lg,
        bgcolor=Colors.surface_2,
        border=ft.border.all(1, Colors.border),
        border_radius=Radii.md,
        content=ft.Column(
            spacing=Spacing.md,
            controls=[
                ft.Text(rec.project_name, style=Typography.subheading(size=15)),
                ft.Text(humanize(rec.created_at), style=Typography.caption()),
                _row("Language", rec.recommended_language, Colors.primary),
                _row("Framework", rec.recommended_framework, Colors.accent_cyan),
                _row("SDLC", rec.recommended_sdlc, Colors.accent_pink),
                confidence_bar(rec.confidence_score),
            ],
        ),
    )


def _row(label: str, value: str, accent: str) -> ft.Control:
    return ft.Row(
        spacing=Spacing.sm,
        controls=[
            ft.Container(
                bgcolor=ft.colors.with_opacity(0.12, accent),
                border_radius=Radii.pill,
                padding=ft.padding.symmetric(horizontal=8, vertical=3),
                content=ft.Text(
                    label.upper(),
                    style=ft.TextStyle(
                        size=10, weight=ft.FontWeight.W_700,
                        color=accent, letter_spacing=1.4,
                    ),
                ),
            ),
            ft.Text(value, size=13, weight=ft.FontWeight.W_600, color=Colors.text_primary),
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )


def _diff_table(left: Recommendation, right: Recommendation) -> ft.Control:
    fields = [
        ("Project Type", left.project_type, right.project_type),
        ("Goal", left.project_goal, right.project_goal),
        ("Complexity", left.complexity, right.complexity),
        ("Team", left.team_size, right.team_size),
        ("Timeline", left.timeline, right.timeline),
        ("Scalability", left.scalability, right.scalability),
        ("Security", left.security, right.security),
        ("Platform", left.platform, right.platform),
        ("Experience", left.experience, right.experience),
    ]
    rows: list[ft.Control] = []
    for name, l, r in fields:
        differs = l != r
        color = Colors.primary_glow if differs else Colors.text_secondary
        rows.append(
            ft.Row(
                spacing=Spacing.md,
                controls=[
                    ft.Text(name, size=12.5, width=140, color=Colors.text_muted),
                    ft.Text(l, size=13, weight=ft.FontWeight.W_600, color=color, expand=1),
                    ft.Text(r, size=13, weight=ft.FontWeight.W_600, color=color, expand=1),
                ],
            )
        )
    return ft.Container(
        padding=Spacing.lg,
        bgcolor=Colors.surface_2,
        border=ft.border.all(1, Colors.border),
        border_radius=Radii.md,
        content=ft.Column(
            spacing=Spacing.sm,
            controls=[
                ft.Text("Project profile differences", style=Typography.subheading(size=14)),
                *rows,
            ],
        ),
    )
