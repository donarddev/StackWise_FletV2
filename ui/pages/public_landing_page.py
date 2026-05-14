"""Public landing page with hero, about, and auth-entry navigation."""

from __future__ import annotations

from typing import Callable

import flet as ft

from app.utils.constants import BRAND_NAME
from ui.components.background_layers import ambient_orb, shared_auth_backdrop, subtle_grid_layer
from ui.components.brand_logo import brand_icon
from ui.components.glass_card import gradient_card
from ui.components.landing_cards import landing_feature_card, section_badge, status_pill
from ui.components.primary_button import primary_button, secondary_button
from ui.themes.app_theme import Colors, Radii, Spacing, Typography

INTRO_CARD_HEIGHT = 186
PROBLEM_CARD_HEIGHT = 242
WORKFLOW_CARD_HEIGHT = 238
CORE_FEATURE_CARD_HEIGHT = 198
REPORT_CARD_HEIGHT = 166


def _create_grid_background() -> ft.Control:
    """Landing-only futuristic grid and glow backdrop."""
    grid_line_color = ft.colors.with_opacity(0.10, "#38bdf8")
    horizontal_lines = 20
    vertical_lines = 30

    return ft.Stack(
        expand=True,
        controls=[
            # Cleaner, flatter dark base to keep focus on hero content.
            ft.Container(
                expand=True,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_center,
                    end=ft.alignment.bottom_center,
                    colors=["#050913", "#070d19", "#060b15"],
                ),
            ),
            subtle_grid_layer(opacity=0.045),
            ft.Container(
                expand=True,
                opacity=0.7,
                content=ft.Stack(
                    expand=True,
                    controls=[
                        ft.Column(
                            expand=True,
                            spacing=0,
                            controls=[
                                ft.Container(
                                    expand=True,
                                    border=ft.border.only(top=ft.BorderSide(0.6, grid_line_color)),
                                )
                                for _ in range(horizontal_lines)
                            ],
                        ),
                        ft.Row(
                            expand=True,
                            spacing=0,
                            controls=[
                                ft.Container(
                                    expand=True,
                                    border=ft.border.only(left=ft.BorderSide(0.6, grid_line_color)),
                                )
                                for _ in range(vertical_lines)
                            ],
                        ),
                    ],
                ),
            ),
            # Very soft supporting glow accents.
            _soft_radial_glow(
                size=460,
                color_hex="#22d3ee",
                left=-260,
                top=-250,
                opacity=0.055,
            ),
            _soft_radial_glow(
                size=440,
                color_hex="#8b5cf6",
                right=-240,
                top=40,
                opacity=0.05,
            ),
            _soft_radial_glow(
                size=400,
                color_hex="#14b8a6",
                left=220,
                top=420,
                opacity=0.04,
            ),
        ],
    )


def _soft_radial_glow(
    *,
    size: int,
    color_hex: str,
    opacity: float,
    left: int | None = None,
    right: int | None = None,
    top: int | None = None,
    bottom: int | None = None,
) -> ft.Control:
    return ft.Container(
        width=size,
        height=size,
        left=left,
        right=right,
        top=top,
        bottom=bottom,
        border_radius=999,
        gradient=ft.RadialGradient(
            center=ft.alignment.center,
            radius=1.05,
            colors=[
                ft.colors.with_opacity(opacity, color_hex),
                ft.colors.with_opacity(opacity * 0.35, color_hex),
                "#02061700",
            ],
        ),
    )


