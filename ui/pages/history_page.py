"""History page — table of past recommendations + search + compare + filters.

The page builder accepts ``body_ref``, ``compare_btn_ref``, ``stats_ref``,
and ``filters_ref`` so the controller can update sections
**in place** without rebuilding the whole page (preserves search focus).
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any, Callable, Literal, Mapping, Optional

import flet as ft

from app.models.recommendation import Recommendation
from ui.components.dashboard.glass_tokens import dashboard_glass_tokens
from ui.components.empty_state import empty_state
from ui.components.glass_card import glass_card
from ui.components.primary_button import primary_button, secondary_button, text_link
from ui.themes.app_theme import Radii, Spacing
from ui.theme import card_box_shadow, display_style, text_style
from ui.widgets.history_table import history_table

HistoryFilterKey = Literal["all", "high", "moderate", "low", "recent"]


def history_workspace_theme(theme: Mapping[str, Any]) -> dict[str, Any]:
    """Dark-workspace tokens aligned with dashboard glass (History route only)."""
    t = dict(theme)
    if str(t.get("page_bg", "")).lower() != "#020617":
        return t
    g = dashboard_glass_tokens(theme)
    cyan = str(theme["accent_2"])
    t.update(
        {
            "card_bg": g["card_bg"],
            "border": g["card_border"],
            "border_strong": "#26364D",
            "surface": "#101A2B",
            "surface_2": g["panel_bg"],
            "surface_3": g["card_hover"],
            "accent": cyan,
            "accent_soft": "#67E8F9",
            "accent_glow": "#5EEAD4",
            "on_gradient": "#06111F",
            "button_shadow": ft.colors.with_opacity(0.22, cyan),
            "secondary_surface": ft.colors.with_opacity(0.28, "#111C2E"),
            "datatable_heading_bg": g["header_bg"],
            "datatable_divider": g["divider"],
            "data_row_selected": "#152838",
            "data_row_selected_hover": "#1c3048",
            "data_row_alt": "#0e1828",
            "data_row_even": "#101A2B",
            "data_row_hover": "#162636",
        }
    )
    return t


@dataclass(frozen=True)
class HistoryStatsSnapshot:
    """Aggregates for summary cards (computed from full user history)."""

    total: int
    avg_confidence: Optional[float]
    top_language: str
    top_framework: str
    top_sdlc: str


def compute_history_stats(items: list[Recommendation]) -> HistoryStatsSnapshot:
    """Derive summary stats; callers pass the full in-memory list (e.g. limit 500)."""
    if not items:
        return HistoryStatsSnapshot(
            total=0,
            avg_confidence=None,
            top_language="No data yet",
            top_framework="No data yet",
            top_sdlc="No data yet",
        )
    scores = [r.confidence_score for r in items]
    avg = sum(scores) / len(scores)
    lang = Counter(r.recommended_language for r in items).most_common(1)[0][0]
    fw = Counter(r.recommended_framework for r in items).most_common(1)[0][0]
    sdlc = Counter(r.recommended_sdlc for r in items).most_common(1)[0][0]
    return HistoryStatsSnapshot(
        total=len(items),
        avg_confidence=avg,
        top_language=lang or "—",
        top_framework=fw or "—",
        top_sdlc=sdlc or "—",
    )


def _format_avg_confidence(avg: Optional[float]) -> str:
    if avg is None:
        return "—"
    return f"{avg:.0f}%"


def _history_badge(theme: Mapping[str, Any]) -> ft.Control:
    teal = theme["accent_2"]
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.icons.HISTORY_EDU_OUTLINED, size=12, color=teal),
                ft.Text(
                    "HISTORY",
                    size=11,
                    weight=ft.FontWeight.W_700,
                    color=teal,
                ),
            ],
            spacing=6,
            tight=True,
        ),
        bgcolor=ft.colors.with_opacity(0.12, teal),
        border=ft.border.all(1, ft.colors.with_opacity(0.35, teal)),
        border_radius=Radii.pill,
        padding=ft.padding.symmetric(horizontal=10, vertical=5),
    )


def _history_header(
    *,
    theme: Mapping[str, Any],
    compare_btn: ft.Control,
    new_rec_btn: ft.Control,
    compare_hint: ft.Control,
) -> ft.Control:
    title_block = ft.Column(
        spacing=4,
        tight=True,
        expand=True,
        controls=[
            _history_badge(theme),
            ft.Container(height=Spacing.sm),
            ft.Text(
                "Every recommendation you've made.",
                style=display_style(theme, size=28),
                max_lines=2,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
            ft.Text(
                "Search, review explanations, regenerate, or compare recommendations side-by-side.",
                style=text_style(theme, size=14),
                max_lines=3,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
        ],
    )
    actions_block = ft.Column(
        spacing=Spacing.xs,
        horizontal_alignment=ft.CrossAxisAlignment.END,
        controls=[
            ft.Row(
                spacing=Spacing.sm,
                alignment=ft.MainAxisAlignment.END,
                wrap=True,
                controls=[compare_btn, new_rec_btn],
            ),
            compare_hint,
        ],
    )
    return ft.ResponsiveRow(
        spacing=Spacing.lg,
        run_spacing=Spacing.md,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[
            ft.Container(col={"xs": 12, "md": 8}, content=title_block),
            ft.Container(col={"xs": 12, "md": 4}, content=actions_block),
        ],
    )


def _stat_card(*, theme: Mapping[str, Any], label: str, value: str) -> ft.Control:
    """Minimal dashboard-style stat tile (uniform glass, teal hover only)."""
    g = dashboard_glass_tokens(theme)
    card_ref = ft.Ref[ft.Container]()
    rest_bg = g["card_bg"]
    hover_bg = g["card_hover"]

    def _rest_shadow() -> list[ft.BoxShadow]:
        return [
            card_box_shadow(theme),
            ft.BoxShadow(
                spread_radius=0,
                blur_radius=12,
                color=ft.colors.with_opacity(0.1, g["teal"]),
                offset=ft.Offset(0, 3),
            ),
        ]

    def _hover_shadow() -> list[ft.BoxShadow]:
        return [
            card_box_shadow(theme),
            ft.BoxShadow(
                spread_radius=0,
                blur_radius=18,
                color=ft.colors.with_opacity(0.16, g["teal"]),
                offset=ft.Offset(0, 5),
            ),
        ]

    def _on_hover(e: ft.ControlEvent) -> None:
        hovered = str(getattr(e, "data", "")).lower() == "true"
        card = card_ref.current
        if card is None:
            return
        if hovered:
            card.bgcolor = hover_bg
            card.border = ft.border.all(1, ft.colors.with_opacity(0.5, g["teal"]))
            card.shadow = _hover_shadow()
        else:
            card.bgcolor = rest_bg
            card.border = ft.border.all(1, g["card_border"])
            card.shadow = _rest_shadow()
        if card.page:
            card.update()

    inner = ft.Column(
        spacing=6,
        tight=True,
        expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            ft.Text(
                label.upper(),
                style=text_style(theme, size=11, weight=ft.FontWeight.W_600, color_key="text_muted"),
            ),
            ft.Text(
                value,
                style=display_style(theme, size=20),
                max_lines=2,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
        ],
    )

    return ft.Container(
        ref=card_ref,
        height=120,
        padding=ft.padding.symmetric(horizontal=14, vertical=12),
        border_radius=Radii.lg,
        bgcolor=rest_bg,
        border=ft.border.all(1, g["card_border"]),
        shadow=_rest_shadow(),
        content=inner,
        on_hover=_on_hover,
        animate=ft.Animation(160, ft.AnimationCurve.EASE_OUT),
    )


def build_stats_row(stats: HistoryStatsSnapshot, theme: Mapping[str, Any]) -> ft.Control:
    gap = 20
    cards = [
        _stat_card(theme=theme, label="Total recommendations", value=str(stats.total)),
        _stat_card(
            theme=theme,
            label="Average confidence",
            value=_format_avg_confidence(stats.avg_confidence),
        ),
        _stat_card(
            theme=theme,
            label="Most recommended language",
            value=stats.top_language,
        ),
        _stat_card(
            theme=theme,
            label="Most recommended framework",
            value=stats.top_framework,
        ),
        _stat_card(
            theme=theme,
            label="Most used SDLC model",
            value=stats.top_sdlc,
        ),
    ]
    row_top = ft.ResponsiveRow(
        spacing=gap,
        run_spacing=gap,
        controls=[
            ft.Container(col={"xs": 12, "sm": 6, "md": 4}, content=cards[0]),
            ft.Container(col={"xs": 12, "sm": 6, "md": 4}, content=cards[1]),
            ft.Container(col={"xs": 12, "sm": 6, "md": 4}, content=cards[2]),
        ],
    )
    row_bottom = ft.ResponsiveRow(
        spacing=gap,
        run_spacing=gap,
        controls=[
            ft.Container(col={"xs": 12, "sm": 6, "md": 6}, content=cards[3]),
            ft.Container(col={"xs": 12, "sm": 6, "md": 6}, content=cards[4]),
        ],
    )
    return ft.Column(spacing=gap, tight=True, controls=[row_top, row_bottom])


def _filter_chip(
    label: str,
    key: HistoryFilterKey,
    *,
    theme: Mapping[str, Any],
    active: HistoryFilterKey,
    on_select: Callable[[HistoryFilterKey], None],
) -> ft.Control:
    selected = active == key
    teal = theme["accent_2"]
    if selected:
        border_c = ft.colors.with_opacity(0.42, teal)
        bg = ft.colors.with_opacity(0.14, teal)
        fg = theme["text"]
    else:
        border_c = theme["border_strong"]
        bg = ft.colors.with_opacity(0.45, theme["surface"])
        fg = theme["text_secondary"]

    def _tap(_: ft.ControlEvent) -> None:
        on_select(key)

    return ft.Container(
        content=ft.Text(
            label,
            size=12,
            weight=ft.FontWeight.W_600,
            color=fg,
        ),
        padding=ft.padding.symmetric(horizontal=13, vertical=7),
        border_radius=Radii.pill,
        border=ft.border.all(1, border_c),
        bgcolor=bg,
        ink=True,
        on_click=_tap,
    )


def build_filters_row(
    *,
    theme: Mapping[str, Any],
    active: HistoryFilterKey,
    on_filter: Callable[[HistoryFilterKey], None],
    show_clear: bool,
    on_clear: Callable[[ft.ControlEvent], None],
) -> ft.Control:
    chips = ft.Row(
        wrap=True,
        run_spacing=10,
        spacing=10,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            _filter_chip("All", "all", theme=theme, active=active, on_select=on_filter),
            _filter_chip("High confidence", "high", theme=theme, active=active, on_select=on_filter),
            _filter_chip("Moderate confidence", "moderate", theme=theme, active=active, on_select=on_filter),
            _filter_chip("Low confidence", "low", theme=theme, active=active, on_select=on_filter),
            _filter_chip("Recent", "recent", theme=theme, active=active, on_select=on_filter),
        ],
    )
    clear_ctrl: ft.Control = ft.Container()
    if show_clear:
        clear_ctrl = ft.Container(
            padding=ft.padding.only(left=Spacing.sm),
            content=text_link("Clear filters", on_clear, theme=theme),
        )
    return ft.Row(
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        wrap=True,
        run_spacing=10,
        spacing=10,
        controls=[chips, clear_ctrl],
    )


def _history_surface(theme: Mapping[str, Any], content: ft.Control) -> ft.Control:
    """Content on the authenticated workspace background (no extra gradient panel)."""
    _ = theme
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=Spacing.xl, vertical=Spacing.xl),
        content=content,
    )


def render_history_body(
    *,
    theme: Mapping[str, Any],
    items: list[Recommendation],
    selected_ids: set[int],
    search_query: str,
    active_filter: HistoryFilterKey,
    on_view: Callable[[Recommendation], None],
    on_regenerate: Callable[[Recommendation], None],
    on_compare_select: Callable[[Recommendation, bool], None],
    on_delete: Callable[[Recommendation], None],
    on_new_recommendation: Callable[[ft.ControlEvent], None],
    error_message: Optional[str] = None,
    on_retry_load: Optional[Callable[[ft.ControlEvent], None]] = None,
) -> ft.Control:
    """Render only the result body (table OR empty state)."""
    if error_message:
        return empty_state(
            icon=ft.icons.ERROR_OUTLINE,
            title="Couldn't load history",
            description=error_message,
            action=(
                primary_button(
                    "Try again",
                    on_click=on_retry_load,
                    icon=ft.icons.REFRESH_ROUNDED,
                    theme=theme,
                    mint_fill=True,
                    border_radius=Radii.pill,
                )
                if on_retry_load is not None
                else None
            ),
            theme=theme,
        )

    q = (search_query or "").strip()
    filtered_empty = not items and (q or active_filter != "all")

    if not items and not filtered_empty:
        inner = empty_state(
            icon=ft.icons.HISTORY_OUTLINED,
            title="No recommendations yet",
            description="Generate your first recommendation to start building your decision history.",
            action=primary_button(
                "New recommendation",
                on_click=on_new_recommendation,
                icon=ft.icons.AUTO_AWESOME,
                theme=theme,
                mint_fill=True,
                border_radius=Radii.pill,
            ),
            theme=theme,
        )
        return glass_card(
            ft.Container(content=inner, padding=Spacing.lg),
            padding=0,
            theme=theme,
        )
    if not items:
        return empty_state(
            icon=ft.icons.SEARCH_OFF_OUTLINED,
            title="No matching recommendations found.",
            description="Try adjusting search or filters, or clear filters to see all records.",
            theme=theme,
        )
    return history_table(
        items,
        theme=theme,
        on_view=on_view,
        on_regenerate=on_regenerate,
        on_compare_select=on_compare_select,
        on_delete=on_delete,
        selected_ids=selected_ids,
    )


def build_history_page(
    *,
    theme: Mapping[str, Any],
    items: list[Recommendation],
    selected_ids: set[int],
    stats: HistoryStatsSnapshot,
    active_filter: HistoryFilterKey,
    search_field: ft.TextField,
    on_search_change: Callable[[str], None],
    on_filter: Callable[[HistoryFilterKey], None],
    on_clear_filters: Callable[[ft.ControlEvent], None],
    on_view: Callable[[Recommendation], None],
    on_regenerate: Callable[[Recommendation], None],
    on_compare_select: Callable[[Recommendation, bool], None],
    on_delete: Callable[[Recommendation], None],
    on_compare: Callable[[ft.ControlEvent], None],
    on_new_recommendation: Callable[[ft.ControlEvent], None],
    body_ref: Optional[ft.Ref[ft.Container]] = None,
    compare_btn_ref: Optional[ft.Ref[ft.Container]] = None,
    compare_hint_ref: Optional[ft.Ref[ft.Text]] = None,
    stats_ref: Optional[ft.Ref[ft.Container]] = None,
    filters_ref: Optional[ft.Ref[ft.Container]] = None,
) -> ft.Control:
    search_field.on_change = lambda _e: on_search_change(search_field.value or "")
    search_field.dense = True
    search_field.content_padding = ft.padding.symmetric(horizontal=14, vertical=14)

    g = dashboard_glass_tokens(theme)
    outline_bd = ft.colors.with_opacity(0.72, g["card_border"])
    hover_bd = g["teal"]
    outline_bg = ft.colors.with_opacity(0.28, theme["surface_2"])

    compare_btn = secondary_button(
        "Compare selected",
        on_compare,
        icon=ft.icons.COMPARE_ARROWS,
        theme=theme,
        height=44,
        border_radius=Radii.pill,
        bgcolor=outline_bg,
        border_color=outline_bd,
        hover_border_color=hover_bd,
        ref=compare_btn_ref if compare_btn_ref is not None else None,
    )

    new_rec_btn = primary_button(
        "New recommendation",
        on_click=on_new_recommendation,
        icon=ft.icons.AUTO_AWESOME,
        theme=theme,
        mint_fill=True,
        border_radius=Radii.pill,
    )

    n_sel = len(selected_ids)
    _hint_kw = {
        "value": "Select two records to compare." if n_sel != 2 else "",
        "visible": n_sel != 2,
        "size": 12,
        "color": theme["text_muted"],
        "text_align": ft.TextAlign.RIGHT,
        "max_lines": 2,
    }
    if compare_hint_ref is not None:
        compare_hint = ft.Text(ref=compare_hint_ref, **_hint_kw)
    else:
        compare_hint = ft.Text(**_hint_kw)

    header = _history_header(
        theme=theme,
        compare_btn=compare_btn,
        new_rec_btn=new_rec_btn,
        compare_hint=compare_hint,
    )

    stats_row = build_stats_row(stats, theme)
    stats_host = ft.Container(content=stats_row)
    if stats_ref is not None:
        stats_host.ref = stats_ref

    show_clear = bool((search_field.value or "").strip()) or active_filter != "all"
    filters_inner = build_filters_row(
        theme=theme,
        active=active_filter,
        on_filter=on_filter,
        show_clear=show_clear,
        on_clear=on_clear_filters,
    )
    filters_host = ft.Container(content=filters_inner)
    if filters_ref is not None:
        filters_host.ref = filters_ref

    body = render_history_body(
        theme=theme,
        items=items,
        selected_ids=selected_ids,
        search_query=search_field.value or "",
        active_filter=active_filter,
        on_view=on_view,
        on_regenerate=on_regenerate,
        on_compare_select=on_compare_select,
        on_delete=on_delete,
        on_new_recommendation=on_new_recommendation,
        error_message=None,
        on_retry_load=None,
    )
    body_container = ft.Container(content=body)
    if body_ref is not None:
        body_container.ref = body_ref

    search_block = glass_card(
        ft.Column(
            spacing=14,
            tight=True,
            controls=[
                search_field,
                filters_host,
            ],
        ),
        padding=20,
        theme=theme,
    )

    inner_column = ft.Column(
        spacing=24,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        controls=[
            header,
            stats_host,
            search_block,
            body_container,
        ],
    )

    apply_compare_button_state(compare_btn, selected_ids, on_compare)

    return _history_surface(theme, inner_column)


def apply_compare_button_state(
    btn: ft.Container,
    selected_ids: set[int],
    on_compare: Callable[[ft.ControlEvent], None],
) -> None:
    """Outline compare CTA: muted until two rows are selected; keeps handler wiring consistent."""
    n = len(selected_ids)
    disabled = n != 2
    btn.opacity = 0.4 if n == 0 else (0.72 if n == 1 else 1.0)
    btn.on_click = None if disabled else on_compare
