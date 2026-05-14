"""CompareDialog — side-by-side comparison of two recommendations (History)."""

from __future__ import annotations

from typing import Any

import flet as ft

from app.helpers.date_helper import humanize
from app.models.recommendation import Recommendation
from app.utils.constants import confidence_label
from ui.components.background_layers import subtle_grid_layer
from ui.components.glass_card import glass_card
from ui.themes.app_theme import Colors, Gradients, Radii, Spacing, Typography

_NA = "Not available"


def _s(value: Any) -> str:
    if value is None:
        return _NA
    if isinstance(value, str):
        t = value.strip()
        return t if t else _NA
    return str(value)


def _expl(rec: Recommendation) -> dict:
    return rec.explanation if isinstance(rec.explanation, dict) else {}


def _summary_text(rec: Recommendation) -> str:
    expl = _expl(rec)
    return _s(expl.get("summary") or expl.get("presentation_summary"))


def _strength_lines(rec: Recommendation) -> list[str]:
    expl = _expl(rec)
    lines: list[str] = []
    for key in ("why_language", "why_framework", "why_sdlc"):
        sec = expl.get(key) or {}
        title = sec.get("title")
        points = sec.get("points") or []
        if not title or not points:
            continue
        lines.append(str(title))
        for p in points:
            lines.append(f"• {p}")
    return lines


def _string_list(expl: dict, key: str) -> list[str]:
    raw = expl.get(key)
    if not raw:
        return []
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    return [str(raw).strip()] if str(raw).strip() else []


def _risks_and_tradeoffs_lines(rec: Recommendation) -> list[str]:
    expl = _expl(rec)
    out: list[str] = []
    for t in _string_list(expl, "trade_offs"):
        out.append(f"Trade-off: {t}")
    for t in _string_list(expl, "risk_analysis"):
        out.append(f"Risk: {t}")
    return out


def _confidence_badge(score: int) -> ft.Control:
    if score >= 80:
        accent, tint = Colors.success, Colors.success
    elif score >= 60:
        accent, tint = Colors.primary_soft, Colors.primary
    elif score >= 45:
        accent, tint = Colors.warning, Colors.warning
    else:
        accent, tint = Colors.danger, Colors.danger
    label = confidence_label(score)
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=12, vertical=8),
        border_radius=Radii.pill,
        bgcolor=ft.colors.with_opacity(0.16, tint),
        border=ft.border.all(1, ft.colors.with_opacity(0.55, accent)),
        content=ft.Text(
            f"{score}% · {label}",
            size=13,
            weight=ft.FontWeight.W_700,
            color=accent,
        ),
    )


def _diff_kind(left: str, right: str) -> str | None:
    """Return accent color hint when values differ (readable on dark)."""
    if _norm(left) == _norm(right):
        return None
    return Colors.accent_cyan


def _norm(t: str) -> str:
    return " ".join(t.lower().split())


def _pair_cell(text: str, *, highlight: bool, side: str) -> ft.Control:
    border_color = (
        ft.colors.with_opacity(0.75, Colors.accent_cyan if side == "left" else Colors.primary)
        if highlight
        else ft.colors.with_opacity(0.35, Colors.border_strong)
    )
    return ft.Container(
        expand=1,
        padding=Spacing.lg,
        border_radius=Radii.md,
        bgcolor=ft.colors.with_opacity(0.45, Colors.surface_2),
        border=ft.border.all(1.5, border_color),
        content=ft.Text(
            text,
            size=13.5,
            color=Colors.text_primary if text != _NA else Colors.text_muted,
        ),
    )


def _pair_row(*, label: str, left: str, right: str) -> ft.Control:
    hl = _diff_kind(left, right) is not None
    return ft.Container(
        padding=ft.padding.only(bottom=Spacing.md),
        content=ft.Column(
            spacing=Spacing.sm,
            tight=True,
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=10, vertical=4),
                            border_radius=Radii.pill,
                            bgcolor=ft.colors.with_opacity(0.14, Colors.primary),
                            border=ft.border.all(1, ft.colors.with_opacity(0.4, Colors.primary)),
                            content=ft.Text(label.upper(), size=10.5, weight=ft.FontWeight.W_700, color=Colors.primary_soft),
                        ),
                    ],
                ),
                ft.Row(
                    spacing=Spacing.md,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        _pair_cell(left, highlight=hl, side="left"),
                        _pair_cell(right, highlight=hl, side="right"),
                    ],
                ),
            ],
        ),
    )


def _bullet_column(lines: list[str]) -> ft.Control:
    if not lines:
        return ft.Text(_NA, size=13, color=Colors.text_muted)
    return ft.Column(
        spacing=6,
        controls=[
            ft.Row(
                spacing=Spacing.sm,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(
                        width=5,
                        height=5,
                        border_radius=99,
                        bgcolor=Colors.accent_cyan,
                        margin=ft.margin.only(top=7),
                    ),
                    ft.Text(line, size=13, color=Colors.text_primary, expand=True),
                ],
            )
            for line in lines
        ],
    )