def build_public_landing_page(
    *,
    on_login: Callable[[ft.ControlEvent], None],
    on_register: Callable[[ft.ControlEvent], None],
    on_create_account: Callable[[ft.ControlEvent], None],
    on_start_recommendation: Callable[[ft.ControlEvent], None],
) -> ft.Control:
    scroll_ref = ft.Ref[ft.Column]()

    def _scroll_to(section_key: str) -> None:
        col = scroll_ref.current
        if col is None:
            return
        try:
            col.scroll_to(key=section_key, duration=350)
            col.update()
        except Exception:
            pass

    header = _header(
        on_home=lambda _e: _scroll_to("home"),
        on_about=lambda _e: _scroll_to("about"),
        on_login=on_login,
        on_register=on_register,
    )
    hero = _hero(on_start_recommendation=on_start_recommendation, on_about=lambda _e: _scroll_to("about"))
    about = _about(on_login=on_login, on_create_account=on_create_account)

    return ft.Container(
        expand=True,
        bgcolor=Colors.background,
        content=ft.Stack(
            expand=True,
            controls=[
                _create_grid_background(),
                ambient_orb(
                    size=420,
                    color_hex=Colors.primary,
                    align_left=True,
                    align_top=True,
                    x_offset=-240,
                    y_offset=-260,
                    opacity=0.04,
                ),
                ambient_orb(
                    size=380,
                    color_hex="#2dd4bf",
                    align_left=False,
                    align_top=True,
                    x_offset=-250,
                    y_offset=-250,
                    opacity=0.035,
                ),
                ft.Column(
                    expand=True,
                    spacing=0,
                    controls=[
                        header,
                        ft.Container(
                            expand=True,
                            content=ft.Column(
                                ref=scroll_ref,
                                scroll=ft.ScrollMode.AUTO,
                                spacing=0,
                                controls=[hero, about],
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )


def _header(*, on_home, on_about, on_login, on_register) -> ft.Control:
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=28, vertical=14),
        bgcolor=ft.colors.TRANSPARENT,
        content=ft.Stack(
            height=56,
            controls=[
                ft.Container(
                    alignment=ft.alignment.center,
                    content=ft.Container(
                        padding=ft.padding.symmetric(horizontal=8, vertical=6),
                        border_radius=Radii.pill,
                        bgcolor=ft.colors.with_opacity(0.52, Colors.surface),
                        border=ft.border.all(1, ft.colors.with_opacity(0.65, Colors.border)),
                        shadow=ft.BoxShadow(
                            spread_radius=0,
                            blur_radius=14,
                            color=ft.colors.with_opacity(0.16, Colors.primary),
                            offset=ft.Offset(0, 2),
                        ),
                        content=ft.Row(
                            spacing=4,
                            tight=True,
                            controls=[
                                _center_nav_button("Home", on_home, active=True),
                                _center_nav_button("About", on_about),
                            ],
                        ),
                    ),
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            spacing=Spacing.md,
                            controls=[
                                brand_icon(size=34, radius=10),
                                ft.Column(
                                    spacing=1,
                                    tight=True,
                                    controls=[
                                        ft.Text(BRAND_NAME, style=Typography.subheading(size=15)),
                                        ft.Text(
                                            "Tech stack decision support system",
                                            style=Typography.caption(),
                                        ),
                                    ],
                                ),
                            ],
                        ),
                        ft.Row(
                            spacing=8,
                            controls=[
                                _header_action_button("Login", on_login),
                                ft.Container(
                                    border_radius=Radii.pill,
                                    gradient=ft.LinearGradient(
                                        begin=ft.alignment.top_left,
                                        end=ft.alignment.bottom_right,
                                        colors=["#2dd4bf", Colors.primary],
                                    ),
                                    content=ft.TextButton(
                                        "Register",
                                        on_click=on_register,
                                        style=ft.ButtonStyle(
                                            color=Colors.text_primary,
                                            shape=ft.RoundedRectangleBorder(radius=Radii.pill),
                                            padding=ft.padding.symmetric(horizontal=18, vertical=11),
                                        ),
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    )


def _hero(*, on_start_recommendation, on_about) -> ft.Control:
    left = ft.Column(
        spacing=Spacing.lg,
        controls=[
            ft.Container(
                key="home",
                padding=ft.padding.symmetric(horizontal=15, vertical=7),
                border_radius=Radii.pill,
                bgcolor=ft.colors.with_opacity(0.16, "#2dd4bf"),
                border=ft.border.all(1, ft.colors.with_opacity(0.28, "#2dd4bf")),
                content=ft.Text("Decision Support System", size=15, color=Colors.text_primary),
            ),
            ft.Text(
                spans=[
                    ft.TextSpan("Choose the right "),
                    ft.TextSpan(
                        "programming language",
                        style=ft.TextStyle(
                            color="#7dd3fc",
                            weight=ft.FontWeight.W_900,
                            letter_spacing=0.2,
                            shadow=ft.BoxShadow(
                                blur_radius=14,
                                spread_radius=0,
                                color=ft.colors.with_opacity(0.28, "#38bdf8"),
                                offset=ft.Offset(0, 0),
                            ),
                        ),
                    ),
                    ft.TextSpan(", "),
                    ft.TextSpan(
                        "framework",
                        style=ft.TextStyle(
                            color="#c4b5fd",
                            weight=ft.FontWeight.W_900,
                            letter_spacing=0.2,
                            shadow=ft.BoxShadow(
                                blur_radius=14,
                                spread_radius=0,
                                color=ft.colors.with_opacity(0.24, "#8b5cf6"),
                                offset=ft.Offset(0, 0),
                            ),
                        ),
                    ),
                    ft.TextSpan(", and "),
                    ft.TextSpan(
                        "SDLC model",
                        style=ft.TextStyle(
                            color="#5eead4",
                            weight=ft.FontWeight.W_900,
                            letter_spacing=0.2,
                            shadow=ft.BoxShadow(
                                blur_radius=14,
                                spread_radius=0,
                                color=ft.colors.with_opacity(0.24, "#14b8a6"),
                                offset=ft.Offset(0, 0),
                            ),
                        ),
                    ),
                    ft.TextSpan(" for your project."),
                ],
                style=Typography.display(size=58, weight=ft.FontWeight.W_800),
                color="#f8fafc",
            ),
            ft.Text(
                "StackWise AI analyzes project type, complexity, team size, preferred platform, "
                "development experience, timeline, and project goal to generate explainable and "
                "data-driven recommendations.",
                style=Typography.body(size=16),
            ),
            ft.Row(
                spacing=Spacing.md,
                controls=[
                    primary_button(
                        "Start Recommendation",
                        on_click=on_start_recommendation,
                        icon=ft.icons.ROCKET_LAUNCH_OUTLINED,
                        height=80,
                        width=250,
                    ),
                    secondary_button(
                        "Learn About StackWise",
                        on_click=on_about,
                        icon=ft.icons.ARROW_DOWNWARD_ROUNDED,
                        height=80,
                        width=250,
                    ),
                ],
            ),
            ft.Text(
                "Rule-based recommendation engine today, AI-assisted scoring with Ollama support.",
                style=Typography.caption(),
            ),
            ft.ResponsiveRow(
                spacing=Spacing.sm,
                run_spacing=Spacing.sm,
                controls=[
                    ft.Container(col={"xs": 6, "md": 4}, content=_chip("Explainable outputs")),
                    ft.Container(col={"xs": 6, "md": 4}, content=_chip("Built for beginners")),
                    ft.Container(col={"xs": 6, "md": 4}, content=_chip("Saved recommendation history")),
                    ft.Container(col={"xs": 6, "md": 4}, content=_chip("Confidence scoring")),
                    ft.Container(col={"xs": 6, "md": 4}, content=_chip("AI-assisted guidance")),
                ],
            ),
        ],
    )

    right = gradient_card(
        width=520,
        radius=Radii.xl,
        padding=ft.padding.symmetric(horizontal=22, vertical=20),
        content=ft.Column(
            spacing=Spacing.md,
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("INTELLIGENCE OVERVIEW", style=Typography.caption()),
                        ft.Container(expand=True),
                        status_pill("Live rules"),
                    ],
                ),
                ft.Text("Decision Intelligence Panel", style=Typography.heading(size=30)),
                ft.Text(
                    "See the compact signals StackWise AI weighs before preparing a recommendation report.",
                    style=Typography.body(size=14),
                ),
                ft.ResponsiveRow(
                    run_spacing=Spacing.md,
                    spacing=Spacing.md,
                    controls=[
                        ft.Container(col={"xs": 12, "md": 6}, content=_intel_card(
                            "Language Recommendation",
                            "Matches the project shape with a language that fits the team and timeline.",
                            "Active",
                        )),
                        ft.Container(col={"xs": 12, "md": 6}, content=_intel_card(
                            "Framework Matching",
                            "Connects the selected language to a practical framework choice.",
                            "Active",
                        )),
                        ft.Container(col={"xs": 12, "md": 6}, content=_intel_card(
                            "SDLC Model Selection",
                            "Chooses a delivery model that fits the project pace and complexity.",
                            "Active",
                        )),
                        ft.Container(col={"xs": 12, "md": 6}, content=_intel_card(
                            "Confidence Score",
                            "Communicates how strong the recommendation match is for the input.",
                            "Preview",
                        )),
                    ],
                ),
            ],
        ),
    )

    return ft.Container(
        padding=ft.padding.symmetric(horizontal=56, vertical=44),
        content=ft.ResponsiveRow(
            spacing=24,
            run_spacing=22,
            controls=[
                ft.Container(col={"xs": 12, "lg": 7}, content=left),
                ft.Container(col={"xs": 12, "lg": 5}, content=right),
            ],
        ),
    )


def _about(*, on_login, on_create_account) -> ft.Control:
    feature_cards = [
        (
            "Recommendation Engine",
            "Generates an explainable stack recommendation based on project requirements.",
            "Active",
        ),
        (
            "Dashboard Analytics",
            "Quick snapshot of activity and recent outputs for reporting and review.",
            "Active",
        ),
        (
            "Recommendation History",
            "Saved recommendation reports to revisit, compare, and cite later.",
            "Active",
        ),
        (
            "Learning Hub",
            "Learn the basics of languages, frameworks, and SDLC models in one place.",
            "Active",
        ),
        (
            "StackWise Chatbot",
            "Ask questions about stack choices, SDLC models, and next steps.",
            "Preview",
        ),
        (
            "Feedback Collection",
            "Capture user feedback to improve recommendation quality over time.",
            "Active",
        ),
    ]

    output_cards = [
        (
            "Recommended language",
            "A best-fit language based on the project context and student team constraints.",
        ),
        (
            "Recommended framework",
            "A practical framework choice aligned to the selected language and project shape.",
        ),
        (
            "Recommended SDLC model",
            "A delivery process that matches timeline, scope uncertainty, and complexity.",
        ),
        (
            "Confidence score",
            "A compact indicator of recommendation fit strength based on the inputs.",
        ),
        (
            "Explanation",
            "Clear reasoning and decision factors to defend in presentations.",
        ),
        (
            "Alternative stacks",
            "Other viable options when priorities or constraints change.",
        ),
        (
            "Risk analysis",
            "Known trade-offs, implementation risks, and planning considerations.",
        ),
        (
            "Skill gap analysis",
            "What the team may need to learn to deliver successfully.",
        ),
        (
            "Suggested roadmap",
            "A high-level next-steps plan to move from decision to execution.",
        ),
    ]

    return ft.Container(
        key="about",
        padding=ft.padding.symmetric(horizontal=56, vertical=52),
        content=ft.Column(
            spacing=Spacing.xxxl,
            controls=[
                _about_stackwise_section(),
                _problem_solution_section(),
                _how_stackwise_works_section(),
                _section_intro(
                    badge="Workspace",
                    title="Core Features",
                    subtitle="Everything you need to generate and defend a project technology stack decision.",
                ),
                _feature_grid(
                    cards=[(title, body, status) for title, body, status in feature_cards],
                    cols={"xs": 12, "md": 6, "lg": 4},
                    height=CORE_FEATURE_CARD_HEIGHT,
                ),
                _section_intro(
                    badge="Output",
                    title="What the recommendation report includes",
                    subtitle=(
                        "The generated report is structured to help students and beginner developers "
                        "explain the \"why\" behind each decision."
                    ),
                ),
                _feature_grid(
                    cards=[(title, body, None) for title, body in output_cards],
                    cols={"xs": 12, "md": 6, "lg": 4},
                    compact=True,
                    height=REPORT_CARD_HEIGHT,
                ),
                _cta_section(on_create_account=on_create_account, on_login=on_login),
            ],
        ),
    )


def create_section_label(text: str) -> ft.Control:
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=12, vertical=7),
        border_radius=Radii.pill,
        bgcolor=ft.colors.with_opacity(0.32, "#0b1324"),
        border=ft.border.all(1, ft.colors.with_opacity(0.25, "#6FE8FF")),
        content=ft.Text(text, style=Typography.caption(), color="#A8B3C7"),
    )


def create_gradient_heading(*, white_text: str, accent_text: str, accent_color: str = "#6FE8FF", size: int = 50) -> ft.Control:
    return ft.Text(
        spans=[
            ft.TextSpan(white_text, style=ft.TextStyle(color="#F5F7FF", weight=ft.FontWeight.W_800)),
            ft.TextSpan(
                accent_text,
                style=ft.TextStyle(
                    color=accent_color,
                    weight=ft.FontWeight.W_800,
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=10,
                        color=ft.colors.with_opacity(0.22, accent_color),
                        offset=ft.Offset(0, 0),
                    ),
                ),
            ),
        ],
        style=Typography.display(size=size, weight=ft.FontWeight.W_800),
    )


def create_value_item(*, title: str, body: str, icon: str, accent: str) -> ft.Control:
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=14, vertical=12),
        border_radius=Radii.lg,
        bgcolor=ft.colors.with_opacity(0.68, "#0a1220"),
        border=ft.border.all(1, ft.colors.with_opacity(0.28, accent)),
        content=ft.Column(
            spacing=Spacing.sm,
            controls=[
                ft.Container(
                    width=28,
                    height=28,
                    border_radius=8,
                    bgcolor=ft.colors.with_opacity(0.18, accent),
                    alignment=ft.alignment.center,
                    content=ft.Icon(icon, color=accent, size=16),
                ),
                ft.Text(title, style=Typography.subheading(size=16), color="#F5F7FF"),
                ft.Text(body, style=Typography.body(size=13, color="#94A3B8")),
            ],
        ),
    )


def _about_stackwise_section() -> ft.Control:
    return ft.Column(
        spacing=Spacing.lg,
        controls=[
            create_section_label("Student Decision Support Platform"),
            create_gradient_heading(white_text="About ", accent_text="StackWise AI", accent_color="#6FE8FF", size=52),
            ft.Container(
                width=980,
                content=ft.Text(
                    "StackWise AI helps students and beginner developers choose a suitable programming language, "
                    "framework, and SDLC model by analyzing project requirements and generating explainable recommendations.",
                    style=Typography.body(size=16, color="#A8B3C7"),
                ),
            ),
            ft.ResponsiveRow(
                spacing=Spacing.md,
                run_spacing=Spacing.md,
                controls=[
                    ft.Container(
                        col={"xs": 12, "md": 4},
                        content=create_value_item(
                            title="Explainable recommendations",
                            body="Clear reasoning you can defend in class presentations and project proposals.",
                            icon=ft.icons.INSIGHTS_ROUNDED,
                            accent="#6FE8FF",
                        ),
                    ),
                    ft.Container(
                        col={"xs": 12, "md": 4},
                        content=create_value_item(
                            title="Beginner-friendly guidance",
                            body="Simple prompts and structured outputs built for students and first-time teams.",
                            icon=ft.icons.SCHOOL_OUTLINED,
                            accent="#34E6B3",
                        ),
                    ),
                    ft.Container(
                        col={"xs": 12, "md": 4},
                        content=create_value_item(
                            title="Service-driven architecture",
                            body="Controllers stay thin with Request Validation and Services for business logic.",
                            icon=ft.icons.DEVICE_HUB_ROUNDED,
                            accent="#9F7CFF",
                        ),
                    ),
                ],
            ),
        ],
    )


def _section_intro(*, badge: str, title: str, subtitle: str) -> ft.Control:
    return ft.Column(
        spacing=Spacing.sm,
        controls=[
            section_badge(badge),
            ft.Text(title, style=Typography.display(size=52, weight=ft.FontWeight.W_800)),
            ft.Text(subtitle, style=Typography.body(size=16)),
        ],
    )


def _problem_solution_section() -> ft.Control:
    return ft.Column(
        spacing=Spacing.lg,
        controls=[
            ft.Column(
                spacing=Spacing.sm,
                controls=[
                    create_section_label("Context"),
                    create_gradient_heading(
                        white_text="Problem and ",
                        accent_text="Solution",
                        accent_color="#34E6B3",
                        size=46,
                    ),
                    ft.Text(
                        "Why StackWise AI exists and how it supports student projects.",
                        style=Typography.body(size=15.5, color="#A8B3C7"),
                    ),
                ],
            ),
            ft.ResponsiveRow(
                spacing=Spacing.md,
                run_spacing=Spacing.md,
                controls=[
                    ft.Container(
                        col={"xs": 12, "lg": 5},
                        content=create_comparison_panel(
                            title="The Problem",
                            subtitle="Challenge",
                            icon=ft.icons.ERROR_OUTLINE_ROUNDED,
                            accent="#F59E0B",
                            body=(
                                "Students and beginner developers often struggle to choose the right programming "
                                "language, framework, and development process for their software projects. This can "
                                "lead to mismatched technologies, unclear planning, and difficulty defending project decisions."
                            ),
                        ),
                    ),
                    ft.Container(
                        col={"xs": 12, "lg": 2},
                        alignment=ft.alignment.center,
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                create_connector_line(),
                                ft.Icon(ft.icons.ARROW_FORWARD_ROUNDED, color="#60A5FA", size=28),
                                create_connector_line(),
                            ],
                        ),
                    ),
                    ft.Container(
                        col={"xs": 12, "lg": 5},
                        content=create_comparison_panel(
                            title="The StackWise Solution",
                            subtitle="Approach",
                            icon=ft.icons.AUTO_AWESOME_ROUNDED,
                            accent="#34E6B3",
                            body=(
                                "StackWise AI guides users through project details such as project type, complexity, "
                                "team size, platform, experience level, timeline, and project goal, then generates a "
                                "structured recommendation report."
                            ),
                        ),
                    ),
                ],
            ),
        ],
    )


