"""HistoryTable — responsive recommendations: DataTable (md+) or stacked cards (xs–sm)."""

from __future__ import annotations

from typing import Any, Callable, Literal, Mapping, Optional

HistoryListMode = Literal["active", "deleted"]

import flet as ft

from app.helpers.date_helper import humanize
from app.models.recommendation import Recommendation
from app.utils.constants import confidence_label
from ui.components.dashboard.glass_tokens import dashboard_glass_tokens
from ui.themes.app_theme import Radii, Spacing
from ui.theme import caption_style, card_box_shadow


def _confidence_palette(score: int, theme: Mapping[str, Any]) -> tuple[str, str]:
    """High = teal, moderate = amber, low = red (no purple band)."""
    if score >= 80:
        t = theme["accent_2"]
        return t, t
    if score >= 45:
        c = theme["confidence_mid"]
        return c, c
    d = theme["confidence_low"]
    return d, d


def _icon_button(
    icon: str,
    *,
    theme: Mapping[str, Any],
    tooltip: str,
    on_click: Callable[[ft.ControlEvent], None],
    danger: bool = False,
) -> ft.IconButton:
    if danger:
        colors: dict = {
            ft.ControlState.DEFAULT: theme["text_muted"],
            ft.ControlState.HOVERED: theme["danger"],
        }
    else:
        colors = {
            ft.ControlState.DEFAULT: theme["text_secondary"],
            ft.ControlState.HOVERED: theme["accent_2"],
        }
    return ft.IconButton(
        icon=icon,
        icon_size=20,
        tooltip=tooltip,
        style=ft.ButtonStyle(color=colors),
        on_click=on_click,
    )


def _cell_confidence(score: int, accent: str, tint: str) -> ft.Control:
    label = confidence_label(score)
    return ft.Container(
        bgcolor=ft.colors.with_opacity(0.16, tint),
        border=ft.border.all(1, ft.colors.with_opacity(0.55, accent)),
        border_radius=Radii.pill,
        padding=ft.padding.symmetric(horizontal=12, vertical=6),
        content=ft.Text(
            f"{score}% · {label}",
            size=12,
            weight=ft.FontWeight.W_700,
            color=accent,
        ),
    )


