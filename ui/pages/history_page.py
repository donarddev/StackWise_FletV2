"""History page — table of past recommendations + search + compare.

The page builder accepts ``body_ref`` and ``compare_btn_ref`` so the
controller can update the results table and compare button **in place**
on every search keystroke / selection toggle, instead of rebuilding the
whole page (which would drop focus and scroll position).
"""

from __future__ import annotations

from typing import Callable, Optional

import flet as ft

from app.models.recommendation import Recommendation
from ui.components.empty_state import empty_state
from ui.components.glass_card import glass_card
from ui.components.page_header import page_header
from ui.components.primary_button import primary_button
from ui.themes.app_theme import Colors, Spacing
from ui.widgets.history_table import history_table


def render_history_body(
    *,
    items: list[Recommendation],
    selected_ids: set[int],
    search_query: str,
    on_view: Callable[[Recommendation], None],
    on_regenerate: Callable[[Recommendation], None],
    on_compare_toggle: Callable[[Recommendation], None],
    on_new_recommendation: Callable[[ft.ControlEvent], None],
) -> ft.Control:
    """Render only the result body (table OR empty state)."""
    if not items and not (search_query or "").strip():
        return empty_state(
            icon=ft.icons.HISTORY_OUTLINED,
            title="No recommendations yet",
            description="Generate your first recommendation and it will appear here.",
            action=primary_button(
                "Start a recommendation",
                on_click=on_new_recommendation,
                icon=ft.icons.AUTO_AWESOME,
            ),
        )
    if not items:
        return empty_state(
            icon=ft.icons.SEARCH_OFF_OUTLINED,
            title="No matches",
            description="Try a different search term.",
        )
    return history_table(
        items,
        on_view=on_view,
        on_regenerate=on_regenerate,
        on_compare_toggle=on_compare_toggle,
        selected_ids=selected_ids,
    )


def build_history_page(
    *,
    items: list[Recommendation],
    selected_ids: set[int],
    search_field: ft.TextField,
    on_search_change: Callable[[str], None],
    on_view: Callable[[Recommendation], None],
    on_regenerate: Callable[[Recommendation], None],
    on_compare_toggle: Callable[[Recommendation], None],
    on_compare: Callable[[ft.ControlEvent], None],
    on_new_recommendation: Callable[[ft.ControlEvent], None],
    body_ref: Optional[ft.Ref[ft.Container]] = None,
    compare_btn_ref: Optional[ft.Ref[ft.ElevatedButton]] = None,
) -> ft.Control:
    search_field.on_change = lambda _e: on_search_change(search_field.value or "")

    compare_btn = primary_button(
        "Compare selected",
        on_click=on_compare,
        icon=ft.icons.COMPARE_ARROWS,
        disabled=len(selected_ids) != 2,
    )
    if compare_btn_ref is not None:
        compare_btn.ref = compare_btn_ref

    header = page_header(
        eyebrow="HISTORY",
        title="Every recommendation you've made.",
        subtitle="Search, review explanations, regenerate, or compare two side-by-side.",
        trailing=ft.Row(
            spacing=Spacing.sm,
            controls=[
                compare_btn,
                primary_button(
                    "New recommendation",
                    on_click=on_new_recommendation,
                    icon=ft.icons.AUTO_AWESOME,
                ),
            ],
        ),
    )

    body = render_history_body(
        items=items,
        selected_ids=selected_ids,
        search_query=search_field.value or "",
        on_view=on_view,
        on_regenerate=on_regenerate,
        on_compare_toggle=on_compare_toggle,
        on_new_recommendation=on_new_recommendation,
    )
    body_container = ft.Container(content=body)
    if body_ref is not None:
        body_container.ref = body_ref

    search_card = glass_card(
        ft.Row(
            spacing=Spacing.md,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.icons.SEARCH, size=20, color=Colors.text_secondary),
                ft.Container(content=search_field, expand=True),
            ],
        ),
        padding=Spacing.md,
    )

    return ft.Column(
        spacing=Spacing.xl,
        controls=[header, search_card, body_container],
    )
