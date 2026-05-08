"""AuthLayout — split-screen shell for login/register."""

from __future__ import annotations

import flet as ft

from ui.components.brand_logo import brand_logo
from ui.components.background_layers import ambient_orb, shared_auth_backdrop, subtle_grid_layer
from ui.components.auth_card import auth_card
from ui.components.feature_item import feature_item
from ui.components.glass_card import gradient_card
from ui.themes.app_theme import Colors, Radii, Spacing, Typography


def auth_layout(form: ft.Control) -> ft.Control:
    hero = _hero_panel()
    panel = auth_card(form, width=460)

    return ft.Container(
        expand=True,
        bgcolor=Colors.background,
        content=ft.Stack(
            expand=True,
            controls=[
                shared_auth_backdrop(),
                subtle_grid_layer(opacity=0.04),
                ambient_orb(
                    size=560,
                    color_hex=Colors.primary,
                    align_left=True,
                    align_top=True,
                    x_offset=-200,
                    y_offset=-200,
                    opacity=0.17,
                ),
                ambient_orb(
                    size=460,
                    color_hex=Colors.accent_cyan,
                    align_left=True,
                    align_top=False,
                    x_offset=-120,
                    y_offset=-170,
                    opacity=0.12,
                ),
                ambient_orb(
                    size=460,
                    color_hex="#22c55e",
                    align_left=False,
                    align_top=False,
                    x_offset=-170,
                    y_offset=-160,
                    opacity=0.10,
                ),
                ft.Row(
                    controls=[
                        ft.Container(
                            expand=True,
                            content=hero,
                            visible=True,
                        ),
                        ft.Container(
                            width=520,
                            bgcolor=ft.colors.with_opacity(0.36, Colors.surface),
                            border=ft.border.only(left=ft.BorderSide(1, ft.colors.with_opacity(0.85, Colors.border))),
                            content=ft.Column(
                                controls=[
                                    ft.Container(
                                        expand=True,
                                        alignment=ft.alignment.center,
                                        padding=ft.padding.symmetric(horizontal=30, vertical=24),
                                        content=panel,
                                    ),
                                    ft.Container(
                                        padding=ft.padding.only(left=30, right=30, bottom=22, top=6),
                                        content=ft.Text(
                                            "Built for students, developers, and modern software teams.",
                                            style=Typography.caption(),
                                            text_align=ft.TextAlign.CENTER,
                                        ),
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                expand=True,
                            ),
                        ),
                    ],
                    spacing=0,
                    expand=True,
                    vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                ),
            ],
        ),
    )


def _hero_panel() -> ft.Control:
    heading = ft.Column(
        controls=[
            brand_logo(
                subtitle="AI-powered decision support",
                icon_size=48,
                title_size=33,
                subtitle_size=15,
            ),
            ft.Container(height=Spacing.lg),
            _pill_badge("AI-powered decision support", "Explainable recommendations"),
            ft.Container(height=Spacing.md),
            ft.Text(
                "Your AI software architect for smarter tech decisions.",
                style=Typography.display(size=48, weight=ft.FontWeight.W_800),
            ),
            ft.Text(
                "StackWise AI analyzes your project goals, complexity, timeline, team size, "
                "scalability, and security needs to recommend the right programming language, "
                "framework, and SDLC model with clear reasoning.",
                style=Typography.body(size=15),
            ),
            ft.Container(height=Spacing.lg),
            feature_item(
                icon=ft.icons.AUTO_AWESOME,
                title="AI-powered recommendation engine",
                body="Analyzes project requirements and suggests the best-fit stack.",
            ),
            feature_item(
                icon=ft.icons.TROUBLESHOOT_OUTLINED,
                title="Explainable decision support",
                body="Shows why a language, framework, or SDLC model fits your project.",
            ),
            feature_item(
                icon=ft.icons.INSIGHTS_OUTLINED,
                title="Confidence scoring",
                body="Provides measurable confidence based on project complexity and constraints.",
            ),
            feature_item(
                icon=ft.icons.MENU_BOOK_OUTLINED,
                title="Learning-focused guidance",
                body="Helps students and developers understand the reasoning behind each recommendation.",
            ),
            ft.Container(height=Spacing.sm),
            _mini_preview(),
        ],
        spacing=Spacing.sm,
        scroll=ft.ScrollMode.AUTO,
    )

    return ft.Container(
        expand=True,
        bgcolor=ft.colors.with_opacity(0.16, Colors.surface),
        border=ft.border.only(
            right=ft.BorderSide(1, ft.colors.with_opacity(0.7, Colors.border)),
        ),
        content=ft.Stack(
            controls=[
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=62, vertical=48),
                    content=heading,
                ),
            ],
            expand=True,
        ),
    )

def _pill_badge(left: str, right: str) -> ft.Control:
    dot = ft.Container(
        width=7,
        height=7,
        border_radius=999,
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[Colors.primary, Colors.accent_cyan],
        ),
    )
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=12, vertical=8),
        border_radius=Radii.pill,
        bgcolor=ft.colors.with_opacity(0.35, Colors.surface),
        border=ft.border.all(1, ft.colors.with_opacity(0.75, Colors.border)),
        content=ft.Row(
            spacing=8,
            tight=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                dot,
                ft.Text(left, size=12.5, weight=ft.FontWeight.W_600, color=Colors.text_primary),
                ft.Text("•", size=12, color=Colors.text_muted),
                ft.Text(right, size=12.5, color=Colors.text_secondary),
            ],
        ),
    )


def _mini_preview() -> ft.Control:
    header = ft.Row(
        spacing=Spacing.sm,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Icon(ft.icons.ROCKET_LAUNCH_OUTLINED, size=18, color=Colors.primary_glow),
            ft.Text("Recommended Stack", style=Typography.subheading(size=14)),
            ft.Container(expand=True),
            ft.Container(
                padding=ft.padding.symmetric(horizontal=10, vertical=6),
                border_radius=Radii.pill,
                bgcolor=ft.colors.with_opacity(0.10, Colors.success),
                border=ft.border.all(1, ft.colors.with_opacity(0.22, Colors.success)),
                content=ft.Text("Confidence: 92%", size=12, color=Colors.text_primary, weight=ft.FontWeight.W_600),
            ),
        ],
    )

    body = ft.Column(
        spacing=7,
        controls=[
            ft.Row(
                spacing=Spacing.md,
                controls=[
                    _kv("Language", "Python"),
                    _kv("Framework", "FastAPI"),
                    _kv("SDLC", "Agile"),
                ],
            ),
            ft.Text(
                "Best fit for scalable AI-assisted platforms with medium-to-high complexity.",
                style=Typography.body(size=12.5),
            ),
        ],
    )

    return gradient_card(
        content=ft.Column(spacing=Spacing.md, controls=[header, body]),
        padding=ft.padding.symmetric(horizontal=16, vertical=14),
        radius=Radii.lg,
        width=540,
    )


def _kv(k: str, v: str) -> ft.Control:
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=12, vertical=10),
        border_radius=Radii.md,
        bgcolor=ft.colors.with_opacity(0.55, Colors.surface),
        border=ft.border.all(1, ft.colors.with_opacity(0.75, Colors.border)),
        content=ft.Column(
            spacing=2,
            tight=True,
            controls=[
                ft.Text(k, style=Typography.caption()),
                ft.Text(v, style=Typography.subheading(size=13)),
            ],
        ),
    )
