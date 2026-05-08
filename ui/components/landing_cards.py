"""Reusable premium cards/badges for landing sections."""

from __future__ import annotations

from typing import Optional

import flet as ft

from ui.themes.app_theme import Colors, Radii, Spacing, Typography


def section_badge(text: str) -> ft.Control:
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=10, vertical=5),
        border_radius=Radii.pill,
        bgcolor=ft.colors.with_opacity(0.13, "#2dd4bf"),
        border=ft.border.all(1, ft.colors.with_opacity(0.22, "#2dd4bf")),
        content=ft.Text(text, size=11.5, color=Colors.text_primary, weight=ft.FontWeight.W_600),
    )


def status_pill(text: str) -> ft.Control:
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=10, vertical=5),
        border_radius=Radii.pill,
        bgcolor=ft.colors.with_opacity(0.14, "#34d399"),
        border=ft.border.all(1, ft.colors.with_opacity(0.24, "#34d399")),
        content=ft.Text(text, size=11.5, color=Colors.text_primary, weight=ft.FontWeight.W_600),
    )


def landing_feature_card(
    *,
    title: str,
    body: str,
    status: Optional[str] = None,
    compact: bool = False,
    workflow: bool = False,
    height: Optional[int] = None,
) -> ft.Control:
    icon_dot = ft.Container(
        width=10 if compact else 11,
        height=10 if compact else 11,
        border_radius=999,
        bgcolor="#34d399",
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=10,
            color="#34d39955",
            offset=ft.Offset(0, 0),
        ),
        animate=ft.Animation(180, ft.AnimationCurve.EASE_OUT),
    )
    card = ft.Container(
        padding=ft.padding.symmetric(horizontal=16, vertical=16 if compact else 18),
        border_radius=Radii.lg,
        bgcolor=ft.colors.with_opacity(0.5, Colors.surface_2),
        border=ft.border.all(1, ft.colors.with_opacity(0.72, Colors.border)),
        height=height,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=14,
            color="#00000022",
            offset=ft.Offset(0, 4),
        ),
        scale=ft.Scale(1),
        animate=ft.Animation(190, ft.AnimationCurve.EASE_OUT),
        animate_scale=ft.Animation(180, ft.AnimationCurve.EASE_OUT),
        content=ft.Column(
            spacing=Spacing.sm,
            controls=[
                ft.Row(
                    controls=[
                        icon_dot,
                        ft.Container(expand=True),
                        *([status_pill(status)] if status else []),
                    ],
                ),
                *(_workflow_text(title, body) if workflow else [
                    ft.Text(title, style=Typography.subheading(size=17 if compact else 18)),
                    ft.Text(body, style=Typography.body(size=13.3 if compact else 13.5)),
                ]),
            ],
        ),
        on_hover=lambda e: _on_card_hover(e, card, icon_dot),
    )
    return card


def _workflow_text(step: str, body: str) -> list[ft.Control]:
    parts = body.split("\n", 1)
    heading = parts[0] if parts else body
    desc = parts[1] if len(parts) > 1 else ""
    return [
        section_badge(step.strip()),
        ft.Text(heading, style=Typography.subheading(size=18)),
        ft.Text(desc, style=Typography.body(size=13.5)),
    ]


def _on_card_hover(
    e: ft.ControlEvent,
    card: ft.Container,
    icon_dot: ft.Container,
) -> None:
    hovered = str(e.data).lower() == "true"
    if hovered:
        card.border = ft.border.all(1, ft.colors.with_opacity(0.45, "#2dd4bf"))
        card.bgcolor = ft.colors.with_opacity(0.66, Colors.surface_2)
        card.shadow = ft.BoxShadow(
            spread_radius=0,
            blur_radius=24,
            color="#2dd4bf2b",
            offset=ft.Offset(0, 8),
        )
        card.scale = ft.Scale(1.012)
        icon_dot.shadow = ft.BoxShadow(
            spread_radius=0,
            blur_radius=16,
            color="#34d39988",
            offset=ft.Offset(0, 0),
        )
    else:
        card.border = ft.border.all(1, ft.colors.with_opacity(0.72, Colors.border))
        card.bgcolor = ft.colors.with_opacity(0.5, Colors.surface_2)
        card.shadow = ft.BoxShadow(
            spread_radius=0,
            blur_radius=14,
            color="#00000022",
            offset=ft.Offset(0, 4),
        )
        card.scale = ft.Scale(1)
        icon_dot.shadow = ft.BoxShadow(
            spread_radius=0,
            blur_radius=10,
            color="#34d39955",
            offset=ft.Offset(0, 0),
        )
    card.update()
    icon_dot.update()