def create_comparison_panel(*, title: str, subtitle: str, body: str, icon: str, accent: str) -> ft.Control:
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=16, vertical=14),
        border_radius=Radii.xl,
        bgcolor=ft.colors.with_opacity(0.68, "#0d1626"),
        border=ft.border.all(1, ft.colors.with_opacity(0.30, accent)),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=14,
            color=ft.colors.with_opacity(0.18, accent),
            offset=ft.Offset(0, 0),
        ),
        content=ft.Column(
            spacing=Spacing.sm,
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(
                            width=30,
                            height=30,
                            border_radius=999,
                            bgcolor=ft.colors.with_opacity(0.18, accent),
                            alignment=ft.alignment.center,
                            content=ft.Icon(icon, size=16, color=accent),
                        ),
                        ft.Container(width=8),
                        ft.Column(
                            spacing=1,
                            tight=True,
                            controls=[
                                ft.Text(subtitle, size=12, color=accent),
                                ft.Text(title, style=Typography.subheading(size=19), color="#F5F7FF"),
                            ],
                        ),
                    ],
                ),
                ft.Text(body, style=Typography.body(size=13.8, color="#A8B3C7")),
            ],
        ),
    )


def create_connector_line() -> ft.Control:
    return ft.Container(
        width=54,
        height=2,
        border_radius=999,
        bgcolor=ft.colors.with_opacity(0.72, "#60A5FA"),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=8,
            color=ft.colors.with_opacity(0.25, "#60A5FA"),
            offset=ft.Offset(0, 0),
        ),
    )