def _cell_project(rec: Recommendation, *, theme: Mapping[str, Any], outline: bool = False) -> ft.Control:
    inner = ft.Column(
        spacing=2,
        tight=True,
        controls=[
            ft.Text(
                rec.project_name,
                size=14,
                weight=ft.FontWeight.W_600,
                color=theme["text"],
                max_lines=2,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
            ft.Text(
                f"{rec.project_type} · {rec.complexity}",
                style=caption_style(theme),
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
        ],
    )
    if not outline:
        return inner
    return ft.Container(
        padding=ft.padding.only(left=10, right=10, top=4, bottom=4),
        border=ft.border.only(
            left=ft.BorderSide(2.5, ft.colors.with_opacity(0.55, theme["accent_2"])),
        ),
        content=inner,
    )


def _cell_text(value: str, *, theme: Mapping[str, Any], size: int = 14) -> ft.Control:
    return ft.Text(
        value,
        color=theme["text_secondary"],
        size=size,
        max_lines=2,
        overflow=ft.TextOverflow.ELLIPSIS,
    )


def _cell_created(rec: Recommendation, *, theme: Mapping[str, Any]) -> ft.Control:
    return ft.Text(
        humanize(rec.created_at),
        size=13.5,
        weight=ft.FontWeight.W_500,
        color=theme["text_secondary"],
    )


def _cell_deleted(rec: Recommendation, *, theme: Mapping[str, Any]) -> ft.Control:
    when = rec.deleted_at or rec.created_at
    return ft.Text(
        humanize(when),
        size=13.5,
        weight=ft.FontWeight.W_500,
        color=theme["text_secondary"],
    )


def _build_data_table(
    items: list[Recommendation],
    *,
    theme: Mapping[str, Any],
    list_mode: HistoryListMode,
    on_view: Callable[[Recommendation], None],
    on_regenerate: Callable[[Recommendation], None],
    on_compare_select: Callable[[Recommendation, bool], None],
    on_delete: Optional[Callable[[Recommendation], None]],
    on_restore: Optional[Callable[[Recommendation], None]],
    selected_ids: set[int],
) -> ft.DataTable:
    cap = caption_style(theme, size=12)
    rows: list[ft.DataRow] = []
    for idx, it in enumerate(items):
        accent, tint = _confidence_palette(it.confidence_score, theme)
        is_sel = it.id in selected_ids

        def _compare_change(e: ft.ControlEvent, r: Recommendation = it) -> None:
            on_compare_select(r, bool(e.control.value))

        compare_cell: ft.DataCell | None = None
        if list_mode == "active":
            compare_cell = ft.DataCell(
                ft.Container(
                    alignment=ft.alignment.center,
                    padding=ft.padding.symmetric(horizontal=2, vertical=4),
                    content=ft.Checkbox(
                        value=is_sel,
                        on_change=_compare_change,
                        tooltip="Select for compare (choose up to two)",
                        active_color=theme["accent_2"],
                        check_color=theme["on_gradient"],
                    ),
                )
            )

        actions: list[ft.Control] = [
            _icon_button(
                ft.icons.VISIBILITY_OUTLINED,
                theme=theme,
                tooltip="View details",
                on_click=lambda _e, r=it: on_view(r),
            ),
        ]
        if list_mode == "active":
            actions.append(
                _icon_button(
                    ft.icons.REFRESH_ROUNDED,
                    theme=theme,
                    tooltip="Regenerate",
                    on_click=lambda _e, r=it: on_regenerate(r),
                ),
            )
            if on_delete is not None:
                actions.append(
                    _icon_button(
                        ft.icons.DELETE_OUTLINE,
                        theme=theme,
                        tooltip="Move to Recently Deleted",
                        on_click=lambda _e, r=it: on_delete(r),
                        danger=True,
                    ),
                )
        elif on_restore is not None:
            actions.append(
                _icon_button(
                    ft.icons.RESTORE_FROM_TRASH_OUTLINED,
                    theme=theme,
                    tooltip="Restore",
                    on_click=lambda _e, r=it: on_restore(r),
                ),
            )

        if is_sel:
            base = theme["data_row_selected"]
            hover = theme["data_row_selected_hover"]
        else:
            base = theme["data_row_alt"] if idx % 2 else theme["data_row_even"]
            hover = theme["data_row_hover"]

        row_color: dict = {
            ft.ControlState.DEFAULT: base,
            ft.ControlState.HOVERED: hover,
        }

        date_cell = (
            _cell_deleted(it, theme=theme)
            if list_mode == "deleted"
            else _cell_created(it, theme=theme)
        )
        row_cells: list[ft.DataCell] = []
        if compare_cell is not None:
            row_cells.append(compare_cell)
        row_cells.extend(
            [
                ft.DataCell(_cell_project(it, theme=theme, outline=is_sel and list_mode == "active")),
                ft.DataCell(_cell_text(it.recommended_language, theme=theme)),
                ft.DataCell(_cell_text(it.recommended_framework, theme=theme)),
                ft.DataCell(_cell_text(it.recommended_sdlc, theme=theme)),
                ft.DataCell(
                    ft.Container(
                        alignment=ft.alignment.center,
                        padding=ft.padding.symmetric(vertical=4),
                        content=_cell_confidence(it.confidence_score, accent, tint),
                    ),
                ),
                ft.DataCell(
                    ft.Container(
                        alignment=ft.alignment.center_left,
                        padding=ft.padding.only(left=4),
                        content=date_cell,
                    ),
                ),
                ft.DataCell(
                    ft.Container(
                        alignment=ft.alignment.center,
                        padding=ft.padding.symmetric(horizontal=4),
                        content=ft.Row(
                            controls=actions,
                            spacing=4,
                            wrap=False,
                            alignment=ft.MainAxisAlignment.CENTER,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                    ),
                ),
            ]
        )
        rows.append(ft.DataRow(color=row_color, cells=row_cells))

    columns: list[ft.DataColumn] = []
    if list_mode == "active":
        columns.append(
            ft.DataColumn(
                ft.Text("Compare", style=cap),
                tooltip="Select two records to compare.",
                heading_row_alignment=ft.MainAxisAlignment.CENTER,
            ),
        )
    columns.extend(
        [
            ft.DataColumn(ft.Text("Project", style=cap), heading_row_alignment=ft.MainAxisAlignment.START),
            ft.DataColumn(ft.Text("Language", style=cap), heading_row_alignment=ft.MainAxisAlignment.START),
            ft.DataColumn(ft.Text("Framework", style=cap), heading_row_alignment=ft.MainAxisAlignment.START),
            ft.DataColumn(ft.Text("SDLC", style=cap), heading_row_alignment=ft.MainAxisAlignment.START),
            ft.DataColumn(ft.Text("Confidence", style=cap), heading_row_alignment=ft.MainAxisAlignment.CENTER),
            ft.DataColumn(
                ft.Text("Deleted" if list_mode == "deleted" else "Created", style=cap),
                heading_row_alignment=ft.MainAxisAlignment.START,
            ),
            ft.DataColumn(ft.Text("Actions", style=cap), heading_row_alignment=ft.MainAxisAlignment.CENTER),
        ]
    )

    return ft.DataTable(
        columns=columns,
        rows=rows,
        heading_row_color=theme["datatable_heading_bg"],
        heading_row_height=48,
        heading_text_style=cap,
        data_text_style=ft.TextStyle(size=14, color=theme["text"]),
        data_row_min_height=72,
        data_row_max_height=88,
        column_spacing=16,
        horizontal_margin=12,
        horizontal_lines=ft.BorderSide(1, ft.colors.with_opacity(0.28, theme["datatable_divider"])),
        divider_thickness=1,
        show_bottom_border=False,
    )


def _history_mobile_card(
    it: Recommendation,
    *,
    theme: Mapping[str, Any],
    list_mode: HistoryListMode,
    idx: int,
    is_sel: bool,
    on_view: Callable[[Recommendation], None],
    on_regenerate: Callable[[Recommendation], None],
    on_compare_select: Callable[[Recommendation, bool], None],
    on_delete: Optional[Callable[[Recommendation], None]],
    on_restore: Optional[Callable[[Recommendation], None]],
) -> ft.Control:
    accent, tint = _confidence_palette(it.confidence_score, theme)

    def _compare_change(e: ft.ControlEvent, r: Recommendation = it) -> None:
        on_compare_select(r, bool(e.control.value))

    actions: list[ft.Control] = [
        _icon_button(ft.icons.VISIBILITY_OUTLINED, theme=theme, tooltip="View details", on_click=lambda _e, r=it: on_view(r)),
    ]
    if list_mode == "active":
        actions.append(
            _icon_button(ft.icons.REFRESH_ROUNDED, theme=theme, tooltip="Regenerate", on_click=lambda _e, r=it: on_regenerate(r)),
        )
        if on_delete is not None:
            actions.append(
                _icon_button(
                    ft.icons.DELETE_OUTLINE,
                    theme=theme,
                    tooltip="Move to Recently Deleted",
                    on_click=lambda _e, r=it: on_delete(r),
                    danger=True,
                ),
            )
    elif on_restore is not None:
        actions.append(
            _icon_button(
                ft.icons.RESTORE_FROM_TRASH_OUTLINED,
                theme=theme,
                tooltip="Restore",
                on_click=lambda _e, r=it: on_restore(r),
            ),
        )

    sel_tint = theme["data_row_selected"]
    alt = theme["data_row_alt"]
    even = theme["data_row_even"]
    base_bg = sel_tint if is_sel else (alt if idx % 2 else even)
    border_c = (
        ft.colors.with_opacity(0.45, theme["accent_2"])
        if is_sel
        else theme["border_strong"]
    )

    header_controls: list[ft.Control] = []
    if list_mode == "active":
        header_controls.append(
            ft.Checkbox(
                value=is_sel,
                on_change=_compare_change,
                tooltip="Select for compare (choose up to two)",
                active_color=theme["accent_2"],
                check_color=theme["on_gradient"],
            ),
        )
    header_controls.append(
        ft.Container(
            expand=True,
            content=ft.Column(
                spacing=2,
                tight=True,
                controls=[
                    ft.Text(
                        it.project_name,
                        size=15,
                        weight=ft.FontWeight.W_600,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        color=theme["text"],
                    ),
                    ft.Text(
                        f"{it.project_type} · {it.complexity}",
                        style=caption_style(theme),
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ],
            ),
        ),
    )

    date_label = humanize(it.deleted_at or it.created_at)
    date_prefix = "Deleted" if list_mode == "deleted" else "Created"

    return ft.Container(
        padding=Spacing.lg,
        border_radius=Radii.lg,
        bgcolor=base_bg,
        border=ft.border.all(1, border_c),
        content=ft.Column(
            spacing=Spacing.md,
            tight=True,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Row(
                            spacing=Spacing.sm,
                            controls=header_controls,
                        ),
                    ],
                ),
                ft.Row(
                    spacing=Spacing.sm,
                    run_spacing=Spacing.sm,
                    wrap=True,
                    controls=[
                        _chip(it.recommended_language, theme),
                        _chip(it.recommended_framework, theme),
                        _chip(it.recommended_sdlc, theme),
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        _cell_confidence(it.confidence_score, accent, tint),
                        ft.Text(f"{date_prefix} {date_label}", style=caption_style(theme)),
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.START,
                    controls=actions,
                    wrap=True,
                ),
            ],
        ),
    )


def _chip(text: str, theme: Mapping[str, Any]) -> ft.Control:
    g = dashboard_glass_tokens(theme)
    line = theme["accent_2"]
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=10, vertical=5),
        border_radius=Radii.pill,
        bgcolor=ft.colors.with_opacity(0.1, line),
        border=ft.border.all(1, ft.colors.with_opacity(0.38, g["card_border"])),
        content=ft.Text(
            text,
            size=12,
            weight=ft.FontWeight.W_600,
            color=theme["text_secondary"],
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        ),
    )


