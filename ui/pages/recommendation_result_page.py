"""Dedicated decision report page for a single saved recommendation."""

from __future__ import annotations

import re
from typing import Any, Callable, Mapping, Optional

import flet as ft

from app.helpers.date_helper import humanize
from app.models.recommendation import Recommendation
from app.models.recommendation_feedback import RecommendationFeedback
from app.utils.constants import confidence_label
from ui.components.input_field import input_field
from ui.components.confidence_bar import confidence_bar
from ui.components.empty_state import empty_state
from ui.components.primary_button import primary_button
from ui.pages.recommendation_page import recommendation_workspace_theme
from ui.themes.app_theme import Radii, Spacing

# Report design tokens (StackWise dark glass)
_C_PRIMARY = "#F8FAFC"
_C_SECONDARY = "#AAB6C8"
_C_MUTED = "#72809A"
_C_CYAN = "#22D3EE"
_C_WARNING = "#F59E0B"
_C_PURPLE = "#8B5CF6"
_C_PANEL = "#132033"
_C_PANEL_BD = "#2A3B55"
_C_INNER = "#101827"
_C_INNER_BD = "#24364F"
_C_RISK_BG = "#1C1B16"
_C_RISK_BD = "#B45309"

_PAGE_PAD = 44
_SECTION_GAP = 24
_CARD_GAP = 16
_INNER_PAD = 18
_PANEL_PAD = 24

_GLASS_SHADOW = ft.BoxShadow(
    blur_radius=18,
    spread_radius=0,
    color="#00000030",
    offset=ft.Offset(0, 8),
)


def build_recommendation_result_page(
    *,
    rec: Optional[Recommendation],
    theme: Mapping[str, Any],
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
                        _compact_action(
                            "Back to History", ft.icons.HISTORY, on_back_history,
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

    content = ft.Column(
        spacing=_SECTION_GAP,
        controls=[
            _hero_card(
                rec,
                created_short=created_short,
                on_back_recommendation=on_back_recommendation,
                on_back_history=on_back_history,
                on_copy_summary=on_copy_summary,
                on_regenerate=on_regenerate,
            ),
            _saved_recommendation_card(rec),
            _main_report_grid(
                rec,
                theme,
                created_short=created_short,
                on_back_recommendation=on_back_recommendation,
                on_back_history=on_back_history,
                on_dashboard=on_dashboard,
                on_copy_summary=on_copy_summary,
                on_feedback=on_feedback,
                on_submit_feedback=on_submit_feedback,
                existing_feedback=existing_feedback,
                feedback_section_ref=feedback_section_ref,
                feedback_rating_ref=feedback_rating_ref,
                feedback_comment_ref=feedback_comment_ref,
                feedback_error_ref=feedback_error_ref,
                feedback_success_ref=feedback_success_ref,
            ),
        ],
    )

    return ft.Container(
        padding=ft.padding.symmetric(horizontal=_PAGE_PAD, vertical=_PAGE_PAD - 4),
        content=content,
    )


# ---------- shell helpers ----------


def _glass_card(body: ft.Control, *, padding: int = _PANEL_PAD) -> ft.Control:
    return ft.Container(
        bgcolor=_C_PANEL,
        border=ft.border.all(1, _C_PANEL_BD),
        border_radius=22,
        padding=padding,
        shadow=_GLASS_SHADOW,
        content=body,
    )


def _inner_card(body: ft.Control, *, padding: int = _INNER_PAD) -> ft.Control:
    return ft.Container(
        bgcolor=_C_INNER,
        border=ft.border.all(1, _C_INNER_BD),
        border_radius=16,
        padding=padding,
        content=body,
    )


def _section_title(title: str, *, subtitle: Optional[str] = None) -> ft.Control:
    controls: list[ft.Control] = [
        ft.Text(title, size=17, weight=ft.FontWeight.W_600, color=_C_PRIMARY),
    ]
    if subtitle:
        controls.append(ft.Text(subtitle, size=13, color=_C_SECONDARY))
    return ft.Column(spacing=4, tight=True, controls=controls)


def _details_badge() -> ft.Control:
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.icons.DESCRIPTION_OUTLINED, size=12, color=_C_CYAN),
                ft.Text("RECOMMENDATION DETAILS", size=10, weight=ft.FontWeight.W_700, color=_C_CYAN),
            ],
            spacing=6,
            tight=True,
        ),
        bgcolor=ft.colors.with_opacity(0.1, _C_CYAN),
        border=ft.border.all(1, ft.colors.with_opacity(0.35, _C_CYAN)),
        border_radius=Radii.pill,
        padding=ft.padding.symmetric(horizontal=10, vertical=5),
    )


