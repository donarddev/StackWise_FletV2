"""Dashboard page — analytics overview + recent activity."""

from __future__ import annotations

from typing import Callable

import flet as ft

from app.models.recommendation import Recommendation
from app.models.user import User
from app.services.analytics_service import DashboardSnapshot
from ui.components.empty_state import empty_state
from ui.components.glass_card import glass_card
from ui.components.page_header import page_header
from ui.components.primary_button import primary_button, secondary_button
from ui.components.section_header import section_header
from ui.components.stat_card import stat_card
from ui.themes.app_theme import Colors, Spacing, Typography
from ui.widgets.recommendation_card import recommendation_result_card
from ui.widgets.top_list import top_list
from ui.widgets.trend_chart import trend_chart


def build_dashboard_page(
    *,
    user: User,
    snapshot: DashboardSnapshot,
    recent: list[Recommendation],
    on_new_recommendation: Callable[[ft.ControlEvent], None],
    on_open_history: Callable[[ft.ControlEvent], None],
    on_open_chatbot: Callable[[ft.ControlEvent], None],
    on_view_recommendation: Callable[[Recommendation], None],
    on_regenerate: Callable[[Recommendation], None],
) -> ft.Control:
    header = page_header(
        eyebrow="DASHBOARD",
        title=f"Welcome back, {user.full_name.split()[0]}.",
        subtitle="A snapshot of your recommendation activity, top stacks, and AI insights.",
        trailing=ft.Row(
            spacing=Spacing.sm,
            controls=[
                secondary_button(
                    "Ask AI",
                    on_click=on_open_chatbot,
                    icon=ft.icons.CHAT_BUBBLE_OUTLINE,
                ),
                primary_button(
                    "New recommendation",
                    on_click=on_new_recommendation,
                    icon=ft.icons.AUTO_AWESOME,
                ),
            ],
        ),
    )

    stats = ft.ResponsiveRow(
        spacing=Spacing.md, run_spacing=Spacing.md,
        controls=[
            ft.Container(col={"xs": 12, "md": 4}, content=stat_card(
                title="Total recommendations",
                value=str(snapshot.total_recommendations),
                subtitle="All projects analyzed by StackWise",
                icon=ft.icons.AUTO_AWESOME_OUTLINED,
                accent=Colors.primary,
            )),
            ft.Container(col={"xs": 12, "md": 4}, content=stat_card(
                title="Average confidence",
                value=f"{snapshot.average_confidence:.0f}/100"
                       if snapshot.average_confidence else "—",
                subtitle="Engine certainty across your decisions",
                icon=ft.icons.INSIGHTS_OUTLINED,
                accent=Colors.accent_cyan,
            )),
            ft.Container(col={"xs": 12, "md": 4}, content=stat_card(
                title="Top language",
                value=snapshot.top_languages[0][0] if snapshot.top_languages else "—",
                subtitle=(
                    f"Used in {snapshot.top_languages[0][1]} recommendations"
                    if snapshot.top_languages else "Generate one to see your favorites"
                ),
                icon=ft.icons.CODE_ROUNDED,
                accent=Colors.accent_pink,
            )),
        ],
    )

    insights = glass_card(
        ft.Column(
            spacing=Spacing.md,
            controls=[
                ft.Row(
                    spacing=Spacing.sm,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=28, height=28, border_radius=8,
                            bgcolor=ft.colors.with_opacity(0.14, Colors.primary),
                            alignment=ft.alignment.center,
                            content=ft.Icon(ft.icons.TIPS_AND_UPDATES_OUTLINED,
                                            size=16, color=Colors.primary_glow),
                        ),
                        ft.Text("AI Insights", style=Typography.subheading(size=15)),
                    ],
                ),
                *[
                    ft.Row(
                        controls=[
                            ft.Container(
                                width=6, height=6, border_radius=999,
                                bgcolor=Colors.primary_glow,
                                margin=ft.margin.only(top=8),
                            ),
                            ft.Text(insight, style=Typography.body(size=13.5), expand=True),
                        ],
                        spacing=Spacing.sm,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    )
                    for insight in snapshot.insights
                ],
            ],
        )
    )

    columns = ft.ResponsiveRow(
        spacing=Spacing.md, run_spacing=Spacing.md,
        controls=[
            ft.Container(col={"xs": 12, "lg": 8}, content=trend_chart(snapshot.weekly_trend)),
            ft.Container(col={"xs": 12, "lg": 4}, content=insights),
        ],
    )

    rankings = ft.ResponsiveRow(
        spacing=Spacing.md, run_spacing=Spacing.md,
        controls=[
            ft.Container(col={"xs": 12, "md": 4}, content=top_list(
                title="Top languages", items=snapshot.top_languages,
                icon=ft.icons.CODE_ROUNDED, accent=Colors.primary,
                empty_text="Run a recommendation to populate this list.",
            )),
            ft.Container(col={"xs": 12, "md": 4}, content=top_list(
                title="Top frameworks", items=snapshot.top_frameworks,
                icon=ft.icons.DASHBOARD_CUSTOMIZE_OUTLINED, accent=Colors.accent_cyan,
                empty_text="Run a recommendation to populate this list.",
            )),
            ft.Container(col={"xs": 12, "md": 4}, content=top_list(
                title="Top SDLC models", items=snapshot.top_sdlc,
                icon=ft.icons.ALT_ROUTE_OUTLINED, accent=Colors.accent_pink,
                empty_text="Run a recommendation to populate this list.",
            )),
        ],
    )

    if recent:
        recent_section = ft.Column(
            spacing=Spacing.md,
            controls=[
                section_header(
                    "Recent recommendations",
                    subtitle="Your last few project analyses",
                    trailing=ft.TextButton(
                        "View all", icon=ft.icons.ARROW_FORWARD,
                        on_click=on_open_history,
                    ),
                ),
                *[
                    recommendation_result_card(
                        r,
                        on_view=lambda _e, rec=r: on_view_recommendation(rec),
                        on_regenerate=lambda _e, rec=r: on_regenerate(rec),
                    )
                    for r in recent
                ],
            ],
        )
    else:
        recent_section = empty_state(
            icon=ft.icons.AUTO_AWESOME_OUTLINED,
            title="Generate your first recommendation",
            description=(
                "Tell StackWise about your project and get an explainable language, "
                "framework, and SDLC pick — usually in under a second."
            ),
            action=primary_button(
                "Start a recommendation",
                on_click=on_new_recommendation,
                icon=ft.icons.AUTO_AWESOME,
            ),
        )

    return ft.Column(
        spacing=Spacing.xl,
        controls=[header, stats, columns, rankings, recent_section],
    )
