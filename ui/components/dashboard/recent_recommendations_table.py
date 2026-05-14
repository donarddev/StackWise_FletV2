"""Dashboard recent recommendations table component."""

from __future__ import annotations

from typing import Any, Callable, Mapping, Optional

import flet as ft

from app.models.recommendation import Recommendation
from ui.components.dashboard.glass_tokens import dashboard_glass_tokens
from ui.components.primary_button import primary_button, secondary_button
from ui.components.section_header import section_header
from ui.themes.app_theme import Radii, Spacing
from ui.theme import card_box_shadow, heading_style, text_style


def _section_shell(*, theme: Mapping[str, Any], content: ft.Control) -> ft.Container:
    g = dashboard_glass_tokens(theme)
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=Spacing.lg, vertical=Spacing.md + 2),
        border_radius=Radii.lg,
        bgcolor=g["card_bg"],
        border=ft.border.all(1, g["card_border"]),
        shadow=[
            card_box_shadow(theme),
            ft.BoxShadow(
                spread_radius=0,
                blur_radius=14,
                color=ft.colors.with_opacity(0.11, g["teal"]),
                offset=ft.Offset(0, 4),
            ),
        ],
        content=content,
        animate=ft.Animation(160, ft.AnimationCurve.EASE_OUT),
    )


def _confidence_badge(score: int, theme: Mapping[str, Any]) -> ft.Container:
    g = dashboard_glass_tokens(theme)
    teal = theme["accent_2"]
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
        border_radius=Radii.pill,
        bgcolor=ft.colors.with_opacity(0.52, theme["surface"]),
        border=ft.border.all(1, ft.colors.with_opacity(0.55, g["card_border"])),
        content=ft.Text(
            f"{score}%",
            size=11.5,
            weight=ft.FontWeight.W_600,
            color=teal,
        ),
    )


def _view_details_pill(
    rec: Recommendation,
    *,
    on_view_details: Callable[[Recommendation], None],
    theme: Mapping[str, Any],
) -> ft.Container:
    g = dashboard_glass_tokens(theme)
    pill_ref = ft.Ref[ft.Container]()

    def on_pill_hover(e: ft.ControlEvent) -> None:
        pill = pill_ref.current
        if pill is None:
            return
        hovered = str(getattr(e, "data", "")).lower() == "true"
        teal = theme["accent_2"]
        if hovered:
            pill.bgcolor = ft.colors.with_opacity(0.18, teal)
            pill.border = ft.border.all(1, ft.colors.with_opacity(0.55, teal))
        else:
            pill.bgcolor = ft.colors.with_opacity(0.1, theme["surface_2"])
            pill.border = ft.border.all(1, ft.colors.with_opacity(0.5, g["card_border"]))
        if pill.page:
            pill.update()

    return ft.Container(
        ref=pill_ref,
        on_click=lambda _e: on_view_details(rec),
        on_hover=on_pill_hover,
        padding=ft.padding.symmetric(horizontal=12, vertical=8),
        border_radius=Radii.pill,
        bgcolor=ft.colors.with_opacity(0.1, theme["surface_2"]),
        border=ft.border.all(1, ft.colors.with_opacity(0.55, g["card_border"])),
        ink=True,
        content=ft.Text(
            "View Details",
            style=text_style(theme, size=12, weight=ft.FontWeight.W_600, color=theme["accent_2"]),
        ),
    )