def _confidence_pill(score: int) -> ft.Control:
    score = max(0, min(100, int(score)))
    label = confidence_label(score)
    return ft.Container(
        content=ft.Text(
            f"{score}% · {label}",
            size=12,
            weight=ft.FontWeight.W_600,
            color=_C_PURPLE,
        ),
        bgcolor=ft.colors.with_opacity(0.12, _C_PURPLE),
        border=ft.border.all(1, ft.colors.with_opacity(0.35, _C_PURPLE)),
        border_radius=Radii.pill,
        padding=ft.padding.symmetric(horizontal=12, vertical=6),
    )


def _compact_action(
    label: str,
    icon: str,
    on_click: Callable[[ft.ControlEvent], None],
    *,
    primary: bool = False,
) -> ft.Control:
    if primary:
        return ft.Container(
            height=38,
            bgcolor=_C_CYAN,
            border_radius=12,
            alignment=ft.alignment.center,
            ink=True,
            on_click=on_click,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=6,
                controls=[
                    ft.Icon(icon, size=16, color="#06111F"),
                    ft.Text(label, size=12, weight=ft.FontWeight.W_600, color="#06111F"),
                ],
            ),
        )
    return ft.Container(
        height=38,
        bgcolor=_C_INNER,
        border=ft.border.all(1, _C_PANEL_BD),
        border_radius=12,
        alignment=ft.alignment.center,
        ink=True,
        on_click=on_click,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=6,
            controls=[
                ft.Icon(icon, size=16, color=_C_SECONDARY),
                ft.Text(label, size=12, weight=ft.FontWeight.W_600, color=_C_PRIMARY),
            ],
        ),
    )


def _hero_meta_chip(label: str, value: str) -> ft.Control:
    return _inner_card(
        ft.Column(
            spacing=4,
            tight=True,
            controls=[
                ft.Text(label.upper(), size=10, weight=ft.FontWeight.W_700, color=_C_MUTED),
                ft.Text(
                    value,
                    size=14,
                    weight=ft.FontWeight.W_700,
                    color=_C_PRIMARY,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
        ),
        padding=12,
    )


# ---------- hero & saved recommendation ----------


def _hero_card(
    rec: Recommendation,
    *,
    created_short: str,
    on_back_recommendation: Callable[[ft.ControlEvent], None],
    on_back_history: Callable[[ft.ControlEvent], None],
    on_copy_summary: Optional[Callable[[ft.ControlEvent], None]],
    on_regenerate: Optional[Callable[[ft.ControlEvent], None]],
) -> ft.Control:
    subtitle = f"{rec.project_type} · {rec.complexity} · {created_short}"

    left = ft.Column(
        spacing=12,
        tight=True,
        controls=[
            _details_badge(),
            ft.Row(
                spacing=12,
                wrap=True,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        rec.project_name,
                        size=28,
                        weight=ft.FontWeight.W_700,
                        color=_C_PRIMARY,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    _confidence_pill(rec.confidence_score),
                ],
            ),
            ft.Text(subtitle, size=14, color=_C_SECONDARY),
        ],
    )

    action_btns: list[ft.Control] = [
        _compact_action("Back to Recommendation", ft.icons.ARROW_BACK, on_back_recommendation),
        _compact_action("Back to History", ft.icons.HISTORY, on_back_history),
    ]
    if on_copy_summary is not None:
        action_btns.append(
            _compact_action("Copy Summary", ft.icons.CONTENT_COPY_OUTLINED, on_copy_summary),
        )
    if on_regenerate is not None:
        action_btns.append(
            _compact_action("Regenerate", ft.icons.REFRESH_ROUNDED, on_regenerate, primary=True),
        )

    action_rows: list[ft.Control] = []
    for i in range(0, len(action_btns), 2):
        pair = action_btns[i : i + 2]
        if len(pair) == 1:
            action_rows.append(pair[0])
        else:
            action_rows.append(
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.Container(content=pair[0], expand=True),
                        ft.Container(content=pair[1], expand=True),
                    ],
                )
            )

    right = ft.Column(
        spacing=12,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        controls=[
            ft.Row(
                spacing=10,
                controls=[
                    ft.Container(content=_hero_meta_chip("Record ID", f"#{rec.id}"), expand=True),
                    ft.Container(content=_hero_meta_chip("Generated", created_short), expand=True),
                ],
            ),
            ft.Column(spacing=10, tight=True, controls=action_rows),
        ],
    )

    body = ft.ResponsiveRow(
        spacing=_SECTION_GAP,
        run_spacing=_CARD_GAP,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[
            ft.Container(col={"xs": 12, "md": 7}, content=left),
            ft.Container(col={"xs": 12, "md": 5}, content=right),
        ],
    )
    return _glass_card(body)


