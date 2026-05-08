"""Learning Hub page.

The page builder accepts ``body_ref`` and ``pills_ref`` so the controller
can refresh the article grid and category pills in place — no full page
rebuild on every keystroke / pill click.
"""

from __future__ import annotations

from typing import Callable, Optional

import flet as ft

from app.models.learning_article import LearningArticle
from ui.components.empty_state import empty_state
from ui.components.glass_card import glass_card
from ui.components.page_header import page_header
from ui.themes.app_theme import Colors, Radii, Spacing
from ui.widgets.learning_card import learning_card


def render_learning_body(
    *,
    articles: list[LearningArticle],
    on_open_article: Callable[[LearningArticle], None],
) -> ft.Control:
    if not articles:
        return empty_state(
            icon=ft.icons.SEARCH_OFF_OUTLINED,
            title="No matching articles",
            description="Try a different search or category.",
        )
    return ft.ResponsiveRow(
        spacing=Spacing.md, run_spacing=Spacing.md,
        controls=[
            ft.Container(
                col={"xs": 12, "md": 6, "lg": 4},
                content=learning_card(article, on_open=on_open_article),
            )
            for article in articles
        ],
    )


def render_category_pills(
    *,
    categories: list[str],
    selected_category: str,
    on_category_change: Callable[[str], None],
) -> ft.Control:
    return ft.Row(
        wrap=True, spacing=Spacing.sm, run_spacing=Spacing.sm,
        controls=[
            _pill("All", selected=(selected_category == "All"),
                  on_click=lambda _e: on_category_change("All")),
            *[
                _pill(cat, selected=(selected_category == cat),
                      on_click=lambda _e, c=cat: on_category_change(c))
                for cat in categories
            ],
        ],
    )


def build_learning_page(
    *,
    articles: list[LearningArticle],
    categories: list[str],
    selected_category: str,
    search_field: ft.TextField,
    on_search_change: Callable[[str], None],
    on_category_change: Callable[[str], None],
    on_open_article: Callable[[LearningArticle], None],
    body_ref: Optional[ft.Ref[ft.Container]] = None,
    pills_ref: Optional[ft.Ref[ft.Container]] = None,
) -> ft.Control:
    search_field.on_change = lambda _e: on_search_change(search_field.value or "")

    pills_container = ft.Container(
        content=render_category_pills(
            categories=categories,
            selected_category=selected_category,
            on_category_change=on_category_change,
        ),
    )
    if pills_ref is not None:
        pills_container.ref = pills_ref

    search_row = glass_card(
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

    body_container = ft.Container(
        content=render_learning_body(articles=articles, on_open_article=on_open_article),
    )
    if body_ref is not None:
        body_container.ref = body_ref

    return ft.Column(
        spacing=Spacing.xl,
        controls=[
            page_header(
                eyebrow="LEARNING HUB",
                title="Curated guidance, on tap.",
                subtitle="Languages, frameworks, methodologies, and software-engineering essentials.",
            ),
            search_row,
            pills_container,
            body_container,
        ],
    )


def _pill(label: str, *, selected: bool, on_click) -> ft.Control:
    if selected:
        return ft.Container(
            on_click=on_click, ink=True,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left, end=ft.alignment.bottom_right,
                colors=[Colors.primary, "#6366f1"],
            ),
            border_radius=Radii.pill,
            padding=ft.padding.symmetric(horizontal=14, vertical=8),
            content=ft.Text(label, size=12.5, weight=ft.FontWeight.W_700,
                            color=Colors.text_primary),
        )
    return ft.Container(
        on_click=on_click, ink=True,
        bgcolor=Colors.surface,
        border=ft.border.all(1, Colors.border),
        border_radius=Radii.pill,
        padding=ft.padding.symmetric(horizontal=14, vertical=8),
        content=ft.Text(label, size=12.5, weight=ft.FontWeight.W_600,
                        color=Colors.text_secondary),
    )
