"""Recommendation page — input form + result panel side-by-side."""

from __future__ import annotations

from typing import Any, Callable, Mapping

import flet as ft

from app.requests.recommendation_request import (
    BUDGET_CONSTRAINTS_LEVELS,
    COMPLEXITY_LEVELS,
    DEPLOYMENT_PREFERENCES,
    DEVELOPMENT_EXPERIENCE_LEVELS,
    FEATURE_OPTIONS,
    MAINTENANCE_EXPECTATIONS_LEVELS,
    PERFORMANCE_REQUIREMENTS_LEVELS,
    PREFERRED_PLATFORMS,
    PROJECT_TYPES,
    REQUIREMENTS_STABILITY_LEVELS,
    SCALABILITY_NEEDS_LEVELS,
    SECURITY_REQUIREMENTS_LEVELS,
    STAKEHOLDER_INVOLVEMENT_LEVELS,
    TIMELINES,
)
from ui.components.dashboard.glass_tokens import dashboard_glass_tokens
from ui.components.glass_card import glass_card
from ui.components.input_field import input_field
from ui.components.page_header import page_header
from ui.components.primary_button import primary_button, secondary_button
from ui.components.section_header import section_header
from ui.components.select_field import select_field
from ui.themes.app_theme import Radii, Spacing
from ui.theme import caption_style, heading_style, subheading_style, text_style
def recommendation_workspace_theme(theme: Mapping[str, Any]) -> dict[str, Any]:
    """Dark-workspace tokens aligned with dashboard glass (navy cards, cyan accents).

    Used only for the Recommendation screen so inputs/cards match the dashboard
    without changing global workspace tokens for other routes.
    """
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
        }
    )
    return t


class RecommendationFormFields:
    def __init__(self, theme: Mapping[str, Any]) -> None:
        t = theme
        self.project_name = input_field(
            "Project Name *", hint="Example: Online Enrollment System",
            icon=ft.icons.STAR_OUTLINE, theme=t,
        )
        self.project_type = select_field("Project Type *", PROJECT_TYPES, theme=t)
        self.project_goal = input_field(
            "Project Goal *",
            hint="Describe the main purpose, features, and expected outcome of your project...",
            multiline=True,
            min_lines=3,
            max_lines=5,
            theme=t,
        )
        self.team_size = input_field("Team Size *", hint="Example: 3", icon=ft.icons.GROUPS_2_OUTLINED, theme=t)
        self.complexity = select_field("Complexity *", COMPLEXITY_LEVELS, theme=t)
        self.timeline = select_field("Timeline *", TIMELINES, theme=t)
        self.requirements_stability = select_field("Requirements Stability *", REQUIREMENTS_STABILITY_LEVELS, theme=t)
        self.stakeholder_involvement = select_field("Stakeholder Involvement *", STAKEHOLDER_INVOLVEMENT_LEVELS, theme=t)
        self.preferred_platform = select_field("Preferred Platform *", PREFERRED_PLATFORMS, theme=t)
        self.development_experience = select_field("Development Experience *", DEVELOPMENT_EXPERIENCE_LEVELS, theme=t)
        self.scalability_needs = select_field("Scalability Needs *", SCALABILITY_NEEDS_LEVELS, theme=t)
        self.performance_requirements = select_field("Performance Requirements *", PERFORMANCE_REQUIREMENTS_LEVELS, theme=t)
        self.security_requirements = select_field("Security Requirements *", SECURITY_REQUIREMENTS_LEVELS, theme=t)
        self.budget_constraints = select_field("Budget Constraints *", BUDGET_CONSTRAINTS_LEVELS, theme=t)
        self.maintenance_expectations = select_field("Maintenance Expectations *", MAINTENANCE_EXPECTATIONS_LEVELS, theme=t)
        self.deployment_preference = select_field("Deployment Preference *", DEPLOYMENT_PREFERENCES, theme=t)
        self.feature_checks = {
            feature: ft.Checkbox(
                label=feature,
                value=False,
                check_color=t["on_gradient"],
                active_color=t["accent_2"],
                label_style=ft.TextStyle(size=12.5, color=t["text_secondary"]),
            )
            for feature in FEATURE_OPTIONS
        }

    def selected_features(self) -> list[str]:
        return [name for name, cb in self.feature_checks.items() if cb.value]

    def values(self) -> dict[str, str]:
        return {
            "project_name": self.project_name.value or "",
            "project_type": self.project_type.value or "",
            "selected_features": "|".join(self.selected_features()),
            "project_goal": self.project_goal.value or "",
            "team_size": self.team_size.value or "",
            "complexity": self.complexity.value or "",
            "timeline": self.timeline.value or "",
            "requirements_stability": self.requirements_stability.value or "",
            "stakeholder_involvement": self.stakeholder_involvement.value or "",
            "preferred_platform": self.preferred_platform.value or "",
            "development_experience": self.development_experience.value or "",
            "scalability_needs": self.scalability_needs.value or "",
            "performance_requirements": self.performance_requirements.value or "",
            "security_requirements": self.security_requirements.value or "",
            "budget_constraints": self.budget_constraints.value or "",
            "maintenance_expectations": self.maintenance_expectations.value or "",
            "deployment_preference": self.deployment_preference.value or "",
        }


