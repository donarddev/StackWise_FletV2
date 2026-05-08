"""Recommendation page — input form + result panel side-by-side."""

from __future__ import annotations

from typing import Callable, Optional

import flet as ft

from app.models.recommendation import Recommendation
from app.utils.constants import (
    COMPLEXITY_LEVELS,
    EXPERIENCE_LEVELS,
    PLATFORMS,
    PROJECT_GOALS,
    PROJECT_TYPES,
    SCALABILITY_LEVELS,
    SECURITY_LEVELS,
    TEAM_SIZES,
    TIMELINES,
)
from ui.components.empty_state import empty_state
from ui.components.glass_card import glass_card
from ui.components.input_field import input_field
from ui.components.page_header import page_header
from ui.components.primary_button import primary_button, secondary_button
from ui.components.section_header import section_header
from ui.components.select_field import select_field
from ui.themes.app_theme import Colors, Radii, Spacing, Typography
from ui.widgets.recommendation_card import recommendation_result_card


class RecommendationFormFields:
    def __init__(self) -> None:
        self.project_name = input_field(
            "Project name", hint="e.g. Aurora — content marketplace",
            icon=ft.icons.STAR_OUTLINE,
        )
        self.project_type = select_field("Project type", PROJECT_TYPES)
        self.project_goal = select_field("Project goal", PROJECT_GOALS)
        self.complexity = select_field("Complexity", COMPLEXITY_LEVELS)
        self.team_size = select_field("Team size", TEAM_SIZES)
        self.timeline = select_field("Timeline", TIMELINES)
        self.scalability = select_field("Scalability requirement", SCALABILITY_LEVELS)
        self.security = select_field("Security requirement", SECURITY_LEVELS)
        self.platform = select_field("Preferred platform", PLATFORMS)
        self.experience = select_field("Development experience", EXPERIENCE_LEVELS)

    def values(self) -> dict[str, str]:
        return {
            "project_name": self.project_name.value or "",
            "project_type": self.project_type.value or "",
            "project_goal": self.project_goal.value or "",
            "complexity": self.complexity.value or "",
            "team_size": self.team_size.value or "",
            "timeline": self.timeline.value or "",
            "scalability": self.scalability.value or "",
            "security": self.security.value or "",
            "platform": self.platform.value or "",
            "experience": self.experience.value or "",
        }


def build_recommendation_page(
    *,
    fields: RecommendationFormFields,
    error_text_ref: ft.Ref[ft.Text],
    submitting_ref: ft.Ref[ft.ProgressRing],
    result_panel_ref: ft.Ref[ft.Column],
    on_generate: Callable[[ft.ControlEvent], None],
    on_reset: Callable[[ft.ControlEvent], None],
    initial_recommendation: Optional[Recommendation] = None,
) -> ft.Control:
    error_text = ft.Text(
        "", size=12.5, color=Colors.danger, ref=error_text_ref, visible=False,
    )
    submitting = ft.ProgressRing(
        width=18, height=18, stroke_width=2, color=Colors.primary_glow,
        visible=False, ref=submitting_ref,
    )

    submit_row = ft.Row(
        spacing=Spacing.md, vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            primary_button(
                "Generate recommendation",
                on_click=on_generate,
                icon=ft.icons.AUTO_AWESOME,
            ),
            secondary_button("Reset", on_click=on_reset, icon=ft.icons.REFRESH),
            submitting,
        ],
    )

    form_card = glass_card(
        ft.Column(
            spacing=Spacing.md,
            controls=[
                section_header(
                    "Project profile",
                    subtitle="The more accurate this is, the more confident the recommendation.",
                ),
                fields.project_name,
                ft.ResponsiveRow(
                    spacing=Spacing.md, run_spacing=Spacing.md,
                    controls=[
                        ft.Container(col={"xs": 12, "md": 6}, content=fields.project_type),
                        ft.Container(col={"xs": 12, "md": 6}, content=fields.project_goal),
                        ft.Container(col={"xs": 12, "md": 6}, content=fields.complexity),
                        ft.Container(col={"xs": 12, "md": 6}, content=fields.team_size),
                        ft.Container(col={"xs": 12, "md": 6}, content=fields.timeline),
                        ft.Container(col={"xs": 12, "md": 6}, content=fields.scalability),
                        ft.Container(col={"xs": 12, "md": 6}, content=fields.security),
                        ft.Container(col={"xs": 12, "md": 6}, content=fields.platform),
                        ft.Container(col={"xs": 12, "md": 6}, content=fields.experience),
                    ],
                ),
                error_text,
                ft.Container(height=Spacing.sm),
                submit_row,
            ],
        )
    )

    initial_panel = (
        recommendation_result_card(initial_recommendation)
        if initial_recommendation
        else empty_state(
            icon=ft.icons.SCIENCE_OUTLINED,
            title="Awaiting your project profile",
            description=(
                "Fill out the form on the left. StackWise will analyze it across nine dimensions "
                "and return an explainable recommendation in under a second."
            ),
        )
    )

    result_column = ft.Column(
        controls=[initial_panel],
        spacing=Spacing.lg,
        ref=result_panel_ref,
    )

    explainer_card = _explainer_card()

    page_body = ft.ResponsiveRow(
        spacing=Spacing.lg, run_spacing=Spacing.lg,
        controls=[
            ft.Container(col={"xs": 12, "lg": 7}, content=form_card),
            ft.Container(
                col={"xs": 12, "lg": 5},
                content=ft.Column(
                    spacing=Spacing.md,
                    controls=[result_column, explainer_card],
                ),
            ),
        ],
    )

    return ft.Column(
        spacing=Spacing.xl,
        controls=[
            page_header(
                eyebrow="RECOMMENDATION GENERATOR",
                title="Choose the right stack — explainably.",
                subtitle="Project profile in. Language, framework, SDLC + reasoning out.",
            ),
            page_body,
        ],
    )


def _explainer_card() -> ft.Control:
    items = [
        ("Hybrid engine",
         "Deterministic scoring across nine weighted dimensions, optionally enriched by Ollama."),
        ("Confidence score",
         "Computed from the margin between top and runner-up candidates."),
        ("Trade-offs included",
         "Each recommendation lists what to watch out for as the project evolves."),
    ]
    rows = []
    for title, body in items:
        rows.append(
            ft.Row(
                spacing=Spacing.md, vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(
                        width=24, height=24, border_radius=8,
                        bgcolor=ft.colors.with_opacity(0.14, Colors.primary),
                        alignment=ft.alignment.center,
                        content=ft.Icon(ft.icons.CHECK, size=14, color=Colors.primary_glow),
                    ),
                    ft.Column(
                        spacing=2, tight=True,
                        controls=[
                            ft.Text(title, size=13, weight=ft.FontWeight.W_700,
                                    color=Colors.text_primary),
                            ft.Text(body, style=Typography.body(size=12.5)),
                        ],
                        expand=True,
                    ),
                ],
            )
        )
    return glass_card(
        ft.Column(
            spacing=Spacing.md,
            controls=[
                ft.Text("How StackWise thinks", style=Typography.subheading(size=15)),
                *rows,
            ],
        )
    )
