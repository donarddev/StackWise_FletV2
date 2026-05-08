"""RecommendationDetailDialog — full breakdown of a single recommendation."""

from __future__ import annotations

import flet as ft

from app.helpers.date_helper import humanize
from app.models.recommendation import Recommendation
from ui.components.confidence_bar import confidence_bar
from ui.themes.app_theme import Colors, Radii, Spacing, Typography


def build_recommendation_detail_dialog(rec: Recommendation, *, on_close) -> ft.AlertDialog:
    return ft.AlertDialog(
        modal=True,
        bgcolor=Colors.surface,
        shape=ft.RoundedRectangleBorder(radius=Radii.lg),
        content=ft.Container(
            width=720,
            content=_dialog_body(rec),
        ),
        actions=[ft.TextButton("Close", on_click=on_close)],
    )


def _dialog_body(rec: Recommendation) -> ft.Control:
    sections: list[ft.Control] = [
        _section_header(rec),
        ft.Divider(color=Colors.border, height=1),
        confidence_bar(rec.confidence_score),
        _summary_block(rec),
        _why_blocks(rec),
        _alternatives_block(rec),
        _trade_off_block(rec),
        _project_profile_block(rec),
    ]
    return ft.Column(
        controls=sections,
        spacing=Spacing.lg,
        scroll=ft.ScrollMode.ADAPTIVE,
        height=560,
    )


def _section_header(rec: Recommendation) -> ft.Control:
    return ft.Column(
        spacing=4,
        controls=[
            ft.Text(rec.project_name, style=Typography.heading(size=20)),
            ft.Text(
                f"{rec.project_type} · {rec.complexity} · created {humanize(rec.created_at)}",
                style=Typography.caption(),
            ),
            ft.Container(height=Spacing.sm),
            ft.Row(
                spacing=Spacing.sm, wrap=True, run_spacing=Spacing.sm,
                controls=[
                    _result_chip("Language", rec.recommended_language, Colors.primary),
                    _result_chip("Framework", rec.recommended_framework, Colors.accent_cyan),
                    _result_chip("SDLC", rec.recommended_sdlc, Colors.accent_pink),
                ],
            ),
        ],
    )


def _result_chip(label: str, value: str, accent: str) -> ft.Control:
    return ft.Container(
        bgcolor=ft.colors.with_opacity(0.12, accent),
        border=ft.border.all(1, ft.colors.with_opacity(0.4, accent)),
        border_radius=Radii.pill,
        padding=ft.padding.symmetric(horizontal=12, vertical=6),
        content=ft.Row(
            spacing=6, tight=True,
            controls=[
                ft.Text(
                    label.upper(),
                    style=ft.TextStyle(
                        size=10.5, weight=ft.FontWeight.W_700,
                        color=accent, letter_spacing=1.4,
                    ),
                ),
                ft.Text(value, size=12.5, weight=ft.FontWeight.W_700, color=Colors.text_primary),
            ],
        ),
    )


def _summary_block(rec: Recommendation) -> ft.Control:
    summary = (rec.explanation or {}).get("summary", "")
    if not summary:
        return ft.Container(visible=False)
    return _block(
        title="Summary",
        body=ft.Text(summary, style=Typography.body(size=13.5)),
    )


def _why_blocks(rec: Recommendation) -> ft.Control:
    expl = rec.explanation or {}
    items = []
    for key in ("why_language", "why_framework", "why_sdlc"):
        section = expl.get(key) or {}
        title = section.get("title")
        points = section.get("points") or []
        if not title or not points:
            continue
        items.append(
            _block(
                title=title,
                body=ft.Column(
                    spacing=6,
                    controls=[_bullet(p) for p in points],
                ),
            )
        )
    return ft.Column(controls=items, spacing=Spacing.md)


def _alternatives_block(rec: Recommendation) -> ft.Control:
    expl = rec.explanation or {}
    alts = rec.alternatives or {}
    if not alts:
        return ft.Container(visible=False)

    def section(title_key: str, alt_key: str, label: str) -> ft.Control:
        runners = expl.get(title_key) or []
        if not runners and not (alts.get(alt_key) or [])[1:]:
            return ft.Container(visible=False)

        rows: list[ft.Control] = []
        for runner in runners:
            rows.append(
                ft.Container(
                    padding=Spacing.md,
                    bgcolor=Colors.surface_2,
                    border=ft.border.all(1, Colors.border),
                    border_radius=Radii.md,
                    content=ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text(runner.get("name", ""), size=13.5,
                                    weight=ft.FontWeight.W_700, color=Colors.text_primary),
                            ft.Text(runner.get("reason", ""), style=Typography.body(size=12.5)),
                        ],
                    ),
                )
            )
        if not rows:
            return ft.Container(visible=False)
        return _block(title=f"Why not the other {label}", body=ft.Column(spacing=Spacing.sm, controls=rows))

    return ft.Column(
        spacing=Spacing.md,
        controls=[
            section("why_not_languages", "languages", "languages"),
            section("why_not_frameworks", "frameworks", "frameworks"),
            section("why_not_sdlc", "sdlc", "SDLC models"),
        ],
    )


def _trade_off_block(rec: Recommendation) -> ft.Control:
    expl = rec.explanation or {}
    trade = expl.get("trade_offs") or []
    if not trade:
        return ft.Container(visible=False)
    return _block(
        title="Trade-offs to keep in mind",
        body=ft.Column(spacing=6, controls=[_bullet(t) for t in trade]),
    )


def _project_profile_block(rec: Recommendation) -> ft.Control:
    items = [
        ("Project Type", rec.project_type),
        ("Goal", rec.project_goal),
        ("Complexity", rec.complexity),
        ("Team", rec.team_size),
        ("Timeline", rec.timeline),
        ("Scalability", rec.scalability),
        ("Security", rec.security),
        ("Platform", rec.platform),
        ("Experience", rec.experience),
    ]
    rows: list[ft.Control] = []
    for k, v in items:
        rows.append(
            ft.Row(
                controls=[
                    ft.Text(k, size=12.5, color=Colors.text_muted, width=120),
                    ft.Text(v, size=13, weight=ft.FontWeight.W_600, color=Colors.text_primary),
                ],
                spacing=Spacing.md,
            )
        )
    return _block(title="Project profile", body=ft.Column(spacing=6, controls=rows))


def _block(*, title: str, body: ft.Control) -> ft.Control:
    return ft.Container(
        padding=Spacing.lg,
        bgcolor=Colors.surface_2,
        border=ft.border.all(1, Colors.border),
        border_radius=Radii.md,
        content=ft.Column(
            spacing=Spacing.md,
            controls=[
                ft.Text(title, style=Typography.subheading(size=14)),
                body,
            ],
        ),
    )


def _bullet(text: str) -> ft.Control:
    return ft.Row(
        controls=[
            ft.Container(
                width=6, height=6, border_radius=999,
                bgcolor=Colors.primary_glow,
                margin=ft.margin.only(top=8),
            ),
            ft.Text(text, style=Typography.body(size=13), expand=True),
        ],
        spacing=Spacing.sm,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )
