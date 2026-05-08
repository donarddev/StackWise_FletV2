"""HistoryTable — DataTable of past recommendations."""

from __future__ import annotations

from typing import Callable, Optional

import flet as ft

from app.helpers.date_helper import humanize
from app.models.recommendation import Recommendation
from app.utils.constants import confidence_label
from ui.components.glass_card import glass_card
from ui.themes.app_theme import Colors, Radii, Spacing, Typography


def history_table(
    items: list[Recommendation],
    *,
    on_view: Callable[[Recommendation], None],
    on_regenerate: Callable[[Recommendation], None],
    on_compare_toggle: Optional[Callable[[Recommendation], None]] = None,
    selected_ids: Optional[set[int]] = None,
) -> ft.Control:
    selected_ids = selected_ids or set()

    rows: list[ft.DataRow] = []
    for it in items:
        confidence_color = (
            Colors.success if it.confidence_score >= 80
            else Colors.primary if it.confidence_score >= 60
            else Colors.warning if it.confidence_score >= 45
            else Colors.danger
        )

        actions: list[ft.Control] = [
            ft.IconButton(
                icon=ft.icons.OPEN_IN_NEW,
                icon_size=18,
                icon_color=Colors.text_secondary,
                tooltip="View",
                on_click=lambda _e, r=it: on_view(r),
            ),
            ft.IconButton(
                icon=ft.icons.REFRESH,
                icon_size=18,
                icon_color=Colors.text_secondary,
                tooltip="Regenerate",
                on_click=lambda _e, r=it: on_regenerate(r),
            ),
        ]
        if on_compare_toggle is not None:
            actions.append(
                ft.IconButton(
                    icon=(
                        ft.icons.CHECK_BOX
                        if it.id in selected_ids
                        else ft.icons.CHECK_BOX_OUTLINE_BLANK
                    ),
                    icon_size=18,
                    icon_color=Colors.primary if it.id in selected_ids else Colors.text_muted,
                    tooltip="Toggle compare",
                    on_click=lambda _e, r=it: on_compare_toggle(r),
                )
            )

        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(_cell_project(it)),
                    ft.DataCell(ft.Text(it.recommended_language, color=Colors.text_primary, size=13)),
                    ft.DataCell(ft.Text(it.recommended_framework, color=Colors.text_primary, size=13)),
                    ft.DataCell(ft.Text(it.recommended_sdlc, color=Colors.text_primary, size=13)),
                    ft.DataCell(_cell_confidence(it.confidence_score, confidence_color)),
                    ft.DataCell(ft.Text(humanize(it.created_at), style=Typography.caption())),
                    ft.DataCell(ft.Row(controls=actions, spacing=2, tight=True)),
                ]
            )
        )

    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Project", style=Typography.caption())),
            ft.DataColumn(ft.Text("Language", style=Typography.caption())),
            ft.DataColumn(ft.Text("Framework", style=Typography.caption())),
            ft.DataColumn(ft.Text("SDLC", style=Typography.caption())),
            ft.DataColumn(ft.Text("Confidence", style=Typography.caption())),
            ft.DataColumn(ft.Text("Created", style=Typography.caption())),
            ft.DataColumn(ft.Text("Actions", style=Typography.caption())),
        ],
        rows=rows,
        heading_row_color=Colors.surface,
        heading_row_height=42,
        data_row_color={ft.MaterialState.DEFAULT: Colors.surface_2},
        data_row_min_height=58,
        data_row_max_height=72,
        column_spacing=24,
        horizontal_lines=ft.BorderSide(1, Colors.border),
        divider_thickness=1,
        show_bottom_border=False,
    )

    return glass_card(
        ft.Column(controls=[table], scroll=ft.ScrollMode.ADAPTIVE),
        padding=Spacing.md,
    )


def _cell_project(rec: Recommendation) -> ft.Control:
    return ft.Column(
        spacing=2, tight=True,
        controls=[
            ft.Text(rec.project_name, size=13.5, weight=ft.FontWeight.W_600, color=Colors.text_primary),
            ft.Text(f"{rec.project_type} · {rec.complexity}", style=Typography.caption()),
        ],
    )


def _cell_confidence(score: int, color: str) -> ft.Control:
    return ft.Container(
        bgcolor=ft.colors.with_opacity(0.14, color),
        border=ft.border.all(1, ft.colors.with_opacity(0.4, color)),
        border_radius=Radii.pill,
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
        content=ft.Text(
            f"{score} · {confidence_label(score)}",
            size=11.5, weight=ft.FontWeight.W_700, color=color,
        ),
    )