def _saved_recommendation_card(rec: Recommendation) -> ft.Control:
    score = max(0, min(100, int(rec.confidence_score)))
    conf_label = confidence_label(score)

    stat_row = ft.ResponsiveRow(
        spacing=_CARD_GAP,
        run_spacing=_CARD_GAP,
        controls=[
            ft.Container(
                col={"xs": 6, "sm": 3},
                content=_rec_stat_tile("Programming Language", rec.recommended_language),
            ),
            ft.Container(
                col={"xs": 6, "sm": 3},
                content=_rec_stat_tile("Framework", rec.recommended_framework),
            ),
            ft.Container(
                col={"xs": 6, "sm": 3},
                content=_rec_stat_tile("SDLC Model", rec.recommended_sdlc),
            ),
            ft.Container(
                col={"xs": 6, "sm": 3},
                content=_rec_stat_tile("Confidence Score", f"{score}% {conf_label}", large=True),
            ),
        ],
    )

    bar = ft.Column(
        spacing=6,
        controls=[
            ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("Confidence", size=12, color=_C_MUTED),
                    ft.Container(expand=True),
                    ft.Text(
                        f"{score}/100",
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color=_C_PURPLE,
                    ),
                ],
            ),
            ft.ProgressBar(
                value=score / 100.0,
                bgcolor=ft.colors.with_opacity(0.15, _C_PURPLE),
                color=_C_PURPLE,
                bar_height=6,
                border_radius=Radii.pill,
            ),
        ],
    )

    body = ft.Column(
        spacing=_CARD_GAP,
        controls=[
            _section_title(
                "Saved Recommendation",
                subtitle="The strongest stack match based on your project profile.",
            ),
            stat_row,
            bar,
        ],
    )
    return _glass_card(body)