def build_recommendation_page(
    *,
    fields: RecommendationFormFields,
    error_text_ref: ft.Ref[ft.Text],
    submitting_ref: ft.Ref[ft.ProgressRing],
    on_generate: Callable[[ft.ControlEvent], None],
    on_reset: Callable[[ft.ControlEvent], None],
    on_back: Callable[[ft.ControlEvent], None],
    theme: Mapping[str, Any],
) -> ft.Control:
    error_text = ft.Text(
        "", size=12.5, color=theme["danger"], ref=error_text_ref, visible=False,
    )
    submitting = ft.ProgressRing(
        width=18, height=18, stroke_width=2, color=theme["accent_2"],
        visible=False, ref=submitting_ref,
    )

    g = dashboard_glass_tokens(theme)
    outline_bd = ft.colors.with_opacity(0.72, g["card_border"])
    hover_bd = g["teal"]
    outline_bg = ft.colors.with_opacity(0.28, theme["surface_2"])

    submit_row = ft.Row(
        spacing=Spacing.md, vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            primary_button(
                "Generate Recommendation",
                on_click=on_generate,
                icon=ft.icons.AUTO_AWESOME,
                theme=theme,
                mint_fill=True,
                border_radius=Radii.pill,
            ),
            secondary_button(
                "Reset",
                on_click=on_reset,
                icon=ft.icons.REFRESH,
                theme=theme,
                height=44,
                border_radius=Radii.pill,
                bgcolor=outline_bg,
                border_color=outline_bd,
                hover_border_color=hover_bd,
            ),
            secondary_button(
                "Back to Dashboard",
                on_click=on_back,
                icon=ft.icons.HOME_OUTLINED,
                theme=theme,
                height=44,
                border_radius=Radii.pill,
                bgcolor=outline_bg,
                border_color=outline_bd,
                hover_border_color=hover_bd,
            ),
            submitting,
        ],
        wrap=True,
    )

    profile_card = _section_card(
        theme,
        "Step 01",
        "Project Profile",
        "Describe what you are building and what outcome you want the project to achieve.",
        ft.Column(
            spacing=Spacing.md,
            controls=[
                fields.project_name,
                ft.Text("Use a clear title so the recommendation report stays easy to read.", style=caption_style(theme)),
                fields.project_type,
                ft.Text("Selected Features *", style=heading_style(theme, size=13, weight=ft.FontWeight.W_600)),
                ft.Container(
                    height=116,
                    padding=ft.padding.symmetric(horizontal=10, vertical=6),
                    border=ft.border.all(1, theme["border_strong"]),
                    border_radius=Radii.md,
                    bgcolor=theme["surface"],
                    content=ft.Column(
                        spacing=2,
                        scroll=ft.ScrollMode.AUTO,
                        controls=list(fields.feature_checks.values()),
                    ),
                ),
                ft.Text(
                    "Pick the most important features so the engine can score realistically.",
                    style=caption_style(theme),
                ),
                fields.project_goal,
                ft.Text(
                    "Mention intended users, major features, and the expected end result.",
                    style=caption_style(theme),
                ),
            ],
        ),
    )

    context_card = _section_card(
        theme,
        "Step 02",
        "Development Context",
        "Share your team size, complexity, and delivery timeline.",
        ft.ResponsiveRow(
            spacing=Spacing.md,
            run_spacing=Spacing.md,
            controls=[
                ft.Container(col={"xs": 12, "md": 4}, content=fields.team_size),
                ft.Container(col={"xs": 12, "md": 4}, content=fields.complexity),
                ft.Container(col={"xs": 12, "md": 4}, content=fields.timeline),
                ft.Container(col={"xs": 12, "md": 6}, content=fields.requirements_stability),
                ft.Container(col={"xs": 12, "md": 6}, content=fields.stakeholder_involvement),
            ],
        ),
    )

    preference_card = _section_card(
        theme,
        "Step 03",
        "Technical Preference",
        "Tell StackWise AI about platform and current development experience.",
        ft.ResponsiveRow(
            spacing=Spacing.md,
            run_spacing=Spacing.md,
            controls=[
                ft.Container(col={"xs": 12, "md": 6}, content=fields.preferred_platform),
                ft.Container(col={"xs": 12, "md": 6}, content=fields.development_experience),
                ft.Container(col={"xs": 12, "md": 6}, content=fields.scalability_needs),
                ft.Container(col={"xs": 12, "md": 6}, content=fields.performance_requirements),
                ft.Container(col={"xs": 12, "md": 6}, content=fields.security_requirements),
                ft.Container(col={"xs": 12, "md": 6}, content=fields.budget_constraints),
                ft.Container(col={"xs": 12, "md": 6}, content=fields.maintenance_expectations),
                ft.Container(col={"xs": 12, "md": 6}, content=fields.deployment_preference),
            ],
        ),
    )

    generate_card = _section_card(
        theme,
        "Step 04",
        "Generate Decision Report",
        "Your submission will produce an explainable report ready for review or presentation.",
        ft.Column(
            spacing=Spacing.md,
            controls=[
                ft.ResponsiveRow(
                    controls=[
                        ft.Container(
                            col={"xs": 12, "md": 7},
                            content=glass_card(
                                ft.Column(
                                    spacing=6,
                                    controls=[
                                        ft.Text("What the report includes", style=subheading_style(theme, size=18)),
                                        ft.Text(
                                            "Language recommendation, framework matching, SDLC model selection, "
                                            "confidence score, alternatives, risk analysis, skill gaps, and roadmap.",
                                            style=text_style(theme, size=13),
                                        ),
                                    ],
                                ),
                                theme=theme,
                            ),
                        ),
                        ft.Container(
                            col={"xs": 12, "md": 5},
                            content=ft.Container(
                                padding=ft.padding.symmetric(horizontal=14, vertical=12),
                                border_radius=Radii.lg,
                                bgcolor=ft.colors.with_opacity(0.10, theme["accent_2"]),
                                border=ft.border.all(1, ft.colors.with_opacity(0.38, theme["accent_2"])),
                                content=ft.Text(
                                    "This final report is readable in class, shareable with teammates, and easy to revisit.",
                                    style=text_style(theme, size=12.5),
                                ),
                            ),
                        ),
                    ]
                ),
                ft.ResponsiveRow(
                    spacing=Spacing.sm,
                    run_spacing=Spacing.sm,
                    controls=[
                        ft.Container(col={"xs": 12, "md": 4}, content=_mini_highlight(theme, "Explainable Results")),
                        ft.Container(col={"xs": 12, "md": 4}, content=_mini_highlight(theme, "Saved Recommendation")),
                        ft.Container(col={"xs": 12, "md": 4}, content=_mini_highlight(theme, "Roadmap Included")),
                    ],
                ),
                error_text,
                submit_row,
            ],
        ),
    )

    form_card = ft.Column(
        spacing=Spacing.lg,
        controls=[profile_card, context_card, preference_card, generate_card],
    )

    explainer_card = _guidance_card(theme)
    submit_note = _submit_note_card(theme)
    awaiting_card = _awaiting_profile_card(theme)

    page_body = ft.ResponsiveRow(
        spacing=Spacing.lg, run_spacing=Spacing.lg,
        controls=[
            ft.Container(col={"xs": 12, "lg": 8}, content=form_card),
            ft.Container(
                col={"xs": 12, "lg": 4},
                content=ft.Column(
                    spacing=Spacing.md,
                    controls=[explainer_card, submit_note, awaiting_card],
                ),
            ),
        ],
    )

    return ft.Column(
        spacing=Spacing.xl,
        controls=[
            page_header(
                eyebrow="Project Assessment",
                title="Tell StackWise AI about your project",
                subtitle=(
                    "Provide your project details so the system can recommend a suitable "
                    "programming language, framework, and SDLC model."
                ),
                theme=theme,
            ),
            page_body,
        ],
    )