def _how_stackwise_works_section() -> ft.Control:
    steps = [
        ("01", "Enter Project Details", "Provide context like project type, platform, timeline, team size, and experience level.", ft.icons.EDIT_NOTE_ROUNDED, "#60A5FA"),
        ("02", "Analyze Requirements", "StackWise AI interprets the inputs to identify the most important decision signals.", ft.icons.ANALYTICS_OUTLINED, "#6FE8FF"),
        ("03", "Generate Recommendations", "Receive language, framework, and SDLC recommendations with clear trade-off reasoning.", ft.icons.AUTO_AWESOME_ROUNDED, "#9F7CFF"),
        ("04", "Review Report and History", "Compare alternatives, track outputs, and refine future decisions with saved history.", ft.icons.FACT_CHECK_ROUNDED, "#34E6B3"),
    ]
    return ft.Column(
        spacing=Spacing.lg,
        controls=[
            ft.Column(
                spacing=Spacing.sm,
                controls=[
                    create_section_label("Workflow"),
                    create_gradient_heading(
                        white_text="How ",
                        accent_text="StackWise AI Works",
                        accent_color="#6FE8FF",
                        size=46,
                    ),
                    ft.Text(
                        "A connected process that transforms project inputs into a clear recommendation report.",
                        style=Typography.body(size=15.5, color="#A8B3C7"),
                    ),
                ],
            ),
            ft.ResponsiveRow(
                spacing=Spacing.md,
                run_spacing=Spacing.md,
                controls=[
                    ft.Container(
                        col={"xs": 12, "md": 6, "lg": 3},
                        content=create_process_node(
                            number=number,
                            title=title,
                            body=body,
                            icon=icon,
                            accent=accent,
                        ),
                    )
                    for number, title, body, icon, accent in steps
                ],
            ),
        ],
    )