def _rec_stat_tile(label: str, value: str, *, large: bool = False) -> ft.Control:
    return _inner_card(
        ft.Column(
            spacing=6,
            tight=True,
            controls=[
                ft.Text(label.upper(), size=10, weight=ft.FontWeight.W_700, color=_C_MUTED),
                ft.Text(
                    value,
                    size=20 if large else 15,
                    weight=ft.FontWeight.W_700,
                    color=_C_PRIMARY,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
        ),
        padding=14,
    )


# ---------- main grid ----------


def _main_report_grid(
    rec: Recommendation,
    theme: Mapping[str, Any],
    *,
    created_short: str,
    on_back_recommendation: Callable[[ft.ControlEvent], None],
    on_back_history: Callable[[ft.ControlEvent], None],
    on_dashboard: Optional[Callable[[ft.ControlEvent], None]] = None,
    on_copy_summary: Optional[Callable[[ft.ControlEvent], None]] = None,
    on_feedback: Optional[Callable[[ft.ControlEvent], None]] = None,
    on_submit_feedback: Optional[Callable[[ft.ControlEvent], None]] = None,
    existing_feedback: Optional[RecommendationFeedback] = None,
    feedback_section_ref: Optional[ft.Ref[ft.Container]] = None,
    feedback_rating_ref: Optional[ft.Ref[ft.RadioGroup]] = None,
    feedback_comment_ref: Optional[ft.Ref[ft.TextField]] = None,
    feedback_error_ref: Optional[ft.Ref[ft.Text]] = None,
    feedback_success_ref: Optional[ft.Ref[ft.Text]] = None,
) -> ft.Control:
    left_sections = _left_column_sections(rec, theme)
    right_sections = _right_column_sections(
        rec,
        theme,
        created_short=created_short,
        on_back_recommendation=on_back_recommendation,
        on_back_history=on_back_history,
        on_dashboard=on_dashboard,
        on_copy_summary=on_copy_summary,
        on_feedback=on_feedback,
        on_submit_feedback=on_submit_feedback,
        existing_feedback=existing_feedback,
        feedback_section_ref=feedback_section_ref,
        feedback_rating_ref=feedback_rating_ref,
        feedback_comment_ref=feedback_comment_ref,
        feedback_error_ref=feedback_error_ref,
        feedback_success_ref=feedback_success_ref,
    )

    return ft.ResponsiveRow(
        spacing=_SECTION_GAP,
        run_spacing=_SECTION_GAP,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[
            ft.Container(
                col={"xs": 12, "lg": 8},
                content=ft.Column(spacing=_CARD_GAP, controls=left_sections),
            ),
            ft.Container(
                col={"xs": 12, "lg": 4},
                content=ft.Column(spacing=_CARD_GAP, controls=right_sections),
            ),
        ],
    )


def _left_column_sections(rec: Recommendation, theme: Mapping[str, Any]) -> list[ft.Control]:
    sections: list[ft.Control] = []
    expl = rec.explanation or {}

    explanation = _explanation_card(rec, theme)
    if explanation is not None:
        sections.append(explanation)

    alternatives = _alternatives_card(rec)
    if alternatives is not None:
        sections.append(alternatives)

    risks = _risk_tradeoffs_card(expl)
    if risks is not None:
        sections.append(risks)

    roadmap = _roadmap_card(expl.get("roadmap") or [])
    if roadmap is not None:
        sections.append(roadmap)

    if not sections:
        sections.append(
            _glass_card(
                ft.Text(
                    "No extended explanation is available for this record.",
                    size=14,
                    color=_C_SECONDARY,
                ),
            )
        )

    return sections


def _right_column_sections(
    rec: Recommendation,
    theme: Mapping[str, Any],
    *,
    created_short: str,
    on_back_recommendation: Callable[[ft.ControlEvent], None],
    on_back_history: Callable[[ft.ControlEvent], None],
    on_dashboard: Optional[Callable[[ft.ControlEvent], None]] = None,
    on_copy_summary: Optional[Callable[[ft.ControlEvent], None]] = None,
    on_feedback: Optional[Callable[[ft.ControlEvent], None]] = None,
    on_submit_feedback: Optional[Callable[[ft.ControlEvent], None]] = None,
    existing_feedback: Optional[RecommendationFeedback] = None,
    feedback_section_ref: Optional[ft.Ref[ft.Container]] = None,
    feedback_rating_ref: Optional[ft.Ref[ft.RadioGroup]] = None,
    feedback_comment_ref: Optional[ft.Ref[ft.TextField]] = None,
    feedback_error_ref: Optional[ft.Ref[ft.Text]] = None,
    feedback_success_ref: Optional[ft.Ref[ft.Text]] = None,
) -> list[ft.Control]:
    rw = recommendation_workspace_theme(theme)
    sections: list[ft.Control] = [
        _project_summary_card(rec),
        _confidence_breakdown_card(rec, theme),
    ]

    expl = rec.explanation or {}
    skills = [s for s in (expl.get("skill_gap_analysis") or []) if str(s).strip()]
    if skills:
        sections.append(_skill_gaps_card(skills))

    sections.append(
        _feedback_card(
            rw,
            existing_feedback=existing_feedback,
            section_ref=feedback_section_ref,
            rating_ref=feedback_rating_ref,
            comment_ref=feedback_comment_ref,
            error_ref=feedback_error_ref,
            success_ref=feedback_success_ref,
            on_submit=on_submit_feedback,
        )
    )

    sections.append(
        _quick_actions_card(
            on_generate_another=on_back_recommendation,
            on_dashboard=on_dashboard,
            on_history=on_back_history,
            on_copy_summary=on_copy_summary,
            on_feedback=on_feedback,
        )
    )
    sections.append(_metadata_card(rec, created_short=created_short))
    return sections


# ---------- left column cards ----------


def _explanation_card(rec: Recommendation, theme: Mapping[str, Any]) -> Optional[ft.Control]:
    expl = rec.explanation or {}
    summary = str(expl.get("summary", "")).strip()
    why_blocks = _why_subsections(expl)

    if not summary and not why_blocks:
        return None

    parts: list[ft.Control] = []
    if summary:
        parts.append(
            ft.Text(summary, size=14, color=_C_SECONDARY, selectable=True),
        )
    if why_blocks:
        parts.append(ft.Column(spacing=14, controls=why_blocks))

    body = ft.Column(
        spacing=14,
        controls=[
            _section_title("Explanation"),
            *parts,
        ],
    )
    return _glass_card(body)


def _why_subsections(expl: dict) -> list[ft.Control]:
    items: list[ft.Control] = []
    for key in ("why_language", "why_framework", "why_sdlc"):
        section = expl.get(key) or {}
        title = section.get("title")
        points = section.get("points") or []
        if not title or not points:
            continue
        items.append(
            ft.Column(
                spacing=8,
                tight=True,
                controls=[
                    ft.Text(title, size=14, weight=ft.FontWeight.W_600, color=_C_PRIMARY),
                    ft.Column(spacing=6, controls=[_bullet(p) for p in points]),
                ],
            )
        )
    return items


def _bullet(text: str) -> ft.Control:
    return ft.Row(
        spacing=10,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[
            ft.Container(
                width=6,
                height=6,
                border_radius=999,
                bgcolor=_C_CYAN,
                margin=ft.margin.only(top=7),
            ),
            ft.Text(text, size=13, color=_C_SECONDARY, expand=True),
        ],
    )


def _alternatives_card(rec: Recommendation) -> Optional[ft.Control]:
    expl = rec.explanation or {}
    alts = rec.alternatives or {}

    panels: list[ft.Control] = []
    for title_key, alt_key, label in (
        ("why_not_languages", "languages", "Languages"),
        ("why_not_frameworks", "frameworks", "Frameworks"),
        ("why_not_sdlc", "sdlc", "SDLC Models"),
    ):
        panel = _alternative_panel(expl, alts, title_key, alt_key, label)
        if panel is not None:
            panels.append(ft.Container(col={"xs": 12, "md": 4}, content=panel))

    if not panels:
        return None

    body = ft.Column(
        spacing=14,
        controls=[
            _section_title(
                "Alternatives considered",
                subtitle="Runners-up and why they scored lower for this profile.",
            ),
            ft.ResponsiveRow(spacing=_CARD_GAP, run_spacing=_CARD_GAP, controls=panels),
        ],
    )
    return _glass_card(body)


def _alternative_panel(
    expl: dict,
    alts: dict,
    title_key: str,
    alt_key: str,
    label: str,
) -> Optional[ft.Control]:
    runners = expl.get(title_key) or []
    if not runners and not (alts.get(alt_key) or [])[1:]:
        return None
    if not runners:
        return None

    rows = [
        _alternative_row(runner.get("name", ""), runner.get("reason", ""))
        for runner in runners[:4]
    ]

    return ft.Column(
        spacing=10,
        controls=[
            ft.Text(label.upper(), size=11, weight=ft.FontWeight.W_700, color=_C_MUTED),
            ft.Column(spacing=8, controls=rows),
        ],
    )


def _alternative_row(name: str, reason: str) -> ft.Control:
    score_hint = _score_hint_from_reason(reason)
    subtitle_controls: list[ft.Control] = []
    if score_hint:
        subtitle_controls.append(
            ft.Text(score_hint, size=11, color=_C_CYAN, weight=ft.FontWeight.W_600),
        )
    subtitle_controls.append(
        ft.Text(reason, size=12, color=_C_SECONDARY, max_lines=4),
    )

    return _inner_card(
        ft.Column(
            spacing=4,
            tight=True,
            controls=[
                ft.Text(name, size=13, weight=ft.FontWeight.W_700, color=_C_PRIMARY),
                *subtitle_controls,
            ],
        ),
        padding=12,
    )


def _score_hint_from_reason(reason: str) -> Optional[str]:
    match = re.search(r"scored\s+([\d.]+)\s+vs\s+([\d.]+)", reason, re.IGNORECASE)
    if not match:
        return None
    return f"Score {match.group(1)} vs {match.group(2)}"


def _risk_tradeoffs_card(expl: dict) -> Optional[ft.Control]:
    trade = list(expl.get("trade_offs") or [])
    risk = list(expl.get("risk_analysis") or [])
    combined: list[str] = []
    seen: set[str] = set()
    for item in trade + risk:
        text = str(item).strip()
        if text and text not in seen:
            seen.add(text)
            combined.append(text)
    if not combined:
        return None

    warning_body = ft.Container(
        padding=14,
        border_radius=14,
        bgcolor=_C_RISK_BG,
        border=ft.border.all(1, _C_RISK_BD),
        content=ft.Column(
            spacing=8,
            controls=[_risk_bullet(t) for t in combined],
        ),
    )

    body = ft.Column(
        spacing=12,
        controls=[
            ft.Row(
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.icons.WARNING_AMBER_OUTLINED, size=18, color=_C_WARNING),
                    ft.Text("Risk / trade-offs", size=17, weight=ft.FontWeight.W_600, color=_C_PRIMARY),
                ],
            ),
            warning_body,
        ],
    )
    return _glass_card(body)


