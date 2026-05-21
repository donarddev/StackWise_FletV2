"""Full decision report UI for session-stored recommendation engine output (Phase 4)."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Callable, Mapping, Optional

import flet as ft

from app.utils.constants import confidence_label
from ui.components.confidence_bar import confidence_bar
from ui.components.empty_state import empty_state
from ui.components.primary_button import primary_button
from ui.pages.recommendation_page import recommendation_workspace_theme
from ui.themes.app_theme import Radii, Spacing

# Dark glass tokens (aligned with recommendation_result_page)
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

_DEFAULT_ROADMAP: list[tuple[str, str]] = [
    ("Week 1", "Finalize scope and database structure"),
    ("Week 2", "Implement authentication and core CRUD"),
    ("Week 3", "Add reports, dashboard, and validation"),
    ("Week 4", "Testing, documentation, and deployment preparation"),
]


def build_session_summary_clipboard_text(
    result: dict[str, Any],
    input_data: dict[str, Any],
) -> str:
    """Plain-text summary for Copy Summary from session report."""
    score = _confidence_int(result)
    label = str(result.get("confidence_label", "") or confidence_label(score))
    lines = [
        f"Project: {input_data.get('project_name', '')}",
        f"Project type: {input_data.get('project_type', '')}",
        f"Recommended language: {result.get('recommended_language', '')}",
        f"Recommended framework: {result.get('recommended_framework', '')}",
        f"Recommended SDLC: {result.get('recommended_sdlc', '')}",
        f"Confidence: {score}% ({label})",
        "",
    ]
    expl = str(result.get("explanation", "") or "").strip()
    if expl:
        lines.extend(["Explanation", expl, ""])
    for item in result.get("risks") or []:
        if str(item).strip():
            lines.append(f"Risk: {item}")
    if result.get("risks"):
        lines.append("")
    for item in result.get("skill_gaps") or []:
        if str(item).strip():
            lines.append(f"Skill gap: {item}")
    if result.get("skill_gaps"):
        lines.append("")
    for step in _roadmap_steps(result):
        lines.append(f"{step[0]}: {step[1]}")
    return "\n".join(lines).strip()


def build_session_recommendation_report(
    *,
    result: Optional[dict[str, Any]],
    input_data: Optional[dict[str, Any]],
    theme: Mapping[str, Any],
    generated_label: str,
    on_back_recommendation: Callable[[ft.ControlEvent], None],
    on_back_history: Callable[[ft.ControlEvent], None],
    on_copy_summary: Optional[Callable[[ft.ControlEvent], None]],
    on_regenerate: Optional[Callable[[ft.ControlEvent], None]],
    on_dashboard: Optional[Callable[[ft.ControlEvent], None]],
) -> ft.Control:
    """Full professional decision report from page.session engine output."""
    rw = recommendation_workspace_theme(theme)
    inp = input_data or {}

    if not result:
        return ft.Container(
            padding=ft.padding.all(_PAGE_PAD),
            content=empty_state(
                icon=ft.icons.SEARCH_OFF_OUTLINED,
                title="No recommendation result found",
                description="Generate a new recommendation from the project profile form.",
                action=primary_button(
                    "Back to Recommendation",
                    on_click=on_back_recommendation,
                    icon=ft.icons.ARROW_BACK,
                    theme=rw,
                    mint_fill=True,
                    border_radius=Radii.pill,
                ),
                theme=rw,
            ),
        )

    score = _confidence_int(result)
    conf_lbl = str(result.get("confidence_label", "") or confidence_label(score))

    content = ft.Column(
        spacing=_SECTION_GAP,
        controls=[
            _session_hero_card(
                result,
                inp,
                score=score,
                conf_label=conf_lbl,
                generated_label=generated_label,
                on_back_recommendation=on_back_recommendation,
                on_back_history=on_back_history,
                on_copy_summary=on_copy_summary,
                on_regenerate=on_regenerate,
            ),
            _session_summary_card(result, score=score, conf_label=conf_lbl),
            ft.ResponsiveRow(
                spacing=_SECTION_GAP,
                run_spacing=_SECTION_GAP,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Container(
                        col={"xs": 12, "lg": 8},
                        content=ft.Column(
                            spacing=_CARD_GAP,
                            controls=[
                                _session_explanation_card(result),
                                _session_alternatives_card(result),
                                _session_risks_card(result, inp),
                                _session_roadmap_card(result),
                            ],
                        ),
                    ),
                    ft.Container(
                        col={"xs": 12, "lg": 4},
                        content=ft.Column(
                            spacing=_CARD_GAP,
                            controls=[
                                _session_profile_card(inp),
                                _session_confidence_card(result, score, theme=rw),
                                _session_skill_gaps_card(result),
                                _session_quick_actions_card(
                                    on_generate_another=on_back_recommendation,
                                    on_dashboard=on_dashboard,
                                    on_history=on_back_history,
                                    on_copy_summary=on_copy_summary,
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        ],
    )

    return ft.Container(
        padding=ft.padding.symmetric(horizontal=_PAGE_PAD, vertical=_PAGE_PAD - 4),
        content=content,
    )


# ---------- helpers ----------


def _confidence_int(result: dict[str, Any]) -> int:
    try:
        score = int(round(float(result.get("confidence_score", 0))))
    except (TypeError, ValueError):
        score = 0
    return max(0, min(100, score))


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
                ft.Text(
                    "DECISION REPORT",
                    size=10,
                    weight=ft.FontWeight.W_700,
                    color=_C_CYAN,
                ),
            ],
            spacing=6,
            tight=True,
        ),
        bgcolor=ft.colors.with_opacity(0.1, _C_CYAN),
        border=ft.border.all(1, ft.colors.with_opacity(0.35, _C_CYAN)),
        border_radius=Radii.pill,
        padding=ft.padding.symmetric(horizontal=10, vertical=5),
    )


def _confidence_pill(score: int, label: str) -> ft.Control:
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
            ft.Text(text, size=13, color=_C_SECONDARY, expand=True, selectable=True),
        ],
    )


def _display(value: Any, *, default: str = "Not specified") -> str:
    if value is None:
        return default
    if isinstance(value, list):
        parts = [str(v).strip() for v in value if str(v).strip()]
        return ", ".join(parts) if parts else default
    text = str(value).strip()
    return text if text else default


def _parse_explanation(text: str) -> tuple[str, list[tuple[str, str]]]:
    """Split engine explanation into summary and why-blocks."""
    raw = (text or "").strip()
    if not raw:
        return "", []

    whys: list[tuple[str, str]] = []
    markers = (
        ("Why this language", "Language:"),
        ("Why this framework", "Framework:"),
        ("Why this SDLC model", "SDLC:"),
    )
    summary_parts: list[str] = []
    for block in re.split(r"\n\s*\n", raw):
        block = block.strip()
        if not block:
            continue
        matched = False
        for title, prefix in markers:
            if block.startswith(prefix):
                whys.append((title, block))
                matched = True
                break
        if not matched:
            summary_parts.append(block)

    summary = "\n\n".join(summary_parts).strip()
    return summary, whys


def _roadmap_steps(result: dict[str, Any]) -> list[tuple[str, str]]:
    raw = result.get("roadmap") or []
    steps: list[tuple[str, str]] = []
    for item in raw:
        if isinstance(item, dict):
            title = str(item.get("title", "") or item.get("phase", "")).strip()
            body = str(item.get("description", "")).strip()
            if title or body:
                steps.append((title or f"Step {len(steps) + 1}", body))
        elif isinstance(item, str) and item.strip():
            if ":" in item:
                head, tail = item.split(":", 1)
                steps.append((head.strip(), tail.strip()))
            else:
                steps.append((f"Step {len(steps) + 1}", item.strip()))
    if steps:
        return steps
    return list(_DEFAULT_ROADMAP)


def _alternatives_list(result: dict[str, Any], key: str) -> list[dict[str, Any]]:
    items = result.get(key) or []
    if not isinstance(items, list):
        return []
    return [x for x in items if isinstance(x, dict) and str(x.get("name", "")).strip()]


# ---------- section cards ----------


def _session_hero_card(
    result: dict[str, Any],
    inp: dict[str, Any],
    *,
    score: int,
    conf_label: str,
    generated_label: str,
    on_back_recommendation: Callable[[ft.ControlEvent], None],
    on_back_history: Callable[[ft.ControlEvent], None],
    on_copy_summary: Optional[Callable[[ft.ControlEvent], None]],
    on_regenerate: Optional[Callable[[ft.ControlEvent], None]],
) -> ft.Control:
    project_name = _display(inp.get("project_name"), default="Your project")
    project_type = _display(inp.get("project_type"))
    complexity = _display(inp.get("complexity"))
    subtitle = f"{project_type} · {complexity} · {generated_label}"

    left = ft.Column(
        spacing=12,
        tight=True,
        controls=[
            _details_badge(),
            ft.Text(
                "Recommendation Details",
                size=14,
                weight=ft.FontWeight.W_600,
                color=_C_MUTED,
            ),
            ft.Row(
                spacing=12,
                wrap=True,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        project_name,
                        size=28,
                        weight=ft.FontWeight.W_700,
                        color=_C_PRIMARY,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    _confidence_pill(score, conf_label),
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
                    ft.Container(
                        content=_hero_meta_chip("Project type", project_type),
                        expand=True,
                    ),
                    ft.Container(
                        content=_hero_meta_chip("Generated", generated_label),
                        expand=True,
                    ),
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


def _session_summary_card(
    result: dict[str, Any],
    *,
    score: int,
    conf_label: str,
) -> ft.Control:
    stat_row = ft.ResponsiveRow(
        spacing=_CARD_GAP,
        run_spacing=_CARD_GAP,
        controls=[
            ft.Container(
                col={"xs": 6, "sm": 3},
                content=_stat_tile("Programming Language", str(result.get("recommended_language", "—"))),
            ),
            ft.Container(
                col={"xs": 6, "sm": 3},
                content=_stat_tile("Framework", str(result.get("recommended_framework", "—"))),
            ),
            ft.Container(
                col={"xs": 6, "sm": 3},
                content=_stat_tile("SDLC Model", str(result.get("recommended_sdlc", "—"))),
            ),
            ft.Container(
                col={"xs": 6, "sm": 3},
                content=_stat_tile("Confidence", f"{score}% {conf_label}", large=True),
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
                "Recommendation Summary",
                subtitle="The strongest stack match based on your project profile.",
            ),
            stat_row,
            bar,
        ],
    )
    return _glass_card(body)


def _stat_tile(label: str, value: str, *, large: bool = False) -> ft.Control:
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


def _session_explanation_card(result: dict[str, Any]) -> ft.Control:
    summary, whys = _parse_explanation(str(result.get("explanation", "") or ""))
    parts: list[ft.Control] = []
    if summary:
        parts.append(ft.Text(summary, size=14, color=_C_SECONDARY, selectable=True))
    for title, body in whys:
        parts.append(
            ft.Column(
                spacing=8,
                tight=True,
                controls=[
                    ft.Text(title, size=14, weight=ft.FontWeight.W_600, color=_C_PRIMARY),
                    ft.Text(body, size=13, color=_C_SECONDARY, selectable=True),
                ],
            )
        )
    if not parts:
        parts.append(
            ft.Text(
                "No detailed explanation was returned by the engine.",
                size=14,
                color=_C_SECONDARY,
            )
        )

    return _glass_card(
        ft.Column(
            spacing=14,
            controls=[_section_title("Explanation"), *parts],
        )
    )


def _session_alternatives_card(result: dict[str, Any]) -> ft.Control:
    panels: list[ft.Control] = []
    for key, label in (
        ("alternative_languages", "Languages"),
        ("alternative_frameworks", "Frameworks"),
        ("alternative_sdlc_models", "SDLC Models"),
    ):
        alts = _alternatives_list(result, key)
        if not alts:
            continue
        rows = [
            _alt_row(str(a.get("name", "")), str(a.get("reason", "") or ""), a.get("score"))
            for a in alts[:4]
        ]
        panels.append(
            ft.Container(
                col={"xs": 12, "md": 4},
                content=ft.Column(
                    spacing=10,
                    controls=[
                        ft.Text(label.upper(), size=11, weight=ft.FontWeight.W_700, color=_C_MUTED),
                        ft.Column(spacing=8, controls=rows),
                    ],
                ),
            )
        )

    if not panels:
        body = ft.Column(
            spacing=10,
            controls=[
                _section_title("Alternatives considered"),
                ft.Text(
                    "No alternative details available yet.",
                    size=14,
                    color=_C_SECONDARY,
                ),
            ],
        )
        return _glass_card(body)

    return _glass_card(
        ft.Column(
            spacing=14,
            controls=[
                _section_title(
                    "Alternatives considered",
                    subtitle="Runners-up and why they scored lower for this profile.",
                ),
                ft.ResponsiveRow(spacing=_CARD_GAP, run_spacing=_CARD_GAP, controls=panels),
            ],
        )
    )


def _alt_row(name: str, reason: str, score: Any) -> ft.Control:
    subtitle_controls: list[ft.Control] = []
    if score is not None:
        try:
            subtitle_controls.append(
                ft.Text(
                    f"Score {float(score):.1f}",
                    size=11,
                    color=_C_CYAN,
                    weight=ft.FontWeight.W_600,
                )
            )
        except (TypeError, ValueError):
            pass
    if reason:
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


def _session_risks_card(result: dict[str, Any], inp: dict[str, Any]) -> ft.Control:
    risks = [str(r).strip() for r in (result.get("risks") or []) if str(r).strip()]
    if not risks:
        risks = _derived_risk_notes(inp, result)

    warning_body = ft.Container(
        padding=14,
        border_radius=14,
        bgcolor=_C_RISK_BG,
        border=ft.border.all(1, _C_RISK_BD),
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Icon(ft.icons.CIRCLE, size=8, color=_C_WARNING),
                        ft.Text(r, size=13, color=_C_SECONDARY, expand=True),
                    ],
                )
                for r in risks
            ],
        ),
    )

    return _glass_card(
        ft.Column(
            spacing=12,
            controls=[
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.icons.WARNING_AMBER_OUTLINED, size=18, color=_C_WARNING),
                        ft.Text(
                            "Risk / trade-offs",
                            size=17,
                            weight=ft.FontWeight.W_600,
                            color=_C_PRIMARY,
                        ),
                    ],
                ),
                warning_body,
            ],
        )
    )


def _derived_risk_notes(inp: dict[str, Any], result: dict[str, Any]) -> list[str]:
    """Display-only notes from saved input/result — no scoring changes."""
    notes: list[str] = []
    timeline = str(inp.get("timeline", "") or "")
    complexity = str(inp.get("complexity", "") or "")
    stability = str(inp.get("requirements_stability", "") or "")
    if "short" in timeline.lower() or "less than" in timeline.lower():
        notes.append(
            "A short timeline raises incomplete-feature and reduced-testing risk."
        )
    if "chang" in stability.lower():
        notes.append(
            "Changing requirements increase scope-creep risk without iterative feedback."
        )
    if complexity.lower() in ("high", "very high"):
        notes.append(
            "Higher complexity increases coordination and delivery risk for the team."
        )
    note = str(result.get("validation_note", "") or "").strip()
    if note:
        notes.append(note)
    if not notes:
        notes.append(
            "No major risks flagged; maintain code review, testing, and documentation discipline."
        )
    return notes


def _session_skill_gaps_card(result: dict[str, Any]) -> ft.Control:
    gaps = [str(g).strip() for g in (result.get("skill_gaps") or []) if str(g).strip()]
    if not gaps:
        body_text = "No major skill gaps detected from the current input."
        gap_controls: list[ft.Control] = [
            ft.Text(body_text, size=14, color=_C_SECONDARY),
        ]
    else:
        gap_controls = [_bullet(g) for g in gaps]

    return _glass_card(
        ft.Column(
            spacing=10,
            controls=[
                _section_title("Skill gaps & learning notes"),
                *gap_controls,
            ],
        )
    )


def _session_roadmap_card(result: dict[str, Any]) -> ft.Control:
    steps = _roadmap_steps(result)
    rows: list[ft.Control] = []
    for idx, (label, body) in enumerate(steps):
        is_last = idx == len(steps) - 1
        rows.append(_timeline_row(label, body, is_last=is_last))

    return _glass_card(
        ft.Column(
            spacing=14,
            controls=[
                _section_title(
                    "Suggested roadmap / next steps",
                    subtitle="A practical delivery sequence for this project.",
                ),
                ft.Column(spacing=0, controls=rows),
            ],
        )
    )


def _timeline_row(label: str, body: str, *, is_last: bool) -> ft.Control:
    dot = ft.Container(width=10, height=10, border_radius=999, bgcolor=_C_CYAN)
    rail_controls: list[ft.Control] = [dot]
    if not is_last:
        rail_controls.append(
            ft.Container(width=2, height=36, bgcolor=ft.colors.with_opacity(0.3, _C_CYAN))
        )
    rail = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=rail_controls,
        width=18,
    )
    content = ft.Column(
        spacing=4,
        controls=[
            ft.Text(label, size=13, weight=ft.FontWeight.W_700, color=_C_CYAN),
            ft.Text(body, size=13, color=_C_SECONDARY, selectable=True),
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


def _session_profile_card(inp: dict[str, Any]) -> ft.Control:
    fields: list[tuple[str, str]] = [
        ("Project type", _display(inp.get("project_type"))),
        ("Goal", _display(inp.get("project_goal"))),
        ("Complexity", _display(inp.get("complexity"))),
        ("Team size", _display(inp.get("team_size"))),
        ("Timeline", _display(inp.get("timeline"))),
        ("Requirements stability", _display(inp.get("requirements_stability"))),
        ("Stakeholder involvement", _display(inp.get("stakeholder_involvement"))),
        ("Scalability", _display(inp.get("scalability_needs"))),
        ("Performance", _display(inp.get("performance_requirements"))),
        ("Security", _display(inp.get("security_requirements"))),
        ("Budget", _display(inp.get("budget_constraints"))),
        ("Platform", _display(inp.get("preferred_platform"))),
        ("Development experience", _display(inp.get("development_experience"))),
        ("Deployment", _display(inp.get("deployment_preference"))),
        ("Maintenance", _display(inp.get("maintenance_expectations"))),
        ("Selected features", _display(inp.get("selected_features"), default="None selected")),
    ]

    kv_controls = [
        ft.Container(
            col={"xs": 12, "sm": 6},
            content=_profile_kv(label, value),
        )
        for label, value in fields
    ]

    return _glass_card(
        ft.Column(
            spacing=12,
            controls=[
                _section_title(
                    "Project profile",
                    subtitle="Inputs used for this recommendation.",
                ),
                ft.ResponsiveRow(spacing=10, run_spacing=6, controls=kv_controls),
            ],
        )
    )


def _profile_kv(label: str, value: str) -> ft.Control:
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


def _session_confidence_card(
    result: dict[str, Any],
    score: int,
    *,
    theme: Mapping[str, Any],
) -> ft.Control:
    label = str(result.get("confidence_label", "") or confidence_label(score))
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

    return _glass_card(
        ft.Column(
            spacing=12,
            controls=[
                _section_title("Confidence breakdown"),
                confidence_bar(score, theme=theme),
                ft.Text(f"Rated {label} for this project profile.", size=13, color=_C_SECONDARY),
                ft.Column(spacing=6, controls=band_rows),
            ],
        )
    )


def _session_quick_actions_card(
    *,
    on_generate_another: Callable[[ft.ControlEvent], None],
    on_history: Callable[[ft.ControlEvent], None],
    on_dashboard: Optional[Callable[[ft.ControlEvent], None]],
    on_copy_summary: Optional[Callable[[ft.ControlEvent], None]],
) -> ft.Control:
    buttons: list[ft.Control] = [
        _compact_action("Generate Another", ft.icons.AUTO_AWESOME, on_generate_another, primary=True),
    ]
    if on_dashboard is not None:
        buttons.append(_compact_action("View Dashboard", ft.icons.DASHBOARD_OUTLINED, on_dashboard))
    buttons.append(_compact_action("View History", ft.icons.HISTORY, on_history))
    if on_copy_summary is not None:
        buttons.append(
            _compact_action("Copy Summary", ft.icons.CONTENT_COPY_OUTLINED, on_copy_summary),
        )

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


def format_generated_label() -> str:
    """Human-readable generated timestamp for session reports."""
    return datetime.now().strftime("%b %d, %Y · %I:%M %p")