def create_process_node(*, number: str, title: str, body: str, icon: str, accent: str) -> ft.Control:
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=14, vertical=14),
        border_radius=Radii.lg,
        bgcolor=ft.colors.with_opacity(0.66, "#0a1220"),
        border=ft.border.all(1, ft.colors.with_opacity(0.30, accent)),
        content=ft.Column(
            spacing=Spacing.sm,
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(
                            width=30,
                            height=30,
                            border_radius=999,
                            bgcolor=ft.colors.with_opacity(0.20, accent),
                            alignment=ft.alignment.center,
                            content=ft.Text(number, size=12, weight=ft.FontWeight.W_700, color="#F5F7FF"),
                        ),
                        ft.Container(width=8),
                        ft.Icon(icon, size=17, color=accent),
                        ft.Container(expand=True),
                        ft.Container(
                            width=44,
                            height=2,
                            border_radius=999,
                            bgcolor=ft.colors.with_opacity(0.62, accent),
                        ),
                    ]
                ),
                ft.Text(title, style=Typography.subheading(size=16), color="#F5F7FF"),
                ft.Text(body, style=Typography.body(size=12.8, color="#94A3B8")),
            ],
        ),
    )


def _feature_grid(*, cards, cols, compact: bool = False, workflow: bool = False, height: int | None = None) -> ft.Control:
    controls = []
    for title, body, status in cards:
        card = _feature_card(
            title,
            body,
            status=status,
            compact=compact,
            workflow=workflow,
            height=height,
        )
        controls.append(ft.Container(col=cols, content=card))
    return ft.ResponsiveRow(
        spacing=Spacing.md,
        run_spacing=Spacing.md,
        controls=controls,
    )