def _risk_bullet(text: str) -> ft.Control:
    return ft.Row(
        spacing=10,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[
            ft.Icon(ft.icons.CIRCLE, size=8, color=_C_WARNING),
            ft.Text(text, size=13, color=_C_SECONDARY, expand=True),
        ],
    )


def _roadmap_card(items: list) -> Optional[ft.Control]:
    steps: list[str] = []
    for item in items:
        if isinstance(item, dict):
            title = str(item.get("title", "") or "").strip()
            desc = str(item.get("description", "") or "").strip()
            if title and desc:
                steps.append(f"{title}: {desc}")
            elif title:
                steps.append(title)
            elif desc:
                steps.append(desc)
        elif str(item).strip():
            steps.append(str(item).strip())
    if not steps:
        return None

    rows: list[ft.Control] = []
    for idx, step in enumerate(steps):
        label, body = _parse_roadmap_step(step, idx)
        is_last = idx == len(steps) - 1
        rows.append(_timeline_row(label, body, is_last=is_last))

    content = ft.Column(
        spacing=14,
        controls=[
            _section_title(
                "Suggested roadmap / next steps",
                subtitle="A practical delivery sequence for this project.",
            ),
            ft.Column(spacing=0, controls=rows),
        ],
    )
    return _glass_card(content)