def _table_shell(theme: Mapping[str, Any], content: ft.Control) -> ft.Container:
    """Dashboard-aligned glass shell (soft navy, subtle border, light teal shadow)."""
    g = dashboard_glass_tokens(theme)
    return ft.Container(
        padding=Spacing.md,
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


def history_results(
    items: list[Recommendation],
    *,
    theme: Mapping[str, Any],
    list_mode: HistoryListMode = "active",
    on_view: Callable[[Recommendation], None],
    on_regenerate: Callable[[Recommendation], None],
    on_compare_select: Callable[[Recommendation, bool], None],
    on_delete: Optional[Callable[[Recommendation], None]] = None,
    on_restore: Optional[Callable[[Recommendation], None]] = None,
    selected_ids: Optional[set[int]] = None,
) -> ft.Control:
    """Wide: DataTable. Narrow: stacked cards. Same callbacks for both."""
    selected_ids = selected_ids or set()

    table = _build_data_table(
        items,
        theme=theme,
        list_mode=list_mode,
        on_view=on_view,
        on_regenerate=on_regenerate,
        on_compare_select=on_compare_select,
        on_delete=on_delete,
        on_restore=on_restore,
        selected_ids=selected_ids,
    )
    table_panel = _table_shell(
        theme,
        ft.Column(
            spacing=0,
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[table],
        ),
    )

    cards = [
        _history_mobile_card(
            it,
            theme=theme,
            list_mode=list_mode,
            idx=i,
            is_sel=it.id in selected_ids,
            on_view=on_view,
            on_regenerate=on_regenerate,
            on_compare_select=on_compare_select,
            on_delete=on_delete,
            on_restore=on_restore,
        )
        for i, it in enumerate(items)
    ]
    cards_panel = _table_shell(
        theme,
        ft.Column(
            spacing=Spacing.md,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=cards,
        ),
    )

    return ft.ResponsiveRow(
        spacing=Spacing.md,
        run_spacing=Spacing.md,
        controls=[
            ft.Container(col={"xs": 12, "md": 0}, content=cards_panel),
            ft.Container(col={"xs": 0, "md": 12}, content=table_panel),
        ],
    )


def history_table(
    items: list[Recommendation],
    *,
    theme: Mapping[str, Any],
    list_mode: HistoryListMode = "active",
    on_view: Callable[[Recommendation], None],
    on_regenerate: Callable[[Recommendation], None],
    on_compare_select: Callable[[Recommendation, bool], None],
    on_delete: Optional[Callable[[Recommendation], None]] = None,
    on_restore: Optional[Callable[[Recommendation], None]] = None,
    selected_ids: Optional[set[int]] = None,
) -> ft.Control:
    """Backward-compatible alias for ``history_results``."""
    return history_results(
        items,
        theme=theme,
        list_mode=list_mode,
        on_view=on_view,
        on_regenerate=on_regenerate,
        on_compare_select=on_compare_select,
        on_delete=on_delete,
        on_restore=on_restore,
        selected_ids=selected_ids,
    )