def _feature_card(
    title: str,
    body: str,
    *,
    status: str | None = None,
    compact: bool = False,
    workflow: bool = False,
    height: int | None = None,
) -> ft.Control:
    return landing_feature_card(
        title=title,
        body=body,
        status=status,
        compact=compact,
        workflow=workflow,
        height=height,
    )


def _cta_section(*, on_create_account, on_login) -> ft.Control:
    return gradient_card(
        radius=Radii.xl,
        padding=ft.padding.symmetric(horizontal=26, vertical=24),
        content=ft.Row(
            spacing=Spacing.lg,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        spacing=Spacing.sm,
                        controls=[
                            section_badge("Next step"),
                            ft.Text(
                                "Ready to build your project recommendation?",
                                style=Typography.heading(size=42, weight=ft.FontWeight.W_800),
                            ),
                            ft.Text(
                                "Start by entering your project details and let StackWise AI prepare a clear decision report.",
                                style=Typography.body(size=15),
                            ),
                        ],
                    ),
                ),
                ft.Row(
                    spacing=Spacing.md,
                    controls=[
                        primary_button("Create Account", on_click=on_create_account),
                        secondary_button("Login", on_click=on_login),
                    ],
                ),
            ],
        ),
    )


def _center_nav_button(label: str, on_click, *, active: bool = False) -> ft.Control:
    return ft.TextButton(
        label,
        on_click=on_click,
        style=ft.ButtonStyle(
            color=Colors.text_primary if active else ft.colors.with_opacity(0.92, Colors.text_secondary),
            bgcolor=(
                ft.colors.with_opacity(0.35, Colors.surface_2)
                if active else ft.colors.with_opacity(0.0, Colors.surface)
            ),
            overlay_color={
                ft.ControlState.HOVERED: ft.colors.with_opacity(0.15, Colors.primary),
                ft.ControlState.DEFAULT: ft.colors.TRANSPARENT,
            },
            shape=ft.RoundedRectangleBorder(radius=Radii.pill),
            padding=ft.padding.symmetric(horizontal=18, vertical=10),
        ),
    )