def _parse_roadmap_step(step: str, index: int) -> tuple[str, str]:
    if ":" in step:
        head, tail = step.split(":", 1)
        return head.strip(), tail.strip()
    defaults = ("Week 1", "Week 2", "Week 3", "Week 4+")
    label = defaults[index] if index < len(defaults) else f"Step {index + 1}"
    return label, step


def _timeline_row(label: str, body: str, *, is_last: bool) -> ft.Control:
    dot = ft.Container(
        width=10,
        height=10,
        border_radius=999,
        bgcolor=_C_CYAN,
    )
    rail_controls: list[ft.Control] = [dot]
    if not is_last:
        rail_controls.append(ft.Container(width=2, height=36, bgcolor=ft.colors.with_opacity(0.3, _C_CYAN)))

    rail = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=rail_controls,
        width=18,
    )
    content = ft.Column(
        spacing=4,
        controls=[
            ft.Text(label, size=13, weight=ft.FontWeight.W_700, color=_C_CYAN),
            ft.Text(body, size=13, color=_C_SECONDARY),
        ],
        expand=True,
    )
    return ft.Container(
        padding=ft.padding.only(bottom=12 if not is_last else 0),
        content=ft.Row(
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[rail, content],
        ),
    )


# ---------- right column cards ----------


def _display_value(value: Any) -> str:
    if value is None:
        return "Not available"
    text = str(value).strip()
    if not text or text == "-":
        return "Not available"
    return text


def _format_selected_features(profile: dict) -> str:
    raw = profile.get("selected_features")
    if raw is None:
        return "Not available"
    if isinstance(raw, str):
        features = [part.strip() for part in raw.replace("|", ",").split(",") if part.strip()]
    elif isinstance(raw, list):
        features = [str(item).strip() for item in raw if str(item).strip()]
    else:
        return "Not available"
    return ", ".join(features) if features else "Not available"


