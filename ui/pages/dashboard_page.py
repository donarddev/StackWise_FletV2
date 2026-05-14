# ACTIVE DASHBOARD PAGE
"""Dashboard page — analytics overview + recent activity.

ACTIVE AUTHENTICATED PAGE - Rendered by DashboardController via wrap_with_layout
Implements premium dark SaaS dashboard matching Laravel version structure but adapted for Flet.

Layout:
1. Workspace Welcome Hero Card (top)
2. Analytics Cards Grid (7 cards)
3. Recent Recommendations Table (bottom)
"""

from __future__ import annotations

from typing import Any, Callable, Mapping

import flet as ft

from app.models.recommendation import Recommendation
from app.models.user import User
from app.services.analytics_service import DashboardSnapshot
from ui.components.dashboard.analytics_card import dashboard_analytics_card
from ui.components.dashboard.hero_card import dashboard_hero_card
from ui.components.dashboard.recent_recommendations_table import dashboard_recent_recommendations_table
from ui.themes.app_theme import Spacing


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
    theme: Mapping[str, Any],
) -> ft.Control:
    """Build the complete dashboard page with hero, analytics, and recent recommendations."""

    # 1. WORKSPACE WELCOME HERO CARD
    hero = dashboard_hero_card(
        user_name=user.full_name,
        on_new_recommendation=on_new_recommendation,
        on_view_history=on_open_history,
        theme=theme,
    )

    # 2. ANALYTICS CARDS GRID (7 cards)
    # Calculate confidence percentage with fallback
    avg_confidence_pct = f"{snapshot.average_confidence:.0f}%" if snapshot.average_confidence else "—"

    # Get top language and framework with fallbacks
    top_language = snapshot.top_languages[0][0] if snapshot.top_languages else "—"
    top_language_desc = (
        f"Most frequently suggested language"
        if snapshot.top_languages
        else "Generate recommendations to populate"
    )

    top_framework = snapshot.top_frameworks[0][0] if snapshot.top_frameworks else "—"
    top_framework_desc = (
        f"Most frequently suggested framework"
        if snapshot.top_frameworks
        else "Generate recommendations to populate"
    )

    top_sdlc = snapshot.top_sdlc[0][0] if snapshot.top_sdlc else "—"
    top_sdlc_desc = (
        f"Most frequently suggested process model"
        if snapshot.top_sdlc
        else "Generate recommendations to populate"
    )

    # Format feedback and rating values
    total_feedback = snapshot.total_feedback if snapshot.total_feedback > 0 else "0"
    feedback_desc = (
        f"Feedback submissions received"
        if snapshot.total_feedback > 0
        else "No feedback yet"
    )

    avg_rating_display = f"{snapshot.average_rating:.1f}/5" if snapshot.average_rating > 0 else "—"
    rating_desc = (
        f"Average user satisfaction rating"
        if snapshot.average_rating > 0
        else "No ratings yet"
    )

    analytics_grid = ft.ResponsiveRow(
        spacing=20,
        run_spacing=20,
        controls=[
            # Card 1: Total Recommendations
            ft.Container(
                col={"xs": 12, "sm": 6, "md": 4, "lg": 3},
                content=dashboard_analytics_card(
                    title="Total Recommendations",
                    value=snapshot.total_recommendations,
                    description="Saved recommendation records",
                    icon="auto_awesome_outlined",
                    accent_color=theme["accent"],
                    theme=theme,
                ),
            ),
            # Card 2: Average Confidence
            ft.Container(
                col={"xs": 12, "sm": 6, "md": 4, "lg": 3},
                content=dashboard_analytics_card(
                    title="Average Confidence",
                    value=avg_confidence_pct,
                    description="Average score from all recommendations",
                    icon="insights_outlined",
                    accent_color=theme["accent_2"],
                    theme=theme,
                ),
            ),
            # Card 3: Top Language
            ft.Container(
                col={"xs": 12, "sm": 6, "md": 4, "lg": 3},
                content=dashboard_analytics_card(
                    title="Top Language",
                    value=top_language,
                    description=top_language_desc,
                    icon="code",
                    accent_color=theme["accent_pink"],
                    theme=theme,
                ),
            ),
            # Card 4: Top Framework
            ft.Container(
                col={"xs": 12, "sm": 6, "md": 4, "lg": 3},
                content=dashboard_analytics_card(
                    title="Top Framework",
                    value=top_framework,
                    description=top_framework_desc,
                    icon="dashboard_customize_outlined",
                    accent_color=theme["accent"],
                    theme=theme,
                ),
            ),
            # Card 5: Top SDLC Model
            ft.Container(
                col={"xs": 12, "sm": 6, "md": 4, "lg": 3},
                content=dashboard_analytics_card(
                    title="Top SDLC Model",
                    value=top_sdlc,
                    description=top_sdlc_desc,
                    icon="route_outlined",
                    accent_color=theme["accent_2"],
                    theme=theme,
                ),
            ),
            # Card 6: Total Feedback
            ft.Container(
                col={"xs": 12, "sm": 6, "md": 4, "lg": 3},
                content=dashboard_analytics_card(
                    title="Total Feedback",
                    value=total_feedback,
                    description=feedback_desc,
                    icon="feedback_outlined",
                    accent_color=theme["accent_pink"],
                    theme=theme,
                ),
            ),
            # Card 7: Average Rating
            ft.Container(
                col={"xs": 12, "sm": 6, "md": 4, "lg": 3},
                content=dashboard_analytics_card(
                    title="Average Rating",
                    value=avg_rating_display,
                    description=rating_desc,
                    icon="star_outline",
                    accent_color=theme["success"],
                    theme=theme,
                ),
            ),
        ],
    )

    # 3. RECENT RECOMMENDATIONS TABLE
    recent_table = dashboard_recent_recommendations_table(
        recommendations=recent,
        on_view_details=on_view_recommendation,
        on_generate=on_new_recommendation,
        theme=theme,
        on_open_history=on_open_history,
    )
    recent_block = ft.Container(
        margin=ft.margin.only(top=Spacing.md),
        content=recent_table,
    )

    # Open layout: no outer panel/card — cards sit on the workspace background;
    # scrolling is handled by AppLayout content area only.
    return ft.Column(
        spacing=24,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        controls=[hero, analytics_grid, recent_block],
    )