def _guidance_card(theme: Mapping[str, Any]) -> ft.Control:
    items = [
        ("Project type", "Helps identify whether the project is web, mobile, desktop, API, or AI-focused."),
        ("Complexity", "Signals how much structure and risk management the report should recommend."),
        ("Team size", "Affects pace, division of work, and practical delivery recommendations."),
        ("Preferred platform", "Aligns the stack with the environment you actually want to build for."),
        ("Development experience", "Keeps recommendations beginner-friendly or more advanced as needed."),
        ("Timeline", "Helps decide between iterative and more sequential delivery approaches."),
        ("Project goal keywords", "Description text helps detect intent, features, and expected outcomes."),
        ("Scalability + security", "Non-functional requirements strongly influence technology fit and SDLC."),
    ]
    rows = []
    for title, body in items:
        rows.append(
            ft.Row(
                spacing=Spacing.md, vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(
                        width=24, height=24, border_radius=999,
                        bgcolor=ft.colors.with_opacity(0.12, theme["accent_2"]),
                        alignment=ft.alignment.center,
                        content=ft.Icon(ft.icons.CIRCLE, size=8, color=theme["accent_2"]),
                    ),
                    ft.Column(
                        spacing=2, tight=True,
                        controls=[
                            ft.Text(title, size=13, weight=ft.FontWeight.W_700, color=theme["text"]),
                            ft.Text(body, style=text_style(theme, size=12.5)),
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
                ft.Text("How StackWise thinks", style=subheading_style(theme, size=15)),
                *rows,
            ],
        ),
        theme=theme,
    )


def _awaiting_profile_card(theme: Mapping[str, Any]) -> ft.Control:
    return glass_card(
        ft.Column(
            spacing=Spacing.sm,
            controls=[
                ft.Icon(ft.icons.SCIENCE_OUTLINED, size=28, color=theme["accent_2"]),
                ft.Text("Awaiting your project profile", style=subheading_style(theme, size=15)),
                ft.Text(
                    "Fill out the form on the left. After you generate, StackWise opens your "
                    "full decision report on a dedicated page — not squeezed into this sidebar.",
                    style=text_style(theme, size=12.5),
                ),
            ],
        ),
        theme=theme,
    )


def _submit_note_card(theme: Mapping[str, Any]) -> ft.Control:
    return glass_card(
        ft.Column(
            spacing=Spacing.sm,
            controls=[
                ft.Text("Before you submit", style=subheading_style(theme, size=15)),
                ft.Text(
                    "StackWise AI will store the recommendation and open your full decision report on a dedicated page.",
                    style=text_style(theme, size=12.5),
                ),
            ],
        ),
        theme=theme,
    )


def _section_card(theme: Mapping[str, Any], step: str, title: str, subtitle: str, body: ft.Control) -> ft.Control:
    return glass_card(
        ft.Column(
            spacing=Spacing.md,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=10, vertical=5),
                            border_radius=Radii.pill,
                            bgcolor=ft.colors.with_opacity(0.12, theme["accent_2"]),
                            border=ft.border.all(1, ft.colors.with_opacity(0.35, theme["accent_2"])),
                            content=ft.Text(step, size=11.5, weight=ft.FontWeight.W_700, color=theme["accent_2"]),
                        ),
                    ],
                ),
                section_header(title, subtitle=subtitle, theme=theme),
                body,
            ],
        ),
        theme=theme,
    )


def _mini_highlight(theme: Mapping[str, Any], title: str) -> ft.Control:
    g = dashboard_glass_tokens(theme)
    header_bg = g.get("header_bg", theme["surface_3"])
    header_bd = g.get("header_border", theme["border_strong"])
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=12, vertical=10),
        border_radius=Radii.md,
        bgcolor=header_bg,
        border=ft.border.all(1, header_bd),
        content=ft.Column(
            spacing=4,
            controls=[
                ft.Text(title, style=subheading_style(theme, size=13)),
                ft.Text(
                    "Included in the final explainable recommendation package.",
                    style=caption_style(theme),
                ),
            ],
        ),
    )
