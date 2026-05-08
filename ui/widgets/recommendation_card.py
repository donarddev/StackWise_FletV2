"""RecommendationResultCard — the big floating card with the recommendation."""

from __future__ import annotations

from typing import Callable, Optional

import flet as ft

from app.helpers.date_helper import humanize
from app.models.recommendation import Recommendation
from ui.components.confidence_bar import confidence_bar
from ui.components.glass_card import glass_card
from ui.themes.app_theme import Colors, Radii, Spacing, Typography


def recommendation_result_card(
    rec: Recommendation,
    *,
    on_view: Optional[Callable[[ft.ControlEvent], None]] = None,
    on_regenerate: Optional[Callable[[ft.ControlEvent], None]] = None,
) -> ft.Control:
    """Detailed result card shown right after generation and on detail view."""
    pillars = ft.ResponsiveRow(
        spacing=Spacing.md, run_spacing=Spacing.md,
        controls=[
            _result_pillar(
                title="Language",
                value=rec.recommended_language,
                icon=ft.icons.CODE_ROUNDED,
                accent=Colors.primary,
                col={"xs": 12, "md": 4},
            ),
            _result_pillar(
                title="Framework",
                value=rec.recommended_framework,
                icon=ft.icons.DASHBOARD_CUSTOMIZE_OUTLINED,
                accent=Colors.accent_cyan,
                col={"xs": 12, "md": 4},
            ),
            _result_pillar(
                title="SDLC Model",
                value=rec.recommended_sdlc,
                icon=ft.icons.ALT_ROUTE_OUTLINED,
                accent=Colors.accent_pink,
                col={"xs": 12, "md": 4},
            ),
        ],
    )

    actions: list[ft.Control] = []
    if on_view is not None:
        actions.append(
            ft.TextButton("View details", on_click=on_view, icon=ft.icons.OPEN_IN_NEW)
        )
    if on_regenerate is not None:
        actions.append(
            ft.TextButton("Regenerate", on_click=on_regenerate, icon=ft.icons.REFRESH)
        )

    header = ft.Row(
        controls=[
            ft.Column(
                controls=[
                    ft.Text(rec.project_name, style=Typography.subheading(size=18)),
                    ft.Text(
                        f"{rec.project_type} · {rec.complexity} · {humanize(rec.created_at)}",
                        style=Typography.caption(),
                    ),
                ],
                spacing=2, tight=True,
            ),
            ft.Container(expand=1),
            *actions,
        ],
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    body = ft.Column(
        spacing=Spacing.lg,
        controls=[
            header,
            pillars,
            confidence_bar(rec.confidence_score),
        ],
    )
    return glass_card(body)


def _result_pillar(
    *, title: str, value: str, icon: str, accent: str, col: dict
) -> ft.Control:
    return ft.Container(
        col=col,
        padding=Spacing.lg,
        bgcolor=Colors.surface,
        border=ft.border.all(1, Colors.border),
        border_radius=Radii.md,
        content=ft.Column(
            spacing=Spacing.sm,
            controls=[
                ft.Row(
                    spacing=Spacing.sm,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            content=ft.Icon(icon, size=16, color=accent),
                            bgcolor=ft.colors.with_opacity(0.14, accent),
                            padding=8, border_radius=10,
                        ),
                        ft.Text(title.upper(), style=Typography.caption()),
                    ],
                ),
                ft.Text(value, size=18, weight=ft.FontWeight.W_700, color=Colors.text_primary),
            ],
        ),
    )