def _pair_list_row(*, label: str, left_lines: list[str], right_lines: list[str]) -> ft.Control:
    hl = left_lines != right_lines
    border_l = ft.colors.with_opacity(0.75, Colors.accent_cyan) if hl else ft.colors.with_opacity(0.35, Colors.border_strong)
    border_r = ft.colors.with_opacity(0.75, Colors.primary) if hl else ft.colors.with_opacity(0.35, Colors.border_strong)
    return ft.Container(
        padding=ft.padding.only(bottom=Spacing.lg),
        content=ft.Column(
            spacing=Spacing.sm,
            tight=True,
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=10, vertical=4),
                            border_radius=Radii.pill,
                            bgcolor=ft.colors.with_opacity(0.12, Colors.warning),
                            border=ft.border.all(1, ft.colors.with_opacity(0.45, Colors.warning)),
                            content=ft.Text(label.upper(), size=10.5, weight=ft.FontWeight.W_700, color=Colors.warning),
                        ),
                    ],
                ),
                ft.Row(
                    spacing=Spacing.md,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Container(
                            expand=1,
                            padding=Spacing.lg,
                            border_radius=Radii.md,
                            bgcolor=ft.colors.with_opacity(0.45, Colors.surface_2),
                            border=ft.border.all(1.5, border_l),
                            content=_bullet_column(left_lines),
                        ),
                        ft.Container(
                            expand=1,
                            padding=Spacing.lg,
                            border_radius=Radii.md,
                            bgcolor=ft.colors.with_opacity(0.45, Colors.surface_2),
                            border=ft.border.all(1.5, border_r),
                            content=_bullet_column(right_lines),
                        ),
                    ],
                ),
            ],
        ),
    )


def _top_pane(rec: Recommendation, *, subtitle: str) -> ft.Control:
    created = humanize(rec.created_at) if rec.created_at else _NA
    return glass_card(
        ft.Column(
            spacing=Spacing.md,
            tight=True,
            controls=[
                ft.Text(subtitle, style=Typography.caption()),
                ft.Text(_s(rec.project_name), style=Typography.subheading(size=16)),
                ft.Text(f"Created {created}", style=Typography.caption()),
                ft.Divider(color=ft.colors.with_opacity(0.35, Colors.border_strong), height=1),
                _labeled_value("Language", _s(rec.recommended_language), Colors.primary),
                _labeled_value("Framework", _s(rec.recommended_framework), Colors.accent_cyan),
                _labeled_value("SDLC", _s(rec.recommended_sdlc), Colors.accent_pink),
                ft.Row(
                    controls=[
                        ft.Text("Confidence", size=12, color=Colors.text_muted),
                        _confidence_badge(int(rec.confidence_score or 0)),
                    ],
                    spacing=Spacing.md,
                ),
            ],
        ),
        padding=Spacing.lg,
        bgcolor=ft.colors.with_opacity(0.55, Colors.surface_2),
        border_color=ft.colors.with_opacity(0.55, Colors.border_strong),
        glow=True,
    )


def _labeled_value(label: str, value: str, accent: str) -> ft.Control:
    return ft.Column(
        spacing=4,
        tight=True,
        controls=[
            ft.Text(label.upper(), size=10, weight=ft.FontWeight.W_700, color=accent),
            ft.Text(value, size=14, weight=ft.FontWeight.W_600, color=Colors.text_primary),
        ],
    )


def build_compare_dialog(left: Recommendation, right: Recommendation, *, on_close) -> ft.AlertDialog:
    body = ft.Container(
        width=960,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        border_radius=Radii.xl,
        gradient=Gradients.card_subtle(),
        border=ft.border.all(1, ft.colors.with_opacity(0.55, Colors.accent_cyan)),
        shadow=ft.BoxShadow(
            blur_radius=36,
            spread_radius=0,
            color="#8b5cf655",
            offset=ft.Offset(0, 16),
        ),
        content=ft.Stack(
            controls=[
                ft.Container(expand=True, content=subtle_grid_layer(opacity=0.06)),
                ft.Container(
                    padding=Spacing.xl,
                    content=ft.Column(
                        spacing=Spacing.lg,
                        controls=[
                            ft.Column(
                                spacing=Spacing.xs,
                                tight=True,
                                controls=[
                                    ft.Text("Compare recommendations", style=Typography.heading(size=22)),
                                    ft.Text(
                                        "Differences use teal (left) and purple (right) outlines. "
                                        "Missing sections show as 'Not available'.",
                                        style=Typography.body(size=13),
                                    ),
                                ],
                            ),
                            ft.Row(
                                spacing=Spacing.lg,
                                vertical_alignment=ft.CrossAxisAlignment.START,
                                controls=[
                                    ft.Container(expand=1, content=_top_pane(left, subtitle="Recommendation A")),
                                    ft.Container(expand=1, content=_top_pane(right, subtitle="Recommendation B")),
                                ],
                            ),
                            _pair_row(
                                label="Explanation summary",
                                left=_summary_text(left),
                                right=_summary_text(right),
                            ),
                            _pair_list_row(
                                label="Strengths (rationale)",
                                left_lines=_strength_lines(left),
                                right_lines=_strength_lines(right),
                            ),
                            _pair_list_row(
                                label="Risks & trade-offs",
                                left_lines=_risks_and_tradeoffs_lines(left),
                                right_lines=_risks_and_tradeoffs_lines(right),
                            ),
                            _pair_list_row(
                                label="Skill gaps",
                                left_lines=_string_list(_expl(left), "skill_gap_analysis"),
                                right_lines=_string_list(_expl(right), "skill_gap_analysis"),
                            ),
                            _pair_list_row(
                                label="Roadmap / next steps",
                                left_lines=_string_list(_expl(left), "roadmap"),
                                right_lines=_string_list(_expl(right), "roadmap"),
                            ),
                        ],
                        scroll=ft.ScrollMode.AUTO,
                        height=560,
                    ),
                ),
            ],
        ),
    )

    return ft.AlertDialog(
        modal=True,
        bgcolor=ft.colors.with_opacity(0.72, "#020617"),
        alignment=ft.alignment.center,
        elevation=0,
        shape=ft.RoundedRectangleBorder(radius=Radii.xl + 4),
        content=body,
        actions=[
            ft.TextButton("Close", on_click=on_close, tooltip="Close comparison"),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        actions_padding=ft.padding.symmetric(horizontal=Spacing.xl, vertical=Spacing.md),
    )
