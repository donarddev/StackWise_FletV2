# ACTIVE LEARNING HUB PAGE
"""Learning Hub page.

Minimum functional Learning Hub with sample topics only.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Callable, Mapping, Optional

import flet as ft

from app.services.learning_hub_service import LearningHubService
from app.models.learning_article import LearningArticle
from ui.components.glass_card import glass_card
from app.utils.constants import Routes
from ui.themes.app_theme import Radii, Spacing

LOGO_TILE_SIZE = 52


def _pal(t: Mapping[str, Any]) -> SimpleNamespace:
    """Theme-derived palette for Learning Hub cards and chrome."""
    return SimpleNamespace(
        SURFACE_BASE=t["surface"],
        SURFACE_CARD=t["surface_2"],
        SURFACE_CARD_HOVER=t["surface_3"],
        BORDER_SOFT=t["border_strong"],
        TEXT_PRIMARY=t["text"],
        TEXT_SECONDARY=t["text_secondary"],
        TEAL=t["accent_2"],
        PURPLE=t["accent"],
        AMBER=t["warning"],
        DANGER=t["danger"],
        LOGO_TILE_BG=t["surface_3"],
        LIMIT_FG=t["learning_chip_limit_fg"],
        TRADE_FG=t["learning_chip_trade_fg"],
        DIFF_FG=t["learning_chip_diff_fg"],
        BEST_FG=t["learning_chip_best_fg"],
        PURPLE_DEEP=t["accent_glow"],
        ON_GRAD=t["on_gradient"],
        BORDER=t["border"],
    )


def _topic_icon_block(topic: dict, p: SimpleNamespace) -> ft.Control:
    """Logo image when logo_path exists; otherwise initials fallback."""
    logo_path = topic.get("logo_path")
    if logo_path:
        inner = ft.Image(
            src=logo_path,
            width=34,
            height=34,
            fit=ft.ImageFit.CONTAIN,
        )
    else:
        inner = ft.Text(
            topic["icon"], size=12, weight=ft.FontWeight.W_700, color=p.TEXT_PRIMARY,
        )
    return ft.Container(
        width=LOGO_TILE_SIZE,
        height=LOGO_TILE_SIZE,
        border_radius=14,
        bgcolor=ft.colors.with_opacity(0.55, p.LOGO_TILE_BG),
        border=ft.border.all(1, ft.colors.with_opacity(0.4, p.TEAL)),
        padding=ft.padding.all(9),
        alignment=ft.alignment.center,
        clip_behavior=ft.ClipBehavior.NONE,
        shadow=ft.BoxShadow(
            blur_radius=12,
            spread_radius=0,
            color=ft.colors.with_opacity(0.14, p.TEAL),
            offset=ft.Offset(0, 4),
        ),
        content=inner,
    )


def render_learning_body(
    *,
    theme: Mapping[str, Any],
    articles: list[LearningArticle],
    on_open_article: Callable[[LearningArticle], None],
) -> ft.Control:
    """Compatibility renderer used by LearningController inline refresh."""
    p = _pal(theme)
    if not articles:
        return glass_card(
            ft.Text("No matching topics.", size=13, color=p.TEXT_SECONDARY),
            padding=Spacing.lg,
            theme=theme,
        )

    def _article_card(article: LearningArticle) -> ft.Control:
        title = getattr(article, "title", "Untitled topic")
        category = getattr(article, "category", "Topic")
        difficulty = getattr(article, "difficulty", "General")
        summary = getattr(article, "summary", None) or getattr(article, "description", "")
        return glass_card(
            ft.Column(
                spacing=Spacing.sm,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(title, size=17, weight=ft.FontWeight.W_700, color=p.TEXT_PRIMARY),
                            ft.Container(expand=True),
                            _chip(category, tone="category", p=p),
                            _chip(difficulty, tone="difficulty", p=p),
                        ],
                    ),
                    ft.Text(summary or "No summary available.", size=12.5, color=p.TEXT_SECONDARY),
                    ft.TextButton(
                        text="More details",
                        on_click=lambda _e, a=article: on_open_article(a),
                        style=ft.ButtonStyle(color=p.TEAL),
                    ),
                ],
            ),
            padding=Spacing.lg,
            theme=theme,
        )

    return ft.ResponsiveRow(
        spacing=Spacing.md,
        run_spacing=Spacing.md,
        controls=[
            ft.Container(
                col={"xs": 12, "md": 6, "lg": 4},
                content=_article_card(article),
            )
            for article in articles
        ],
    )


def render_category_pills(
    *,
    theme: Mapping[str, Any],
    categories: list[str],
    selected_category: str,
    on_category_change: Callable[[str], None],
) -> ft.Control:
    """Compatibility pills used by LearningController inline refresh."""
    p = _pal(theme)
    all_categories = ["All", *categories]
    return ft.Row(
        wrap=True,
        spacing=Spacing.sm,
        run_spacing=Spacing.sm,
        controls=[
            ft.Container(
                on_click=lambda _e, c=cat: on_category_change(c),
                ink=True,
                border_radius=Radii.pill,
                border=ft.border.all(1, p.BORDER),
                bgcolor=ft.colors.with_opacity(0.22, p.PURPLE)
                if selected_category == cat
                else p.SURFACE_BASE,
                padding=ft.padding.symmetric(horizontal=14, vertical=8),
                content=ft.Text(
                    cat,
                    size=12.5,
                    weight=ft.FontWeight.W_700 if selected_category == cat else ft.FontWeight.W_600,
                    color=p.TEXT_PRIMARY if selected_category == cat else p.TEXT_SECONDARY,
                ),
            )
            for cat in all_categories
        ],
    )


def _display_category(category: str) -> str:
    if category == "language":
        return "Languages"
    if category == "framework":
        return "Frameworks"
    if category == "sdlc":
        return "SDLC Models"
    return "Topic"


def _chip(label: str, *, p: SimpleNamespace, tone: str = "default") -> ft.Control:
    if tone == "category":
        bg = ft.colors.with_opacity(0.18, p.TEAL)
        fg = p.TEXT_PRIMARY
    elif tone == "difficulty":
        bg = ft.colors.with_opacity(0.20, p.PURPLE)
        fg = p.DIFF_FG
    elif tone == "best_for":
        bg = ft.colors.with_opacity(0.18, p.TEAL)
        fg = p.BEST_FG
    elif tone == "limitation":
        bg = ft.colors.with_opacity(0.22, p.AMBER)
        fg = p.LIMIT_FG
    elif tone == "tradeoff":
        bg = ft.colors.with_opacity(0.16, p.DANGER)
        fg = p.TRADE_FG
    else:
        bg = ft.colors.with_opacity(0.56, p.SURFACE_BASE)
        fg = p.TEXT_SECONDARY
    return ft.Container(
        bgcolor=bg,
        border=ft.border.all(1, ft.colors.with_opacity(0.45, p.BORDER_SOFT)),
        border_radius=Radii.pill,
        padding=ft.padding.symmetric(horizontal=10, vertical=5),
        content=ft.Text(label, size=11, color=fg, weight=ft.FontWeight.W_600),
    )


def _hoverable_card(content: ft.Control, p: SimpleNamespace, *, padding=Spacing.lg, border_radius=Radii.lg) -> ft.Container:
    ref = ft.Ref[ft.Container]()

    def on_hover(e: ft.HoverEvent) -> None:
        if ref.current is None:
            return
        hovering = e.data == "true"
        ref.current.bgcolor = p.SURFACE_CARD_HOVER if hovering else p.SURFACE_CARD
        ref.current.border = ft.border.all(
            1.2,
            ft.colors.with_opacity(0.85, p.TEAL if hovering else p.BORDER_SOFT),
        )
        if e.control.page:
            ref.current.update()

    return ft.Container(
        ref=ref,
        on_hover=on_hover,
        bgcolor=p.SURFACE_CARD,
        border=ft.border.all(1.2, ft.colors.with_opacity(0.65, p.BORDER_SOFT)),
        border_radius=border_radius,
        padding=padding,
        shadow=ft.BoxShadow(
            blur_radius=30,
            spread_radius=0,
            color=ft.colors.with_opacity(0.12, p.PURPLE),
            offset=ft.Offset(0, 10),
        ),
        content=content,
    )


def _hover_pill(
    label: str,
    p: SimpleNamespace,
    *,
    selected: bool,
    on_click: Callable[[ft.ControlEvent], None],
) -> ft.Container:
    ref = ft.Ref[ft.Container]()

    def on_hover(e: ft.HoverEvent) -> None:
        if ref.current is None:
            return
        hovering = e.data == "true"
        if selected:
            ref.current.gradient = ft.LinearGradient(
                begin=ft.alignment.center_left,
                end=ft.alignment.center_right,
                colors=[p.TEAL, p.PURPLE_DEEP if hovering else p.PURPLE],
            )
        else:
            ref.current.bgcolor = ft.colors.with_opacity(0.26 if hovering else 0.12, p.PURPLE)
            ref.current.border = ft.border.all(
                1,
                ft.colors.with_opacity(0.75 if hovering else 0.5, p.BORDER_SOFT),
            )
        if e.control.page:
            ref.current.update()

    return ft.Container(
        ref=ref,
        on_hover=on_hover,
        on_click=on_click,
        ink=True,
        border_radius=Radii.pill,
        gradient=ft.LinearGradient(
            begin=ft.alignment.center_left,
            end=ft.alignment.center_right,
            colors=[p.TEAL, p.PURPLE],
        )
        if selected
        else None,
        bgcolor=None if selected else ft.colors.with_opacity(0.12, p.PURPLE),
        border=ft.border.all(1, ft.colors.with_opacity(0.5, p.BORDER_SOFT)),
        padding=ft.padding.symmetric(horizontal=15, vertical=9),
        content=ft.Text(
            label,
            size=12.5,
            weight=ft.FontWeight.W_700 if selected else ft.FontWeight.W_600,
            color=p.ON_GRAD if selected else p.TEXT_SECONDARY,
        ),
    )


def _hover_action_button(text: str, icon: str, on_click: Callable[[ft.ControlEvent], None], p: SimpleNamespace) -> ft.Control:
    ref = ft.Ref[ft.Container]()

    def on_hover(e: ft.HoverEvent) -> None:
        if ref.current is None:
            return
        hovering = e.data == "true"
        ref.current.gradient = ft.LinearGradient(
            begin=ft.alignment.center_left,
            end=ft.alignment.center_right,
            colors=[p.TEAL, p.PURPLE_DEEP if hovering else p.PURPLE],
        )
        ref.current.shadow = ft.BoxShadow(
            blur_radius=30 if hovering else 18,
            spread_radius=0,
            color=ft.colors.with_opacity(0.35 if hovering else 0.22, p.TEAL),
            offset=ft.Offset(0, 8),
        )
        if e.control.page:
            ref.current.update()

    return ft.Container(
        ref=ref,
        on_click=on_click,
        on_hover=on_hover,
        ink=True,
        border_radius=Radii.pill,
        padding=ft.padding.symmetric(horizontal=18, vertical=12),
        gradient=ft.LinearGradient(
            begin=ft.alignment.center_left,
            end=ft.alignment.center_right,
            colors=[p.TEAL, p.PURPLE],
        ),
        shadow=ft.BoxShadow(
            blur_radius=18,
            spread_radius=0,
            color=ft.colors.with_opacity(0.22, p.TEAL),
            offset=ft.Offset(0, 8),
        ),
        content=ft.Row(
            tight=True,
            spacing=8,
            controls=[
                ft.Icon(icon, size=16, color=p.ON_GRAD),
                ft.Text(text, size=13, weight=ft.FontWeight.W_700, color=p.ON_GRAD),
            ],
        ),
    )


def _details_list(items: list[str], p: SimpleNamespace) -> ft.Column:
    return ft.Column(
        spacing=6,
        controls=[
            ft.Row(
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Icon(ft.icons.CHECK_CIRCLE_OUTLINE_ROUNDED, size=14, color=p.TEAL),
                    ft.Text(item, size=12.5, color=p.TEXT_SECONDARY, expand=True),
                ],
            )
            for item in items
        ],
    )


def _topic_card(
    topic: dict,
    p: SimpleNamespace,
    *,
    expanded: bool,
    on_toggle: Callable[[ft.ControlEvent], None],
) -> ft.Control:
    limitations = topic.get("limitations", [])
    first_limitation = limitations[0] if limitations else "No limitations listed."
    related_tech = list(topic.get("common_frameworks", []))
    related_language = topic.get("related_language")
    if related_language:
        related_tech.append(related_language)
    learning_path = topic.get("learning_path", [])
    next_step = learning_path[-1] if learning_path else "Continue exploring this topic."

    top_row = ft.Row(
        spacing=Spacing.sm,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            _topic_icon_block(topic, p),
            ft.Column(
                spacing=2,
                tight=True,
                expand=True,
                controls=[
                    ft.Text(topic["name"], size=18, weight=ft.FontWeight.W_700, color=p.TEXT_PRIMARY),
                    ft.Text(_display_category(topic["category"]), size=11.5, color=p.TEXT_SECONDARY),
                ],
            ),
            _chip(topic["difficulty"], tone="difficulty", p=p),
        ],
    )

    def section_label(text: str) -> ft.Control:
        return ft.Text(text, size=10.5, weight=ft.FontWeight.W_700, color=p.TEXT_SECONDARY)

    preview_advantages = topic.get("advantages", [])[:2]
    preview_limitations = topic.get("limitations", [])[:1]

    details = ft.Container()
    if expanded:
        details = ft.Container(
            margin=ft.margin.only(top=Spacing.md),
            padding=Spacing.md,
            bgcolor=ft.colors.with_opacity(0.35, p.SURFACE_BASE),
            border=ft.border.all(1, ft.colors.with_opacity(0.55, p.BORDER_SOFT)),
            border_radius=Radii.md,
            content=ft.Column(
                spacing=Spacing.sm,
                controls=[
                    ft.Text("Advantages", size=12, weight=ft.FontWeight.W_700, color=p.TEXT_PRIMARY),
                    _details_list(topic["advantages"], p),
                    ft.Text("Trade-offs", size=12, weight=ft.FontWeight.W_700, color=p.TEXT_PRIMARY),
                    ft.Column(
                        spacing=6,
                        controls=[
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Icon(ft.icons.REPORT_GMAILERRORRED_ROUNDED, size=14, color=p.AMBER),
                                    ft.Text(item, size=12.5, color=p.TEXT_SECONDARY, expand=True),
                                ],
                            )
                            for item in topic["limitations"]
                        ],
                    ),
                    _chip(f"Example project: {topic.get('example_project', 'N/A')}", tone="best_for", p=p),
                    ft.Text(f"Beginner advice: {topic['beginner_advice']}", size=12.5, color=p.TEXT_SECONDARY),
                    ft.Text(
                        f"Related technologies: {', '.join(related_tech) if related_tech else 'N/A'}",
                        size=12.5,
                        color=p.TEXT_SECONDARY,
                    ),
                    ft.Text("Learning path", size=12, weight=ft.FontWeight.W_700, color=p.TEXT_PRIMARY),
                    _details_list(learning_path if learning_path else [next_step], p),
                ],
            ),
        )

    return _hoverable_card(
        ft.Container(
            height=None if expanded else 620,
            content=ft.Column(
                spacing=Spacing.sm,
                controls=[
                    top_row,
                    ft.Row(
                        wrap=True,
                        spacing=Spacing.xs,
                        run_spacing=Spacing.xs,
                        controls=[
                            _chip(_display_category(topic["category"]), tone="category", p=p),
                        ],
                    ),
                    ft.Row(
                        wrap=True,
                        spacing=Spacing.xs,
                        run_spacing=Spacing.xs,
                        controls=[_chip(use_case, tone="best_for", p=p) for use_case in topic["tags"]],
                    ),
                    ft.Text(topic["description"], size=13, color=p.TEXT_SECONDARY),
                    section_label("BEST FOR"),
                    ft.Row(
                        wrap=True,
                        spacing=Spacing.xs,
                        run_spacing=Spacing.xs,
                        controls=[_chip(topic["best_for"], tone="best_for", p=p)],
                    ),
                    section_label("TOP ADVANTAGES"),
                    ft.Column(
                        spacing=4,
                        controls=[
                            ft.Row(
                                spacing=8,
                                controls=[
                                    ft.Icon(ft.icons.CHECK_CIRCLE_OUTLINE_ROUNDED, size=13, color=p.TEAL),
                                    ft.Text(adv, size=12.2, color=p.TEXT_SECONDARY, expand=True),
                                ],
                            )
                            for adv in preview_advantages
                        ],
                    ),
                    section_label("KEY LIMITATION"),
                    ft.Row(
                        wrap=True,
                        spacing=Spacing.xs,
                        run_spacing=Spacing.xs,
                        controls=[_chip(preview_limitations[0] if preview_limitations else first_limitation, tone="limitation", p=p)],
                    ),
                    section_label("RECOMMENDED WHEN"),
                    ft.Text(topic.get("recommended_when", "N/A"), size=12.2, color=p.TEXT_SECONDARY),
                    section_label("AVOID WHEN"),
                    ft.Text(topic.get("avoid_when", "N/A"), size=12.2, color=p.TEXT_SECONDARY),
                    section_label("REFERENCES"),
                    ft.Text(", ".join(topic.get("references", [])), size=11.5, color=p.TEXT_SECONDARY),
                    *(
                        [
                            section_label("COMMON FRAMEWORKS"),
                            ft.Row(
                                wrap=True,
                                spacing=Spacing.xs,
                                run_spacing=Spacing.xs,
                                controls=[_chip(item, p=p) for item in topic.get("common_frameworks", [])],
                            ),
                        ]
                        if topic.get("category") == "language" and topic.get("common_frameworks")
                        else []
                    ),
                    *(
                        [
                            section_label("EXAMPLE PROJECT"),
                            ft.Text(topic.get("example_project", "N/A"), size=12.2, color=p.TEXT_SECONDARY),
                        ]
                        if topic.get("category") == "sdlc"
                        else []
                    ),
                    ft.TextButton(
                        text="More details" if not expanded else "Hide details",
                        icon=ft.icons.EXPAND_MORE if not expanded else ft.icons.EXPAND_LESS,
                        style=ft.ButtonStyle(color=p.TEAL),
                        on_click=on_toggle,
                    ),
                    details,
                ],
            ),
        ),
        p,
        padding=Spacing.md,
    )


def build_learning_page(
    *,
    theme: Mapping[str, Any],
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
    del articles, categories, selected_category, search_field, on_search_change, on_category_change, on_open_article

    p = _pal(theme)
    service = LearningHubService()
    category_counts = service.count_by_category()
    tab_to_category = {
        "All topics": "All topics",
        "Languages": "Languages",
        "Frameworks": "Frameworks",
        "SDLC models": "SDLC Models",
    }
    state = {
        "query": "",
        "tab": "All topics",
        "dropdown": "All topics",
        "expanded_id": None,
    }

    search_input_ref = ft.Ref[ft.TextField]()
    category_dropdown_ref = ft.Ref[ft.Dropdown]()
    filters_ref = ft.Ref[ft.Column]()
    cards_ref = body_ref or ft.Ref[ft.Container]()
    tabs_ref = pills_ref or ft.Ref[ft.Container]()

    def start_recommendation(e: ft.ControlEvent) -> None:
        if e.control.page:
            e.control.page.go(Routes.RECOMMENDATION)

    def render_tabs() -> ft.Control:
        tab_labels = ["All topics", "Languages", "Frameworks", "SDLC models"]
        return ft.Row(
            wrap=True,
            spacing=Spacing.sm,
            run_spacing=Spacing.sm,
            controls=[
                _hover_pill(
                    label,
                    p,
                    selected=(state["tab"] == label),
                    on_click=lambda _e, lbl=label: set_tab(lbl),
                )
                for label in tab_labels
            ],
        )

    def render_cards() -> ft.Control:
        filtered = service.search_topics(state["query"], state["dropdown"])
        if not filtered:
            return _hoverable_card(
                ft.Text(
                    "No topics match your filter. Try a broader keyword or category.",
                    size=14,
                    color=p.TEXT_SECONDARY,
                ),
                p,
            )
        return ft.ResponsiveRow(
            spacing=Spacing.md,
            run_spacing=Spacing.md,
            controls=[
                ft.Container(
                    col={"xs": 12, "md": 6, "lg": 4},
                    content=_topic_card(
                        topic,
                        p,
                        expanded=(state["expanded_id"] == topic["id"]),
                        on_toggle=lambda _e, topic_id=topic["id"]: toggle_details(_e, topic_id),
                    ),
                )
                for topic in filtered
            ],
        )

    def sync_ui_after_filter(control: ft.Control) -> None:
        if cards_ref.current is not None:
            cards_ref.current.content = render_cards()
            if control.page:
                cards_ref.current.update()
        if tabs_ref.current is not None:
            tabs_ref.current.content = render_tabs()
            if control.page:
                tabs_ref.current.update()
        if filters_ref.current is not None:
            if control.page:
                filters_ref.current.update()

    def apply_filters(e: ft.ControlEvent) -> None:
        if search_input_ref.current is not None:
            state["query"] = (search_input_ref.current.value or "").strip()
        if category_dropdown_ref.current is not None:
            state["dropdown"] = category_dropdown_ref.current.value or "All topics"
        state["expanded_id"] = None
        sync_ui_after_filter(e.control)

    def clear_filters(e: ft.ControlEvent) -> None:
        state["query"] = ""
        state["tab"] = "All topics"
        state["dropdown"] = "All topics"
        state["expanded_id"] = None
        if search_input_ref.current is not None:
            search_input_ref.current.value = ""
        if category_dropdown_ref.current is not None:
            category_dropdown_ref.current.value = "All topics"
        sync_ui_after_filter(e.control)

    def set_tab(tab_label: str) -> None:
        state["tab"] = tab_label
        state["dropdown"] = tab_to_category[tab_label]
        if category_dropdown_ref.current is not None:
            category_dropdown_ref.current.value = state["dropdown"]
        if cards_ref.current is not None:
            cards_ref.current.content = render_cards()
            if cards_ref.current.page:
                cards_ref.current.update()
        if tabs_ref.current is not None:
            tabs_ref.current.content = render_tabs()
            if tabs_ref.current.page:
                tabs_ref.current.update()
        if filters_ref.current is not None and filters_ref.current.page:
            filters_ref.current.update()

    def toggle_details(e: ft.ControlEvent, topic_id: str) -> None:
        state["expanded_id"] = None if state["expanded_id"] == topic_id else topic_id
        if cards_ref.current is not None:
            cards_ref.current.content = render_cards()
            if e.control.page:
                cards_ref.current.update()

    hero = _hoverable_card(
        ft.Column(
            spacing=Spacing.md,
            controls=[
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=11, vertical=7),
                    border_radius=Radii.pill,
                    bgcolor=ft.colors.with_opacity(0.16, p.TEAL),
                    border=ft.border.all(1, ft.colors.with_opacity(0.5, p.BORDER_SOFT)),
                    content=ft.Text(
                        "Learning Hub",
                        size=11.5,
                        weight=ft.FontWeight.W_700,
                        color=p.TEXT_PRIMARY,
                    ),
                ),
                ft.Text(
                    "Explore languages, frameworks, and SDLC models",
                    size=36,
                    weight=ft.FontWeight.W_700,
                    color=p.TEXT_PRIMARY,
                ),
                ft.Text(
                    "Use this guide to understand the technologies and process models that "
                    "StackWise AI may recommend for your project.",
                    size=14,
                    color=p.TEXT_SECONDARY,
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.END,
                    controls=[
                        _hover_action_button(
                            "Start Recommendation",
                            ft.icons.AUTO_AWESOME,
                            start_recommendation,
                            p,
                        ),
                    ],
                ),
            ],
        ),
        p,
        padding=Spacing.xl,
        border_radius=Radii.xl,
    )

    def stat_card(label: str, value: str, icon_name: str) -> ft.Control:
        return _hoverable_card(
            ft.Row(
                controls=[
                    ft.Container(
                        width=38,
                        height=38,
                        border_radius=11,
                        bgcolor=ft.colors.with_opacity(0.14, p.PURPLE),
                        border=ft.border.all(1, ft.colors.with_opacity(0.45, p.BORDER_SOFT)),
                        alignment=ft.alignment.center,
                        content=ft.Icon(icon_name, size=17, color=p.TEXT_PRIMARY),
                    ),
                    ft.Column(
                        spacing=4,
                        tight=True,
                        expand=True,
                        controls=[
                            ft.Text(label, size=11.5, color=p.TEXT_SECONDARY),
                            ft.Text(value, size=28, weight=ft.FontWeight.W_700, color=p.TEXT_PRIMARY),
                        ],
                    ),
                ],
            ),
            p,
            padding=Spacing.lg,
        )

    stats_row = ft.ResponsiveRow(
        spacing=Spacing.md,
        run_spacing=Spacing.md,
        controls=[
            ft.Container(
                col={"xs": 12, "md": 4},
                content=stat_card(
                    "Programming Languages",
                    str(category_counts.get("languages", 0)),
                    ft.icons.CODE_ROUNDED,
                ),
            ),
            ft.Container(
                col={"xs": 12, "md": 4},
                content=stat_card(
                    "Frameworks",
                    str(category_counts.get("frameworks", 0)),
                    ft.icons.WIDGETS_ROUNDED,
                ),
            ),
            ft.Container(
                col={"xs": 12, "md": 4},
                content=stat_card(
                    "SDLC Models",
                    str(category_counts.get("sdlc_models", 0)),
                    ft.icons.ACCOUNT_TREE_ROUNDED,
                ),
            ),
        ],
    )

    tabs_container = ft.Container(ref=tabs_ref, content=render_tabs())

    filter_panel = _hoverable_card(
        ft.Column(
            ref=filters_ref,
            spacing=Spacing.md,
            controls=[
                ft.Text("Search and filter", size=13, weight=ft.FontWeight.W_600, color=p.TEXT_SECONDARY),
                ft.ResponsiveRow(
                    spacing=Spacing.md,
                    run_spacing=Spacing.md,
                    controls=[
                        ft.Container(
                            col={"xs": 12, "md": 7},
                            content=ft.TextField(
                                ref=search_input_ref,
                                hint_text='Try "API", "mobile", "Agile", "beginner", or "AI"',
                                height=44,
                                content_padding=ft.padding.symmetric(horizontal=14, vertical=10),
                                border_radius=Radii.md,
                                bgcolor=ft.colors.with_opacity(0.56, p.SURFACE_BASE),
                                border_color=ft.colors.with_opacity(0.5, p.BORDER_SOFT),
                                focused_border_color=p.TEAL,
                                text_size=13.5,
                                color=p.TEXT_PRIMARY,
                                hint_style=ft.TextStyle(color=p.TEXT_SECONDARY, size=12.5),
                            ),
                        ),
                        ft.Container(
                            col={"xs": 12, "md": 3},
                            content=ft.Dropdown(
                                ref=category_dropdown_ref,
                                value="All topics",
                                height=44,
                                options=[
                                    ft.dropdown.Option("All topics"),
                                    ft.dropdown.Option("Languages"),
                                    ft.dropdown.Option("Frameworks"),
                                    ft.dropdown.Option("SDLC Models"),
                                ],
                                border_radius=Radii.md,
                                bgcolor=ft.colors.with_opacity(0.56, p.SURFACE_BASE),
                                border_color=ft.colors.with_opacity(0.5, p.BORDER_SOFT),
                                focused_border_color=p.TEAL,
                                text_size=13.5,
                                color=p.TEXT_PRIMARY,
                            ),
                        ),
                        ft.Container(
                            col={"xs": 12, "md": 2},
                            content=ft.Row(
                                spacing=Spacing.sm,
                                controls=[
                                    ft.ElevatedButton(
                                        text="Apply filters",
                                        style=ft.ButtonStyle(
                                            bgcolor=ft.colors.with_opacity(0.2, p.TEAL),
                                            color=p.TEXT_PRIMARY,
                                            side=ft.BorderSide(1, ft.colors.with_opacity(0.5, p.BORDER_SOFT)),
                                            shape=ft.RoundedRectangleBorder(radius=12),
                                        ),
                                        on_click=apply_filters,
                                    ),
                                    ft.OutlinedButton(
                                        text="Clear filters",
                                        style=ft.ButtonStyle(
                                            color=p.TEXT_SECONDARY,
                                            side=ft.BorderSide(1, ft.colors.with_opacity(0.5, p.BORDER_SOFT)),
                                            shape=ft.RoundedRectangleBorder(radius=12),
                                        ),
                                        on_click=clear_filters,
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
            ],
        ),
        p,
        padding=Spacing.lg,
    )

    cards_container = ft.Container(ref=cards_ref, content=render_cards())

    page = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=Spacing.lg,
        controls=[
            hero,
            stats_row,
            tabs_container,
            filter_panel,
            cards_container,
        ],
    )

    return page
