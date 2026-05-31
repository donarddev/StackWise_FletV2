"""Dedicated decision report page for a single saved recommendation."""

from __future__ import annotations

from typing import Any, Callable, Mapping, Optional

import flet as ft

from app.models.recommendation import Recommendation
from app.models.recommendation_feedback import RecommendationFeedback
from ui.components.empty_state import empty_state
from ui.components.primary_button import primary_button
from ui.components.recommendation_decision_report import (
    build_decision_report_body,
    report_data_from_recommendation,
)
from ui.pages.recommendation_page import recommendation_workspace_theme
from ui.themes.app_theme import Radii, Spacing

_PAGE_PAD = 40


def build_recommendation_result_page(
    *,
    rec: Optional[Recommendation],
    theme: Mapping[str, Any],
    page: Optional[ft.Page] = None,
    viewer_user_id: Optional[int] = None,
    on_back_recommendation: Callable[[ft.ControlEvent], None],
    on_back_history: Callable[[ft.ControlEvent], None],
    on_regenerate: Optional[Callable[[ft.ControlEvent], None]] = None,
    on_copy_summary: Optional[Callable[[ft.ControlEvent], None]] = None,
    on_dashboard: Optional[Callable[[ft.ControlEvent], None]] = None,
    on_feedback: Optional[Callable[[ft.ControlEvent], None]] = None,
    on_submit_feedback: Optional[Callable[[ft.ControlEvent], None]] = None,
    existing_feedback: Optional[RecommendationFeedback] = None,
    feedback_section_ref: Optional[ft.Ref[ft.Container]] = None,
    feedback_rating_ref: Optional[ft.Ref[ft.RadioGroup]] = None,
    feedback_comment_ref: Optional[ft.Ref[ft.TextField]] = None,
    feedback_error_ref: Optional[ft.Ref[ft.Text]] = None,
    feedback_success_ref: Optional[ft.Ref[ft.Text]] = None,
    feedback_submit_btn_ref: Optional[ft.Ref[ft.Container]] = None,
    not_found: bool = False,
) -> ft.Control:
    rw = recommendation_workspace_theme(theme)

    if not_found or rec is None:
        return ft.Container(
            padding=ft.padding.all(_PAGE_PAD),
            content=empty_state(
                icon=ft.icons.SEARCH_OFF_OUTLINED,
                title="Recommendation not found",
                description=(
                    "This report may have been deleted or you may not have access to it. "
                    "Return to History or create a new recommendation."
                ),
                action=ft.Row(
                    wrap=True,
                    spacing=Spacing.sm,
                    controls=[
                        primary_button(
                            "Back to History",
                            on_click=on_back_history,
                            icon=ft.icons.HISTORY,
                            theme=rw,
                            border_radius=Radii.pill,
                        ),
                        primary_button(
                            "Back to Recommendation",
                            on_click=on_back_recommendation,
                            icon=ft.icons.AUTO_AWESOME,
                            theme=rw,
                            mint_fill=True,
                            border_radius=Radii.pill,
                        ),
                    ],
                ),
                theme=rw,
            ),
        )

    assert rec is not None
    created_short = rec.created_at.strftime("%b %d, %Y") if rec.created_at else "—"
    data = report_data_from_recommendation(rec, created_short=created_short)

    return build_decision_report_body(
        data,
        theme=rw,
        page=page,
        input_data=rec.project_profile,
        user_id=viewer_user_id,
        route_params={"id": rec.id},
        on_back_recommendation=on_back_recommendation,
        on_back_history=on_back_history,
        on_copy_summary=on_copy_summary,
        on_regenerate=on_regenerate,
        on_dashboard=on_dashboard,
        on_feedback=on_feedback,
        on_submit_feedback=on_submit_feedback,
        existing_feedback=existing_feedback,
        feedback_section_ref=feedback_section_ref,
        feedback_rating_ref=feedback_rating_ref,
        feedback_comment_ref=feedback_comment_ref,
        feedback_error_ref=feedback_error_ref,
        feedback_success_ref=feedback_success_ref,
        feedback_submit_btn_ref=feedback_submit_btn_ref,
        show_feedback=True,
    )