def dashboard_recent_recommendations_table(
    *,
    recommendations: list[Recommendation],
    on_view_details: Callable[[Recommendation], None],
    on_generate: Callable[[ft.ControlEvent], None],
    theme: Mapping[str, Any],
    on_open_history: Optional[Callable[[ft.ControlEvent], None]] = None,
) -> ft.Control:
    """Recent recommendations table with project details and actions."""

    g = dashboard_glass_tokens(theme)

    trailing = None
    if on_open_history is not None:
        trailing = secondary_button(
            "View history",
            on_click=on_open_history,
            icon="history",
            theme=theme,
            height=42,
            bgcolor=ft.colors.with_opacity(0.28, theme["surface_2"]),
            border_color=ft.colors.with_opacity(0.72, g["card_border"]),
        )

    header_block = section_header(
        "Recent Recommendations",
        subtitle="A quick review of the most recent saved results.",
        trailing=trailing,
        theme=theme,
    )

    if not recommendations:
        empty_body = ft.Column(
            spacing=Spacing.md,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=52,
                    height=52,
                    border_radius=Radii.md,
                    bgcolor=ft.colors.with_opacity(0.1, theme["accent_2"]),
                    border=ft.border.all(1, ft.colors.with_opacity(0.45, g["teal"])),
                    alignment=ft.alignment.center,
                    content=ft.Icon("auto_awesome_outlined", size=24, color=theme["accent_2"]),
                ),
                ft.Text(
                    "No recommendations yet",
                    style=heading_style(theme, size=18),
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Generate your first recommendation to populate your dashboard.",
                    style=text_style(theme, size=14),
                    text_align=ft.TextAlign.CENTER,
                ),
                primary_button(
                    "Generate recommendation",
                    on_click=on_generate,
                    icon="auto_awesome",
                    theme=theme,
                    mint_fill=True,
                    width=272,
                    border_radius=Radii.pill,
                ),
            ],
        )
        inner = ft.Column(
            spacing=Spacing.lg,
            controls=[
                header_block,
                ft.Container(
                    padding=ft.padding.symmetric(vertical=Spacing.xl, horizontal=Spacing.lg),
                    alignment=ft.alignment.center,
                    content=empty_body,
                ),
            ],
        )
        return _section_shell(theme=theme, content=inner)

    _hdr = ft.FontWeight.W_600

    header_row = ft.Container(
        padding=ft.padding.symmetric(horizontal=Spacing.lg, vertical=Spacing.sm + 2),
        border_radius=Radii.md,
        bgcolor=g["header_bg"],
        border=ft.border.all(1, g["header_border"]),
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(
                        "Project",
                        style=text_style(theme, size=12, weight=_hdr, color_key="text_secondary"),
                    ),
                    expand=2,
                ),
                ft.Container(
                    content=ft.Text(
                        "Language",
                        style=text_style(theme, size=12, weight=_hdr, color_key="text_secondary"),
                    ),
                    expand=1,
                ),
                ft.Container(
                    content=ft.Text(
                        "Framework",
                        style=text_style(theme, size=12, weight=_hdr, color_key="text_secondary"),
                    ),
                    expand=1,
                ),
                ft.Container(
                    content=ft.Text(
                        "SDLC Model",
                        style=text_style(theme, size=12, weight=_hdr, color_key="text_secondary"),
                    ),
                    expand=1,
                ),
                ft.Container(
                    content=ft.Text(
                        "Confidence",
                        style=text_style(theme, size=12, weight=_hdr, color_key="text_secondary"),
                    ),
                    expand=1,
                ),
                ft.Container(
                    content=ft.Text(
                        "Date",
                        style=text_style(theme, size=12, weight=_hdr, color_key="text_secondary"),
                    ),
                    expand=1,
                ),
                ft.Container(width=108, alignment=ft.alignment.center_right),
            ],
            spacing=Spacing.md,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    def create_table_row(rec: Recommendation) -> ft.Control:
        row_container = ft.Ref[ft.Container]()

        def on_row_hover(e: ft.ControlEvent) -> None:
            row = row_container.current
            if row is None:
                return
            hovered = str(getattr(e, "data", "")).lower() == "true"
            if hovered:
                row.bgcolor = ft.colors.with_opacity(0.08, g["teal"])
                row.border = ft.border.all(1, ft.colors.with_opacity(0.38, g["teal"]))
            else:
                row.bgcolor = "transparent"
                row.border = ft.border.all(1, "transparent")
            if row.page:
                row.update()

        confidence = rec.confidence_score
        date_str = rec.created_at.strftime("%b %d, %Y") if rec.created_at else "—"

        row_content = ft.Container(
            ref=row_container,
            on_hover=on_row_hover,
            padding=ft.padding.symmetric(horizontal=Spacing.lg, vertical=Spacing.md),
            border_radius=Radii.sm,
            border=ft.border.all(1, "transparent"),
            ink=True,
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            rec.project_name[:30],
                            style=text_style(theme, size=13, color_key="text"),
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        expand=2,
                    ),
                    ft.Container(
                        content=ft.Text(
                            rec.recommended_language,
                            style=text_style(theme, size=13, color_key="text"),
                        ),
                        expand=1,
                    ),
                    ft.Container(
                        content=ft.Text(
                            rec.recommended_framework,
                            style=text_style(theme, size=13, color_key="text"),
                        ),
                        expand=1,
                    ),
                    ft.Container(
                        content=ft.Text(
                            rec.recommended_sdlc,
                            style=text_style(theme, size=13, color_key="text"),
                        ),
                        expand=1,
                    ),
                    ft.Container(
                        content=_confidence_badge(confidence, theme),
                        expand=1,
                        alignment=ft.alignment.center_left,
                    ),
                    ft.Container(
                        content=ft.Text(
                            date_str,
                            style=text_style(theme, size=13, color_key="text"),
                        ),
                        expand=1,
                    ),
                    ft.Container(
                        width=108,
                        alignment=ft.alignment.center_right,
                        content=_view_details_pill(rec, on_view_details=on_view_details, theme=theme),
                    ),
                ],
                spacing=Spacing.md,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        return row_content

    table_rows: list[ft.Control] = []
    for i, rec in enumerate(recommendations):
        table_rows.append(create_table_row(rec))
        if i < len(recommendations) - 1:
            table_rows.append(
                ft.Divider(
                    height=1,
                    color=ft.colors.with_opacity(0.55, g["divider"]),
                )
            )

    table_body = ft.Column(spacing=0, controls=table_rows)

    inner = ft.Column(
        spacing=Spacing.md + 4,
        controls=[
            header_block,
            header_row,
            table_body,
        ],
    )

    return _section_shell(theme=theme, content=inner)