def _project_summary_card(rec: Recommendation) -> ft.Control:
    profile = rec.project_profile or {}
    fields: list[tuple[str, str]] = [
        ("Project Name", _display_value(rec.project_name)),
        ("Project Type", _display_value(rec.project_type)),
        ("Selected Features", _format_selected_features(profile)),
        ("Team Size", _display_value(rec.team_size)),
        ("Complexity", _display_value(rec.complexity)),
        ("Preferred Platform", _display_value(profile.get("preferred_platform") or rec.platform)),
        ("Development Experience", _display_value(profile.get("development_experience") or rec.experience)),
        ("Timeline", _display_value(rec.timeline)),
        ("Project Goal", _display_value(profile.get("project_goal") or rec.project_goal)),
        ("Scalability Needs", _display_value(profile.get("scalability_needs") or rec.scalability)),
        ("Security Requirements", _display_value(profile.get("security_requirements") or rec.security)),
        ("Performance Requirements", _display_value(profile.get("performance_requirements"))),
        ("Budget Constraints", _display_value(profile.get("budget_constraints"))),
        ("Maintenance Expectations", _display_value(profile.get("maintenance_expectations"))),
        ("Deployment Preference", _display_value(profile.get("deployment_preference"))),
    ]

    kv_controls = [
        ft.Container(
            col={"xs": 12, "sm": 6},
            content=_summary_kv(label, value),
        )
        for label, value in fields
    ]

    body = ft.Column(
        spacing=12,
        controls=[
            _section_title(
                "Project Summary",
                subtitle="Core inputs saved with this recommendation.",
            ),
            ft.ResponsiveRow(spacing=10, run_spacing=6, controls=kv_controls),
        ],
    )
    return _glass_card(body)


def _summary_kv(label: str, value: str) -> ft.Control:
    return ft.Column(
        spacing=3,
        tight=True,
        controls=[
            ft.Text(label.upper(), size=10, weight=ft.FontWeight.W_700, color=_C_MUTED),
            ft.Text(
                value,
                size=13,
                weight=ft.FontWeight.W_600,
                color=_C_PRIMARY,
                max_lines=4,
            ),
        ],
    )


def _confidence_breakdown_card(rec: Recommendation, theme: Mapping[str, Any]) -> ft.Control:
    score = rec.confidence_score
    label = confidence_label(score)

    bands = [
        ("Very High", "85–100", score >= 85),
        ("High", "70–84", 70 <= score <= 84),
        ("Moderate", "50–69", 50 <= score <= 69),
        ("Low", "0–49", score < 50),
    ]
    band_rows = [
        ft.Row(
            spacing=8,
            controls=[
                ft.Text(name, size=12, color=_C_MUTED, width=72),
                ft.Text(range_txt, size=12, color=_C_SECONDARY, width=52),
                ft.Icon(
                    ft.icons.CHECK_CIRCLE if active else ft.icons.RADIO_BUTTON_UNCHECKED,
                    size=14,
                    color=_C_CYAN if active else _C_MUTED,
                ),
            ],
        )
        for name, range_txt, active in bands
    ]

    body = ft.Column(
        spacing=12,
        controls=[
            _section_title("Confidence breakdown"),
            confidence_bar(score, theme=theme),
            ft.Text(f"Rated {label} for this project profile.", size=13, color=_C_SECONDARY),
            ft.Column(spacing=6, controls=band_rows),
        ],
    )
    return _glass_card(body)