def _header_action_button(label: str, on_click) -> ft.Control:
    return ft.TextButton(
        label,
        on_click=on_click,
        style=ft.ButtonStyle(
            color=ft.colors.with_opacity(0.95, Colors.text_secondary),
            overlay_color={
                ft.ControlState.HOVERED: ft.colors.with_opacity(0.12, Colors.primary),
                ft.ControlState.DEFAULT: ft.colors.TRANSPARENT,
            },
            shape=ft.RoundedRectangleBorder(radius=Radii.pill),
            padding=ft.padding.symmetric(horizontal=14, vertical=10),
        ),
    )


def _chip(text: str) -> ft.Control:
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=11, vertical=7),
        border_radius=Radii.pill,
        bgcolor=ft.colors.with_opacity(0.44, Colors.surface),
        border=ft.border.all(1, ft.colors.with_opacity(0.7, Colors.border)),
        content=ft.Text(text, size=12.5, color=Colors.text_secondary),
    )


def _intel_card(title: str, body: str, status: str) -> ft.Control:
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=14, vertical=14),
        border_radius=Radii.lg,
        bgcolor=ft.colors.with_opacity(0.5, Colors.surface),
        border=ft.border.all(1, ft.colors.with_opacity(0.75, Colors.border)),
        content=ft.Column(
            spacing=Spacing.sm,
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(
                            width=11,
                            height=11,
                            border_radius=999,
                            bgcolor="#34d399",
                            shadow=ft.BoxShadow(
                                spread_radius=0,
                                blur_radius=12,
                                color="#34d39966",
                                offset=ft.Offset(0, 0),
                            ),
                        ),
                        ft.Container(expand=True),
                        status_pill(status),
                    ],
                ),
                ft.Text(title, style=Typography.subheading(size=18)),
                ft.Text(body, style=Typography.body(size=13.2)),
            ],
        ),
    )