def _feedback_card(
    theme: Mapping[str, Any],
    *,
    existing_feedback: Optional[RecommendationFeedback],
    section_ref: Optional[ft.Ref[ft.Container]],
    rating_ref: Optional[ft.Ref[ft.RadioGroup]],
    comment_ref: Optional[ft.Ref[ft.TextField]],
    error_ref: Optional[ft.Ref[ft.Text]],
    success_ref: Optional[ft.Ref[ft.Text]],
    on_submit: Optional[Callable[[ft.ControlEvent], None]] = None,
) -> ft.Control:
    if existing_feedback is not None:
        body = ft.Column(
            spacing=10,
            controls=[
                _section_title(
                    "Your feedback",
                    subtitle="Thank you for rating this recommendation.",
                ),
                ft.Text(
                    _rating_stars_label(existing_feedback.rating),
                    size=18,
                    color=_C_CYAN,
                    weight=ft.FontWeight.W_600,
                ),
                ft.Text(
                    existing_feedback.comment or "No comment provided.",
                    size=13,
                    color=_C_SECONDARY,
                    selectable=True,
                ),
                ft.Text(
                    f"Submitted {humanize(existing_feedback.created_at)}",
                    size=12,
                    color=_C_MUTED,
                ),
            ],
        )
        return ft.Container(
            key="recommendation_feedback_section",
            ref=section_ref,
            visible=True,
            content=_glass_card(body, padding=20),
        )

    error_text = ft.Text(
        "",
        size=12,
        color=_C_WARNING,
        ref=error_ref,
        visible=False,
    )
    success_text = ft.Text(
        "",
        size=12,
        color=_C_CYAN,
        ref=success_ref,
        visible=False,
    )
    rating_group = ft.RadioGroup(
        ref=rating_ref,
        value=None,
        content=ft.Row(
            spacing=6,
            wrap=True,
            controls=[
                ft.Radio(value=str(n), label=f"{n} ★", label_style=ft.TextStyle(size=12, color=_C_SECONDARY))
                for n in range(1, 6)
            ],
        ),
    )
    comment_field = input_field(
        "Comment (optional)",
        hint="What was helpful or what could be improved?",
        multiline=True,
        min_lines=2,
        max_lines=4,
        theme=theme,
    )
    comment_field.ref = comment_ref

    submit_btn = (
        primary_button(
            "Submit Feedback",
            on_click=on_submit,
            icon=ft.icons.SEND_ROUNDED,
            theme=theme,
            mint_fill=True,
            border_radius=Radii.pill,
            expand=True,
        )
        if on_submit is not None
        else ft.Container()
    )

    form_body = ft.Column(
        spacing=12,
        controls=[
            _section_title(
                "Rate this recommendation",
                subtitle="Your rating helps improve future decision reports.",
            ),
            ft.Text("Rating *", size=12, weight=ft.FontWeight.W_600, color=_C_MUTED),
            rating_group,
            comment_field,
            submit_btn,
            error_text,
            success_text,
        ],
    )

    return ft.Container(
        key="recommendation_feedback_section",
        ref=section_ref,
        visible=False,
        content=_glass_card(form_body, padding=20),
    )


def _rating_stars_label(rating: int) -> str:
    rating = max(1, min(5, int(rating)))
    return f"{'★' * rating}{'☆' * (5 - rating)}  ({rating}/5)"


def _skill_gaps_card(skills: list[str]) -> ft.Control:
    body = ft.Column(
        spacing=10,
        controls=[
            _section_title("Skill gaps & learning notes"),
            ft.Column(spacing=6, controls=[_bullet(s) for s in skills]),
        ],
    )
    return _glass_card(body)


def _quick_actions_card(
    *,
    on_generate_another: Callable[[ft.ControlEvent], None],
    on_history: Callable[[ft.ControlEvent], None],
    on_dashboard: Optional[Callable[[ft.ControlEvent], None]] = None,
    on_copy_summary: Optional[Callable[[ft.ControlEvent], None]] = None,
    on_feedback: Optional[Callable[[ft.ControlEvent], None]] = None,
) -> ft.Control:
    buttons: list[ft.Control] = [
        _compact_action("Generate Another", ft.icons.AUTO_AWESOME, on_generate_another, primary=True),
    ]
    if on_dashboard is not None:
        buttons.append(_compact_action("View Dashboard", ft.icons.DASHBOARD_OUTLINED, on_dashboard))
    buttons.append(_compact_action("View History", ft.icons.HISTORY, on_history))
    if on_copy_summary is not None:
        buttons.append(_compact_action("Copy Summary", ft.icons.CONTENT_COPY_OUTLINED, on_copy_summary))
    if on_feedback is not None:
        buttons.append(_compact_action("Submit Feedback", ft.icons.RATE_REVIEW_OUTLINED, on_feedback))

    return _glass_card(
        ft.Column(
            spacing=10,
            tight=True,
            controls=[
                _section_title("Quick actions"),
                *buttons,
            ],
        ),
        padding=20,
    )


def _metadata_card(rec: Recommendation, *, created_short: str) -> ft.Control:
    created_rel = humanize(rec.created_at) if rec.created_at else "—"
    rows = [
        ("Report ID", f"#{rec.id}"),
        ("Created", f"{created_short} ({created_rel})"),
        ("Language", rec.recommended_language),
        ("Framework", rec.recommended_framework),
        ("SDLC", rec.recommended_sdlc),
    ]

    body = ft.Column(
        spacing=10,
        controls=[
            _section_title("Report metadata"),
            ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(k, size=12, color=_C_MUTED, width=88),
                            ft.Text(v, size=12, weight=ft.FontWeight.W_600, color=_C_PRIMARY, expand=True),
                        ],
                    )
                    for k, v in rows
                ],
            ),
        ],
    )
    return _glass_card(body)
