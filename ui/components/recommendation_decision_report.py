"""Shared decision-report sections for recommendation details (display only)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Mapping, Optional

import flet as ft

from app.helpers.date_helper import humanize
from app.helpers.recommendation_engine_compat import (
    alternative_stacks_from_record,
    devops_support_note,
    engine_full_result_from_explanation,
    normalize_engine_result_for_ui,
    structured_risk_analysis,
    structured_roadmap_phases,
    structured_skill_gap_analysis,
    why_not_entries_sorted,
)
from app.models.recommendation import Recommendation
from app.models.recommendation_feedback import RecommendationFeedback
from app.utils.constants import confidence_label
from ui.components.input_field import input_field
from ui.components.primary_button import primary_button
from ui.components.toast import show_toast
from ui.themes.app_theme import Radii

# Dark glass tokens
_C_PRIMARY = "#F8FAFC"
_C_SECONDARY = "#AAB6C8"
_C_MUTED = "#72809A"
_C_CYAN = "#22D3EE"
_C_WARNING = "#F59E0B"
_C_SUCCESS = "#34D399"
_C_PURPLE = "#8B5CF6"
_C_PANEL = "#132033"
_C_PANEL_BD = "#2A3B55"
_C_INNER = "#101827"
_C_INNER_BD = "#24364F"
# Trade-off panels (alternatives) — unchanged green-teal family
_C_REASON_BG = "#0c2228"
_C_REASON_BD = "#1e4d56"
# Saved Recommendation nested cards — dashboard navy/cyan glass
_CARD_BG = "#101D2F"
_CARD_BG_SOFT = "#13243A"
_CARD_BG_ACCENT = "#12364A"
_CARD_BORDER = "#24415F"
_SAVED_CARD_BORDER_CYAN = 0.42
_C_ADV_LABEL = "#34D399"
_C_DISADV_LABEL = "#F472B6"

_PAGE_PAD = 40
_SECTION_GAP = 22
_CARD_GAP = 14
_INNER_PAD = 16
_PANEL_PAD = 22
_MAX_WIDTH = 1360

_GLASS_SHADOW = ft.BoxShadow(
    blur_radius=18,
    spread_radius=0,
    color="#00000030",
    offset=ft.Offset(0, 8),
)

_DISCLAIMER = (
    "This is a decision-support recommendation, not an absolute technology guarantee."
)

_HEADER_SUBTITLE = (
    "A full breakdown of the saved recommendation record for presentation, "
    "review, and class discussion."
)

_DEVOPS_UI_NOTE = (
    "DevOps support is useful for CI/CD, monitoring, cloud deployment, "
    "and production maintenance."
)

_MAX_ALTERNATIVE_ROWS = 4

# Why Not / Risk: gap; row wraps when content area is too narrow (e.g. expanded sidebar).
_WHY_RISK_GAP = 24

def _wrapping_action_row(
    controls: list[ft.Control],
    *,
    spacing: int = 8,
    center: bool = False,
) -> ft.Control:
    """Row with wrap — compatible with flet_core builds that lack ft.Wrap."""
    return ft.Row(
        spacing=spacing,
        wrap=True,
        alignment=ft.MainAxisAlignment.CENTER if center else ft.MainAxisAlignment.START,
        controls=controls,
    )


@dataclass
class DecisionReportData:
    """Normalized view-model for details/session pages (no scoring)."""

    project_name: str
    project_type: str
    complexity: str
    generated_label: str
    record_id: Optional[int] = None
    confidence_score: int = 0
    confidence_label: str = ""
    recommended_language: str = "—"
    recommended_framework: str = "—"
    recommended_sdlc: str = "—"
    language_reason: str = ""
    framework_reason: str = ""
    sdlc_reason: str = ""
    explanation_summary: str = ""
    why_language_points: list[str] = field(default_factory=list)
    why_framework_points: list[str] = field(default_factory=list)
    why_sdlc_points: list[str] = field(default_factory=list)
    alternative_stacks: list[dict[str, Any]] = field(default_factory=list)
    why_not_this: list[dict[str, Any]] = field(default_factory=list)
    risk_analysis: list[dict[str, Any]] = field(default_factory=list)
    skill_gap_analysis: list[dict[str, Any]] = field(default_factory=list)
    roadmap_phases: list[dict[str, Any]] = field(default_factory=list)
    user_preferred_stack: dict[str, Any] = field(default_factory=dict)
    scoring_basis: str = ""
    defense_explanation: str = ""
    validation_note: str = ""
    profile_fields: list[tuple[str, str]] = field(default_factory=list)
    reason_context: dict[str, Any] = field(default_factory=dict)


def report_data_from_recommendation(
    rec: Recommendation,
    *,
    created_short: str,
) -> DecisionReportData:
    expl = rec.explanation or {}
    snap = engine_full_result_from_explanation(expl)
    merged = {**snap, **{k: v for k, v in expl.items() if k != "engine_full_result"}}
    if snap:
        merged["risk_analysis"] = snap.get("risk_analysis") or expl.get("risk_analysis")
        merged["skill_gap_analysis"] = (
            snap.get("skill_gap_analysis") or expl.get("skill_gap_analysis")
        )
        merged["suggested_project_roadmap"] = (
            snap.get("suggested_project_roadmap")
            or snap.get("roadmap")
            or expl.get("roadmap")
        )

    score = max(0, min(100, int(rec.confidence_score)))
    lbl = str(expl.get("confidence_label", "") or confidence_label(score))

    lang_r = str(expl.get("language_reason", "") or snap.get("language_reason", "") or "")
    fw_r = str(expl.get("framework_reason", "") or snap.get("framework_reason", "") or "")
    sdlc_r = str(expl.get("sdlc_reason", "") or snap.get("sdlc_reason", "") or "")

    summary = str(expl.get("summary", "") or "").strip()
    why_lang, why_fw, why_sdlc = _why_points_from_explanation(expl)

    profile = rec.project_profile or {}
    fields = _profile_fields_from_rec(rec, profile)

    return DecisionReportData(
        project_name=rec.project_name or "Your project",
        project_type=rec.project_type or "—",
        complexity=rec.complexity or "—",
        generated_label=created_short,
        record_id=rec.id,
        confidence_score=score,
        confidence_label=lbl,
        recommended_language=rec.recommended_language or "—",
        recommended_framework=rec.recommended_framework or "—",
        recommended_sdlc=rec.recommended_sdlc or "—",
        language_reason=lang_r,
        framework_reason=fw_r,
        sdlc_reason=sdlc_r,
        explanation_summary=summary,
        why_language_points=why_lang or _text_to_points(lang_r),
        why_framework_points=why_fw or _text_to_points(fw_r),
        why_sdlc_points=why_sdlc or _text_to_points(sdlc_r),
        alternative_stacks=alternative_stacks_from_record(expl, rec.alternatives),
        why_not_this=why_not_entries_sorted(
            expl.get("why_not_this") or snap.get("why_not_this") or []
        ),
        risk_analysis=structured_risk_analysis(merged),
        skill_gap_analysis=structured_skill_gap_analysis(merged),
        roadmap_phases=structured_roadmap_phases(merged),
        user_preferred_stack=(
            expl.get("user_preferred_stack")
            if isinstance(expl.get("user_preferred_stack"), dict)
            else snap.get("user_preferred_stack") or {}
        ),
        scoring_basis=str(expl.get("scoring_basis", "") or snap.get("scoring_basis", "") or ""),
        defense_explanation=str(
            expl.get("defense_explanation", "") or snap.get("defense_explanation", "") or ""
        ),
        validation_note=str(
            expl.get("validation_note", "") or snap.get("validation_note", "") or ""
        ),
        profile_fields=fields,
        reason_context=_build_reason_context(profile=profile, rec=rec),
    )


def report_data_from_session(
    result: dict[str, Any],
    input_data: dict[str, Any],
    *,
    generated_label: str,
) -> DecisionReportData:
    result = normalize_engine_result_for_ui(result)
    inp = input_data or {}

    score = _confidence_int(result)
    lbl = str(result.get("confidence_label", "") or confidence_label(score))

    raw_expl = str(result.get("explanation", "") or "").strip()
    summary, parsed_whys = _parse_explanation_text(raw_expl)

    lang_r = str(result.get("language_reason", "") or "").strip()
    fw_r = str(result.get("framework_reason", "") or "").strip()
    sdlc_r = str(result.get("sdlc_reason", "") or "").strip()

    why_lang = _text_to_points(parsed_whys.get("language", lang_r))
    why_fw = _text_to_points(parsed_whys.get("framework", fw_r))
    why_sdlc = _text_to_points(parsed_whys.get("sdlc", sdlc_r))

    stacks = result.get("alternative_technology_stacks") or result.get("alternatives") or []
    if not isinstance(stacks, list):
        stacks = []
    stacks = [s for s in stacks if isinstance(s, dict)]

    return DecisionReportData(
        project_name=_display(inp.get("project_name"), default="Your project"),
        project_type=_display(inp.get("project_type")),
        complexity=_display(inp.get("complexity")),
        generated_label=generated_label,
        record_id=None,
        confidence_score=score,
        confidence_label=lbl,
        recommended_language=str(result.get("recommended_language", "—") or "—"),
        recommended_framework=str(result.get("recommended_framework", "—") or "—"),
        recommended_sdlc=str(result.get("recommended_sdlc", "—") or "—"),
        language_reason=lang_r,
        framework_reason=fw_r,
        sdlc_reason=sdlc_r,
        explanation_summary=summary,
        why_language_points=why_lang,
        why_framework_points=why_fw,
        why_sdlc_points=why_sdlc,
        alternative_stacks=stacks,
        why_not_this=why_not_entries_sorted(result.get("why_not_this") or []),
        risk_analysis=structured_risk_analysis(result),
        skill_gap_analysis=structured_skill_gap_analysis(result),
        roadmap_phases=structured_roadmap_phases(result),
        user_preferred_stack=(
            result.get("user_preferred_stack")
            if isinstance(result.get("user_preferred_stack"), dict)
            else {}
        ),
        scoring_basis=str(result.get("scoring_basis", "") or ""),
        defense_explanation=str(result.get("defense_explanation", "") or ""),
        validation_note=str(result.get("validation_note", "") or ""),
        profile_fields=_profile_fields_from_input(inp),
        reason_context=_build_reason_context(profile=inp, result=result),
    )


def build_decision_report_body(
    data: DecisionReportData,
    *,
    theme: Mapping[str, Any],
    on_back_recommendation: Callable[[ft.ControlEvent], None],
    on_back_history: Callable[[ft.ControlEvent], None],
    on_copy_summary: Optional[Callable[[ft.ControlEvent], None]] = None,
    on_copy_project_summary: Optional[Callable[[ft.ControlEvent], None]] = None,
    on_regenerate: Optional[Callable[[ft.ControlEvent], None]] = None,
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
    show_feedback: bool = False,
) -> ft.Control:
    rw = theme
    sections: list[ft.Control] = [
        build_details_header(data),
        build_summary_overview_row(
            data,
            on_copy_project_summary=_project_summary_copy_handler(
                data, on_copy_project_summary
            ),
        ),
    ]

    why_risk = build_why_not_risk_section(data)
    if why_risk is not None:
        sections.append(why_risk)

    skill_section = build_skill_gap_section(data)
    if skill_section is not None:
        sections.append(skill_section)

    roadmap_section = build_project_roadmap_section(data)
    if roadmap_section is not None:
        sections.append(roadmap_section)

    left_sections = _left_column(data, rw)
    if left_sections:
        sections.append(ft.Column(spacing=_CARD_GAP, controls=left_sections))

    footer = build_feedback_and_report_actions_section(
        rw,
        show_feedback=show_feedback,
        existing_feedback=existing_feedback,
        feedback_section_ref=feedback_section_ref,
        feedback_rating_ref=feedback_rating_ref,
        feedback_comment_ref=feedback_comment_ref,
        feedback_error_ref=feedback_error_ref,
        feedback_success_ref=feedback_success_ref,
        feedback_submit_btn_ref=feedback_submit_btn_ref,
        on_submit_feedback=on_submit_feedback,
        on_generate_another=on_back_recommendation,
        on_dashboard=on_dashboard,
        on_history=on_back_history,
        on_copy_summary=on_copy_summary,
    )
    if footer is not None:
        sections.append(footer)

    content = ft.Column(spacing=_SECTION_GAP, controls=sections)
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=_PAGE_PAD, vertical=_PAGE_PAD - 4),
        alignment=ft.alignment.top_center,
        content=ft.Container(
            width=_MAX_WIDTH,
            content=content,
        ),
    )


# ---------- section builders ----------


def build_details_header(data: DecisionReportData) -> ft.Control:
    """Laravel-style page header: title, confidence, subtitle, record ID, generated date."""
    score = data.confidence_score
    conf_badge = f"{score}% Confidence" if score else "— Confidence"
    record_val = f"#{data.record_id}" if data.record_id is not None else "—"
    generated_val = data.generated_label or "—"

    title_row = ft.Row(
        spacing=12,
        wrap=True,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text(
                "Recommendation Details",
                size=24,
                weight=ft.FontWeight.W_700,
                color=_C_PRIMARY,
            ),
            _header_confidence_badge(conf_badge),
        ],
    )

    left = ft.Column(
        spacing=6,
        tight=True,
        controls=[
            title_row,
            ft.Text(_HEADER_SUBTITLE, size=13, color=_C_SECONDARY),
        ],
    )

    right = ft.Row(
        spacing=10,
        controls=[
            ft.Container(
                width=132,
                content=_header_meta_chip("Record ID", record_val),
            ),
            ft.Container(
                width=168,
                content=_header_meta_chip("Generated", generated_val),
            ),
        ],
    )

    body = ft.ResponsiveRow(
        spacing=16,
        run_spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(col={"xs": 12, "md": 8}, content=left),
            ft.Container(
                col={"xs": 12, "md": 4},
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.END,
                    controls=[right],
                ),
            ),
        ],
    )
    return _glass_card(body, padding=20)


def build_summary_overview_row(
    data: DecisionReportData,
    *,
    on_copy_project_summary: Optional[Callable[[ft.ControlEvent], None]] = None,
) -> ft.Control:
    """Laravel-style row: Project Summary (~30%) + Saved Recommendation / Alternatives (~70%)."""
    right_sections: list[ft.Control] = [build_saved_recommendation_card(data)]
    alt = build_alternative_stacks_card(data)
    if alt is not None:
        right_sections.append(alt)

    right_column = ft.Column(spacing=_CARD_GAP, controls=right_sections)

    return ft.ResponsiveRow(
        spacing=_SECTION_GAP,
        run_spacing=_SECTION_GAP,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[
            ft.Container(
                col={"xs": 12, "lg": 4},
                content=build_project_summary_card(
                    data,
                    on_copy_project_summary=on_copy_project_summary,
                ),
            ),
            ft.Container(col={"xs": 12, "lg": 8}, content=right_column),
        ],
    )


def _project_summary_copy_handler(
    data: DecisionReportData,
    override: Optional[Callable[[ft.ControlEvent], None]],
) -> Callable[[ft.ControlEvent], None]:
    if override is not None:
        return override
    return lambda e: copy_project_summary(e, data)


def build_project_summary_copy_text(data: DecisionReportData) -> str:
    """Plain-text export of Project Summary fields for the clipboard."""
    lines = ["PROJECT SUMMARY", ""]
    for label, value in data.profile_fields:
        text = (value or "").strip() or "—"
        lines.append(f"{label}: {text}")
    return "\n".join(lines).strip()


def copy_project_summary(e: ft.ControlEvent, data: DecisionReportData) -> None:
    """Copy project summary to the clipboard and show feedback."""
    page = e.page
    if page is None:
        return
    try:
        page.set_clipboard(build_project_summary_copy_text(data))
        show_toast(page, "Project summary copied.", kind="success")
    except Exception:
        show_toast(page, "Unable to copy project summary.", kind="warning")


def build_project_summary_copy_button(
    on_click: Callable[[ft.ControlEvent], None],
) -> ft.Control:
    """Compact outline copy control for the Project Summary header."""
    return ft.Container(
        height=32,
        border=ft.border.all(1, ft.colors.with_opacity(0.45, _C_CYAN)),
        border_radius=Radii.pill,
        bgcolor=ft.colors.with_opacity(0.08, _C_CYAN),
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
        alignment=ft.alignment.center,
        ink=True,
        on_click=on_click,
        content=ft.Row(
            spacing=4,
            tight=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.icons.CONTENT_COPY_OUTLINED, size=14, color=_C_CYAN),
                ft.Text("Copy", size=11, weight=ft.FontWeight.W_600, color=_C_CYAN),
            ],
        ),
    )


def build_project_summary_card(
    data: DecisionReportData,
    *,
    on_copy_project_summary: Optional[Callable[[ft.ControlEvent], None]] = None,
) -> ft.Control:
    score = data.confidence_score
    conf_badge = build_confidence_badge(score) if score else None

    header_left = ft.Column(
        spacing=4,
        tight=True,
        expand=True,
        controls=[
            ft.Text("Project Summary", size=17, weight=ft.FontWeight.W_600, color=_C_PRIMARY),
            ft.Text(
                "Core project information saved with the recommendation.",
                size=12,
                color=_C_SECONDARY,
            ),
        ],
    )

    header_right_items: list[ft.Control] = []
    if conf_badge is not None:
        header_right_items.append(conf_badge)
    if on_copy_project_summary is not None:
        header_right_items.append(
            build_project_summary_copy_button(on_copy_project_summary)
        )

    header_controls: list[ft.Control] = [header_left]
    if header_right_items:
        header_controls.append(
            ft.Column(
                spacing=6,
                horizontal_alignment=ft.CrossAxisAlignment.END,
                controls=header_right_items,
            )
        )

    rows = [
        build_summary_row(label, value)
        for label, value in data.profile_fields
    ]

    return _glass_card(
        ft.Column(
            spacing=0,
            controls=[
                ft.Container(
                    padding=ft.padding.only(bottom=12),
                    content=ft.Row(
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        controls=header_controls,
                    ),
                ),
                ft.Column(spacing=0, controls=rows),
            ],
        )
    )


def build_saved_recommendation_card(data: DecisionReportData) -> ft.Control:
    score = data.confidence_score
    lang = data.recommended_language or "—"
    fw = data.recommended_framework or "—"
    sdlc = data.recommended_sdlc or "—"

    header = ft.Row(
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[
            ft.Column(
                spacing=4,
                tight=True,
                expand=True,
                controls=[
                    ft.Text(
                        "Saved Recommendation",
                        size=17,
                        weight=ft.FontWeight.W_600,
                        color=_C_PRIMARY,
                    ),
                    ft.Text(
                        "The strongest stack match based on the project details.",
                        size=12,
                        color=_C_SECONDARY,
                    ),
                ],
            ),
            build_confidence_badge(score),
        ],
    )

    mini_row = ft.ResponsiveRow(
        spacing=_CARD_GAP,
        run_spacing=_CARD_GAP,
        controls=[
            ft.Container(
                col={"xs": 6, "sm": 3},
                content=build_stack_mini_card("Programming Language", lang),
            ),
            ft.Container(
                col={"xs": 6, "sm": 3},
                content=build_stack_mini_card("Framework", fw),
            ),
            ft.Container(
                col={"xs": 6, "sm": 3},
                content=build_stack_mini_card("SDLC Model", sdlc),
            ),
            ft.Container(
                col={"xs": 6, "sm": 3},
                content=build_stack_mini_card(
                    "Confidence Score",
                    f"{score}%" if score else "—",
                    highlight=True,
                ),
            ),
        ],
    )

    result_view = _report_result_view(data)
    lang_body = format_reason_text(
        "language",
        _reason_text(data.language_reason, data.why_language_points),
        result_view,
        data.reason_context,
    )
    fw_body = format_reason_text(
        "framework",
        _reason_text(data.framework_reason, data.why_framework_points),
        result_view,
        data.reason_context,
    )
    sdlc_body = format_reason_text(
        "sdlc",
        _reason_text(data.sdlc_reason, data.why_sdlc_points),
        result_view,
        data.reason_context,
    )

    reason_row = ft.ResponsiveRow(
        spacing=_CARD_GAP,
        run_spacing=_CARD_GAP,
        controls=[
            ft.Container(
                col={"xs": 12, "md": 4},
                content=build_reason_card("Language Reason", lang_body),
            ),
            ft.Container(
                col={"xs": 12, "md": 4},
                content=build_reason_card("Framework Reason", fw_body),
            ),
            ft.Container(
                col={"xs": 12, "md": 4},
                content=build_reason_card("SDLC Reason", sdlc_body),
            ),
        ],
    )

    disclaimer = ft.Text(_DISCLAIMER, size=11, color=_C_MUTED, italic=True)

    return _glass_card(
        ft.Column(
            spacing=_CARD_GAP,
            controls=[header, mini_row, reason_row, disclaimer],
        )
    )


def build_alternative_technology_stacks_card(data: DecisionReportData) -> Optional[ft.Control]:
    """Alias for the alternatives section builder."""
    return build_alternative_stacks_card(data)


def build_alternative_stacks_card(data: DecisionReportData) -> Optional[ft.Control]:
    """Laravel-style alternatives table with collapsible trade-offs (display only)."""
    stacks = dedupe_alternatives_by_language_framework(
        data.alternative_stacks,
        {
            "language": data.recommended_language,
            "framework": data.recommended_framework,
            "sdlc": data.recommended_sdlc,
        },
    )
    if not stacks:
        return None

    raw_scores = [_raw_fit_value(alt) for alt in stacks]

    header = ft.Row(
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[
            ft.Column(
                spacing=4,
                tight=True,
                expand=True,
                controls=[
                    ft.Text(
                        "Alternative Technology Stacks",
                        size=17,
                        weight=ft.FontWeight.W_600,
                        color=_C_PRIMARY,
                    ),
                    ft.Text(
                        "Options that could also fit the project with different trade-offs.",
                        size=13,
                        color=_C_SECONDARY,
                    ),
                ],
            ),
            ft.Text(
                "Compared by fit, strength, and limitation",
                size=11,
                color=_C_MUTED,
            ),
        ],
    )

    table_header = ft.Container(
        padding=ft.padding.symmetric(vertical=8, horizontal=4),
        border=ft.border.only(bottom=ft.BorderSide(1, _C_INNER_BD)),
        content=ft.Row(
            controls=[
                _table_head_cell("Language", 2),
                _table_head_cell("Framework", 2),
                _table_head_cell("SDLC Model", 2),
                _table_head_cell("Best For", 2),
                _table_head_cell("Score", 1),
                _table_head_cell("Limitation", 3),
            ],
        ),
    )

    rows: list[ft.Control] = [table_header]
    for alt in stacks[:_MAX_ALTERNATIVE_ROWS]:
        rows.append(
            build_alternative_row(alt, raw_scores=raw_scores),
        )

    return _glass_card(
        ft.Column(
            spacing=12,
            controls=[
                header,
                ft.Column(spacing=0, controls=rows),
            ],
        )
    )


def normalize_alt_key(value: Any) -> str:
    """Display-only key for language/framework deduplication."""
    text = str(value or "").strip().lower()
    if not text:
        return ""
    text = text.replace(".", "")
    text = re.sub(r"[\s_\-/]+", "", text)
    return text


def dedupe_alternatives_by_language_framework(
    alternatives: list[dict[str, Any]],
    selected_stack: dict[str, str],
) -> list[dict[str, Any]]:
    """One row per language+framework; keep highest score; merge DevOps variants."""
    pl = normalize_alt_key(selected_stack.get("language"))
    pf = normalize_alt_key(selected_stack.get("framework"))

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for alt in alternatives:
        if not isinstance(alt, dict):
            continue
        lang = str(alt.get("language", "") or "").strip()
        fw = str(alt.get("framework", "") or "").strip()
        if not lang or not fw:
            continue
        key = (normalize_alt_key(lang), normalize_alt_key(fw))
        if key == (pl, pf) and pl and pf:
            continue
        grouped.setdefault(key, []).append(alt)

    merged: list[dict[str, Any]] = []
    for items in grouped.values():
        kept = _pick_best_alternative_for_group(items)
        merge_devops_support_note(kept, items)
        merged.append(kept)

    merged.sort(key=_raw_fit_value, reverse=True)
    return merged[:_MAX_ALTERNATIVE_ROWS]


def dedupe_alternatives(
    alternatives: list[dict[str, Any]],
    primary_language: str,
    primary_framework: str,
    primary_sdlc: str,
) -> list[dict[str, Any]]:
    return dedupe_alternatives_by_language_framework(
        alternatives,
        {
            "language": primary_language,
            "framework": primary_framework,
            "sdlc": primary_sdlc,
        },
    )


def _pick_best_alternative_for_group(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Highest-scoring stack; SDLC column prefers a non-DevOps model when present."""
    winner = dict(max(items, key=_raw_fit_value))
    if _is_devops_sdlc(winner.get("sdlc")):
        non_devops = [a for a in items if not _is_devops_sdlc(a.get("sdlc"))]
        if non_devops:
            best_nd = max(non_devops, key=_raw_fit_value)
            winner["sdlc"] = best_nd.get("sdlc")
    return winner


def _is_devops_sdlc(sdlc: Any) -> bool:
    return normalize_alt_key(sdlc) == "devops"


def merge_devops_support_note(
    alt: dict[str, Any],
    group: list[dict[str, Any]],
) -> None:
    """Append DevOps support text when a dropped duplicate used DevOps as SDLC."""
    if not any(_is_devops_sdlc(item.get("sdlc")) for item in group):
        return
    limitation = str(alt.get("limitation", "") or "").strip()
    if _DEVOPS_UI_NOTE.lower() in limitation.lower():
        alt["_devops_support_merged"] = True
        return
    alt["limitation"] = f"{limitation} {_DEVOPS_UI_NOTE}".strip() if limitation else _DEVOPS_UI_NOTE
    alt["_devops_support_merged"] = True


def _display_sdlc_for_row(alt: dict[str, Any]) -> str:
    sdlc = str(alt.get("sdlc", "") or "").strip()
    if _is_devops_sdlc(sdlc):
        return "—"
    return sdlc or "—"


def format_alt_fit_score(
    alt: dict[str, Any],
    *,
    raw_scores: list[float],
) -> str:
    return normalize_fit_score_for_display(alt, raw_scores=raw_scores)


def _raw_fit_value(alt: dict[str, Any]) -> float:
    raw_internal = alt.get("_raw_stack_score")
    if raw_internal is not None:
        try:
            return float(raw_internal)
        except (TypeError, ValueError):
            pass
    for key in ("fit_score", "fit_percent"):
        raw = alt.get(key)
        if raw is None:
            continue
        try:
            return float(raw)
        except (TypeError, ValueError):
            continue
    return 0.0


def normalize_fit_score_for_display(
    alt: dict[str, Any],
    *,
    raw_scores: list[float],
) -> str:
    """Display-only percentage; never show raw internal totals."""
    display = str(alt.get("fit_display", "") or "").strip()
    if display:
        if "%" in display:
            match = re.search(r"(\d{1,3})\s*%", display)
            if match:
                return f"{match.group(1)}%"
        if display.lower() == "strong fit":
            return "Strong fit"

    fit_percent = alt.get("fit_percent")
    if fit_percent is not None:
        try:
            pct = int(round(float(fit_percent)))
            if 0 < pct <= 100:
                return f"{pct}%"
        except (TypeError, ValueError):
            pass

    raw = _raw_fit_value(alt)
    scores = [s for s in raw_scores if s > 0]
    if not scores:
        return "Strong fit" if raw >= 88 else "—"

    if raw <= 100 and max(scores) <= 100:
        pct = max(0, min(100, int(round(raw))))
        return f"{pct}%"

    max_raw = max(scores)
    min_raw = min(scores)
    ref = max(max_raw, 1.0)
    span = max(max_raw - min_raw, 1.0)
    rel = (raw - min_raw) / span
    win_ratio = raw / ref
    pct = 60 + round(min(35, rel * 18 + win_ratio * 17))
    pct = max(60, min(95, pct))
    return f"{pct}%"


def get_stack_tradeoff_fallback(
    language: str,
    framework: str,
    sdlc: str,
) -> tuple[list[str], list[str], dict[str, str]]:
    """Display-only advantages, disadvantages, and comparison lines."""
    lang = (language or "").strip()
    fw = (framework or "").strip()
    key = f"{lang}|{fw}".lower()

    presets: dict[str, tuple[list[str], list[str]]] = {
        "typescript|nestjs": (
            [
                "Strong structure for scalable APIs",
                "Good fit for real-time and modular backend services",
                "Shared language with frontend teams",
            ],
            [
                "Requires strong TypeScript/backend architecture knowledge",
                "Async patterns and Node ecosystem can add complexity",
            ],
        ),
        "java|spring boot": (
            [
                "Mature enterprise backend ecosystem",
                "Strong for security, scalability, and complex business logic",
                "Good long-term maintainability",
            ],
            [
                "More setup and configuration",
                "Steeper learning curve for smaller teams",
            ],
        ),
        "c#|asp.net core": (
            [
                "Strong enterprise web/API framework",
                "Good performance and security tooling",
                "Works well for Microsoft-based environments",
            ],
            [
                "Best when the team knows C#/.NET ecosystem",
                "Deployment may require more environment planning",
            ],
        ),
        "python|fastapi": (
            [
                "Fast API development",
                "Strong Python ecosystem",
                "Good for AI/data/API integrations",
            ],
            [
                "Requires careful architecture for large systems",
                "Async/database patterns may need discipline",
            ],
        ),
        "php|laravel": (
            [
                "Rapid CRUD/admin development",
                "Built-in MVC, routing, validation, migrations, and auth support",
                "Good for web management systems",
            ],
            [
                "Less ideal for mobile-first or high-performance real-time systems",
                "Requires good structure for large projects",
            ],
        ),
        "dart|flutter": (
            [
                "Strong cross-platform mobile UI",
                "Fast interface development",
                "Good for mobile-first apps",
            ],
            [
                "Backend still requires separate API services",
                "Team must learn Flutter/Dart patterns",
            ],
        ),
        "rust|tauri": (
            [
                "Lightweight and secure desktop apps",
                "Good performance",
                "Modern cross-platform desktop approach",
            ],
            [
                "Steeper learning curve",
                "Smaller ecosystem compared to traditional web stacks",
            ],
        ),
        "ruby|ruby on rails": (
            [
                "Fast MVP and CRUD development",
                "Convention-over-configuration",
                "Good for startup-style web apps",
            ],
            [
                "Performance tuning may be needed at scale",
                "Smaller local talent pool depending on team context",
            ],
        ),
        "go|gin": (
            [
                "High-performance APIs with simple concurrency",
                "Good for cloud-native backend services",
                "Fast compile and deployment cycles",
            ],
            [
                "Less batteries-included than larger frameworks",
                "Team may need to assemble more infrastructure pieces",
            ],
        ),
    }

    advantages, disadvantages = presets.get(
        key,
        (
            [
                "Compatible with this project profile",
                "Provides a viable implementation path",
                "Can support the required features with proper setup",
            ],
            [
                "May require different tooling or learning effort",
                "May need additional planning for scalability, security, or maintenance",
            ],
        ),
    )

    comparison = _comparison_grid_fallback(language, framework, sdlc)
    return advantages, disadvantages, comparison


def _comparison_grid_fallback(
    language: str,
    framework: str,
    sdlc: str,
) -> dict[str, str]:
    _ = sdlc
    fw = (framework or "").lower()
    if "spring" in fw or "asp.net" in fw or "django" in fw:
        scale = "Strong for enterprise-scale APIs with proper architecture."
    elif "flutter" in fw or "react native" in fw:
        scale = "Strong for client-facing apps; backend scale depends on API design."
    elif "fastapi" in fw or "nestjs" in fw or "gin" in fw:
        scale = "Strong for many scalable APIs, especially with proper architecture."
    else:
        scale = "Scalability depends on architecture, caching, and deployment choices."

    return {
        "Scalability": scale,
        "Maintenance": "Good maintainability with structured patterns and documentation.",
        "Learning Curve": f"Moderate learning curve; depends on team experience with {language or 'the stack'}.",
        "Dev Speed": "Moderate to fast development speed depending on tooling and team familiarity.",
        "Cost": "Costs depend mainly on hosting choice and team ramp-up time.",
    }


def _tradeoff_lists(alt: dict[str, Any]) -> tuple[list[str], list[str], dict[str, str]]:
    tradeoffs = alt.get("tradeoffs") if isinstance(alt.get("tradeoffs"), dict) else {}
    advantages = _as_string_list(alt.get("advantages") or tradeoffs.get("advantages"))
    disadvantages = _as_string_list(alt.get("disadvantages") or tradeoffs.get("disadvantages"))
    comparison_raw = tradeoffs.get("comparison") or alt.get("comparison") or {}
    if isinstance(comparison_raw, dict) and comparison_raw:
        comparison = {str(k): str(v) for k, v in comparison_raw.items()}
    else:
        comparison = {}

    lang = str(alt.get("language", "") or "")
    fw = str(alt.get("framework", "") or "")
    sdlc = str(alt.get("sdlc", "") or "")
    if not advantages or not disadvantages:
        fb_adv, fb_dis, fb_cmp = get_stack_tradeoff_fallback(lang, fw, sdlc)
        if not advantages:
            advantages = fb_adv
        if not disadvantages:
            disadvantages = fb_dis
        if not comparison:
            comparison = fb_cmp
    elif not comparison:
        _, _, comparison = get_stack_tradeoff_fallback(lang, fw, sdlc)

    return advantages, disadvantages, comparison


def _as_string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _tradeoff_list_card(
    title: str,
    accent: str,
    items: list[str],
) -> ft.Control:
    bullets = [_mini_bullet(item) for item in items[:6]] or [
        ft.Text("—", size=11, color=_C_MUTED),
    ]
    return ft.Container(
        expand=True,
        bgcolor=_C_REASON_BG,
        border=ft.border.all(1, ft.colors.with_opacity(0.35, _C_REASON_BD)),
        border_radius=12,
        padding=12,
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Text(title, size=11, weight=ft.FontWeight.W_700, color=accent),
                ft.Column(spacing=4, controls=bullets),
            ],
        ),
    )


def _tradeoff_comparison_card(comparison: dict[str, str]) -> ft.Control:
    rows = [
        ft.Column(
            spacing=2,
            tight=True,
            controls=[
                ft.Text(label, size=10, weight=ft.FontWeight.W_700, color=_C_MUTED),
                ft.Text(text, size=11, color=_C_SECONDARY),
            ],
        )
        for label, text in comparison.items()
    ]
    if not rows:
        rows = [ft.Text("No comparison notes available.", size=11, color=_C_MUTED)]

    return ft.Container(
        expand=True,
        bgcolor=_C_REASON_BG,
        border=ft.border.all(1, ft.colors.with_opacity(0.35, _C_REASON_BD)),
        border_radius=12,
        padding=12,
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Text("COMPARISON", size=11, weight=ft.FontWeight.W_700, color=_C_CYAN),
                ft.Column(spacing=6, controls=rows),
            ],
        ),
    )


def build_tradeoffs_panel(alt: dict[str, Any]) -> ft.Control:
    """Full-width horizontal trade-offs panel (placed below the table row)."""
    advantages, disadvantages, comparison = _tradeoff_lists(alt)

    body = ft.ResponsiveRow(
        spacing=12,
        run_spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[
            ft.Container(
                col={"xs": 12, "md": 4},
                content=_tradeoff_list_card("ADVANTAGES", _C_ADV_LABEL, advantages),
            ),
            ft.Container(
                col={"xs": 12, "md": 4},
                content=_tradeoff_list_card("DISADVANTAGES", _C_DISADV_LABEL, disadvantages),
            ),
            ft.Container(
                col={"xs": 12, "md": 4},
                content=_tradeoff_comparison_card(comparison),
            ),
        ],
    )

    return ft.Container(
        bgcolor=_C_INNER,
        border=ft.border.all(1, _C_INNER_BD),
        border_radius=12,
        padding=14,
        content=body,
    )


def build_alternative_row(
    alt: dict[str, Any],
    *,
    raw_scores: list[float],
) -> ft.Control:
    lang = str(alt.get("language", "") or "—")
    fw = str(alt.get("framework", "") or "—")
    sdlc = _display_sdlc_for_row(alt)
    best_for = str(alt.get("best_for", "") or "—")
    score_label = format_alt_fit_score(alt, raw_scores=raw_scores)
    limitation = str(alt.get("limitation", "") or "").strip()
    if not limitation:
        limitation = (
            "May involve different trade-offs in learning curve, tooling setup, "
            "or long-term maintenance."
        )
    support = None if alt.get("_devops_support_merged") else devops_support_note(alt)

    tradeoff_panel = ft.Container(
        visible=False,
        content=build_tradeoffs_panel(alt),
    )
    toggle_label = ft.Text(
        "▸ TRADE-OFFS",
        size=11,
        weight=ft.FontWeight.W_700,
        color=_C_CYAN,
    )

    def toggle_tradeoffs(e: ft.ControlEvent) -> None:
        tradeoff_panel.visible = not tradeoff_panel.visible
        toggle_label.value = (
            "▾ TRADE-OFFS" if tradeoff_panel.visible else "▸ TRADE-OFFS"
        )
        if tradeoff_panel.page:
            tradeoff_panel.update()
        if toggle_label.page:
            toggle_label.update()

    lim_controls: list[ft.Control] = [
        ft.Text(limitation, size=12, color=_C_SECONDARY, selectable=True),
    ]
    if support:
        lim_controls.append(ft.Text(support, size=11, color=_C_MUTED, italic=True))
    lim_controls.append(
        ft.Container(
            ink=True,
            on_click=toggle_tradeoffs,
            padding=ft.padding.only(top=6),
            content=toggle_label,
        )
    )

    limitation_cell = ft.Container(
        expand=3,
        content=ft.Column(spacing=4, controls=lim_controls),
    )

    main_row = ft.Container(
        padding=ft.padding.symmetric(vertical=12, horizontal=4),
        content=ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                _table_body_cell(lang, 2),
                _table_body_cell(fw, 2),
                _table_body_cell(sdlc, 2),
                _table_body_cell(best_for, 2),
                _table_body_cell(score_label, 1),
                limitation_cell,
            ],
        ),
    )

    return ft.Container(
        border=ft.border.only(
            bottom=ft.BorderSide(1, ft.colors.with_opacity(0.35, _C_INNER_BD))
        ),
        content=ft.Column(
            spacing=10,
            tight=True,
            controls=[
                main_row,
                tradeoff_panel,
            ],
        ),
    )


def build_user_preference_card(data: DecisionReportData) -> Optional[ft.Control]:
    pref = data.user_preferred_stack
    if not isinstance(pref, dict) or not pref.get("is_provided"):
        return None

    alignment = str(pref.get("alignment_status", "") or "—").strip()
    compatible = pref.get("is_compatible", True)
    border_color = _C_CYAN
    if alignment == "Aligned":
        border_color = _C_SUCCESS
    elif alignment == "Incompatible" or compatible is False:
        border_color = _C_WARNING

    fields = [
        ("Preferred Language", str(pref.get("language", "") or "—")),
        ("Preferred Framework", str(pref.get("framework", "") or "—")),
        ("Preferred SDLC", str(pref.get("sdlc", "") or "—")),
        ("Reason", str(pref.get("reason", "") or "—")),
        ("Alignment Status", alignment or "—"),
        (
            "Compatibility Status",
            "Compatible" if compatible else "Incompatible",
        ),
        ("Comparison Summary", str(pref.get("comparison_summary", "") or "—")),
    ]

    kv = [
        ft.Container(
            col={"xs": 12, "sm": 6},
            content=_profile_kv(label, value, wide=label == "Comparison Summary"),
        )
        for label, value in fields
    ]

    return ft.Container(
        border=ft.border.all(1, border_color),
        border_radius=22,
        bgcolor=_C_PANEL,
        padding=_PANEL_PAD,
        shadow=_GLASS_SHADOW,
        content=ft.Column(
            spacing=12,
            controls=[
                _section_title(
                    "User Preferred Stack Comparison",
                    subtitle="How your stated preference compares to the top recommendation.",
                ),
                ft.ResponsiveRow(spacing=10, run_spacing=8, controls=kv),
            ],
        ),
    )


def build_why_not_risk_section(data: DecisionReportData) -> Optional[ft.Control]:
    """Why Not (~65%) + Risk (~35%); stacks below xl to avoid narrow-column crush."""
    why_not = build_why_not_this_card(data)
    risk = build_risk_analysis_card(data)
    if why_not is None and risk is None:
        return None

    # ResponsiveRow only (no Row+wrap+expand — that breaks CanvasKit with unbounded width).
    # Side-by-side at xxl (≥1400px); stacked full-width below that (expanded sidebar safe).
    return ft.ResponsiveRow(
        spacing=_WHY_RISK_GAP,
        run_spacing=_WHY_RISK_GAP,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[
            ft.Container(
                col={"xs": 12, "xxl": 8},
                content=why_not if why_not is not None else ft.Container(),
            ),
            ft.Container(
                col={"xs": 12, "xxl": 4},
                content=risk if risk is not None else ft.Container(),
            ),
        ],
    )


def build_why_not_this_card(data: DecisionReportData) -> Optional[ft.Control]:
    entries = data.why_not_this
    if not entries:
        return None

    cards = [build_why_not_item_card(entry) for entry in entries[:6]]
    cards = [c for c in cards if c is not None]
    if not cards:
        return None

    return _glass_card(
        ft.Column(
            spacing=14,
            controls=[
                _section_title(
                    "Why Not This?",
                    subtitle="Why other options were not selected as the top recommendation.",
                ),
                ft.Column(
                    spacing=8,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                    controls=cards,
                ),
            ],
        ),
    )


def build_why_not_item_card(entry: dict[str, Any]) -> Optional[ft.Control]:
    title = str(
        entry.get("technology_or_stack", "") or entry.get("title", "") or ""
    ).strip()
    if not title:
        return None
    reason = str(entry.get("reason", "") or "").strip() or "No reason available."
    when = str(entry.get("when_it_is_better", "") or "").strip()
    source = str(entry.get("source", "") or "").strip()

    lines: list[ft.Control] = [
        ft.Text(
            f"Why not {title}?",
            size=14,
            weight=ft.FontWeight.W_600,
            color=_C_PRIMARY,
            selectable=True,
        ),
        ft.Text(reason, size=13, color=_C_SECONDARY, selectable=True),
    ]
    if when:
        lines.append(
            ft.Text(f"When it is better: {when}", size=12, color=_C_MUTED, italic=True)
        )
    if source:
        lines.append(
            ft.Text(f"Source: {source}", size=11, color=_C_CYAN, weight=ft.FontWeight.W_600)
        )

    return _inner_card(ft.Column(spacing=6, controls=lines), padding=14)


def build_risk_analysis_card(data: DecisionReportData) -> Optional[ft.Control]:
    risks = data.risk_analysis
    if not risks:
        return None

    cards = [build_risk_item_card(item) for item in risks[:8]]
    cards = [c for c in cards if c is not None]
    if not cards:
        return None

    return _glass_card(
        ft.Column(
            spacing=12,
            controls=[
                _section_title("Risk Analysis"),
                ft.Column(
                    spacing=8,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                    controls=cards,
                ),
            ],
        ),
    )


def build_risk_item_card(item: dict[str, Any]) -> Optional[ft.Control]:
    title = str(
        item.get("risk", "")
        or item.get("risk_title", "")
        or item.get("title", "")
        or "Unknown risk"
    ).strip()
    impact_level = str(item.get("impact_level", "") or "").strip()
    impact_raw = str(item.get("impact", "") or "").strip()
    impact = _impact_label_for_badge(impact_level or impact_raw or "Medium")
    reason = str(item.get("reason", "") or "").strip() or "No reason available."
    mitigation = (
        str(item.get("mitigation", "") or item.get("solution", "") or "").strip()
        or "No mitigation available."
    )

    header = ft.Column(
        spacing=8,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        controls=[
            ft.Text(
                title,
                size=14,
                weight=ft.FontWeight.W_600,
                color=_C_PRIMARY,
                selectable=True,
            ),
            ft.Row(
                controls=[build_impact_badge(impact)],
                alignment=ft.MainAxisAlignment.START,
            ),
        ],
    )

    body = ft.Column(
        spacing=8,
        controls=[
            header,
            ft.Text(reason, size=12, color=_C_SECONDARY, selectable=True),
            ft.Row(
                wrap=True,
                spacing=4,
                run_spacing=2,
                controls=[
                    ft.Text(
                        "Solution:",
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color=_C_PRIMARY,
                    ),
                    ft.Text(
                        mitigation,
                        size=12,
                        color=_C_SECONDARY,
                        selectable=True,
                    ),
                ],
            ),
        ],
    )

    return _inner_card(body, padding=14)


def build_impact_badge(level: str) -> ft.Control:
    return _impact_badge(level)


def build_skill_gap_section(data: DecisionReportData) -> Optional[ft.Control]:
    """Two-column row: Skill Gap Analysis (~70%) + Learning Priorities (~30%)."""
    skill = build_skill_gap_analysis_card(data)
    learning = build_learning_priorities_card(data)
    if skill is None and learning is None:
        return None

    controls: list[ft.Control] = []
    if skill is not None:
        controls.append(
            ft.Container(col={"xs": 12, "lg": 8}, content=skill),
        )
    if learning is not None:
        controls.append(
            ft.Container(
                col={"xs": 12, "lg": 4} if skill is not None else {"xs": 12},
                content=learning,
            ),
        )

    return ft.ResponsiveRow(
        spacing=_SECTION_GAP,
        run_spacing=_SECTION_GAP,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=controls,
    )


def build_skill_gap_analysis_card(data: DecisionReportData) -> Optional[ft.Control]:
    rows = data.skill_gap_analysis
    if not rows:
        return None

    header = ft.Container(
        visible=True,
        content=ft.Row(
            controls=[
                _table_head_cell("Skill", 2),
                _table_head_cell("Required", 1),
                _table_head_cell("User", 1),
                _table_head_cell("Gap", 1),
                _table_head_cell("Suggestion", 3),
            ],
        ),
        padding=ft.padding.only(bottom=8),
        border=ft.border.only(bottom=ft.BorderSide(1, _C_INNER_BD)),
    )

    table_rows: list[ft.Control] = [header]
    for item in rows:
        table_rows.append(
            ft.Container(
                padding=ft.padding.symmetric(vertical=10),
                border=ft.border.only(bottom=ft.BorderSide(1, ft.colors.with_opacity(0.35, _C_INNER_BD))),
                content=ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        _table_body_cell(str(item.get("skill", "—")), 2),
                        _table_body_cell(str(item.get("required_level", "—")), 1),
                        _table_body_cell(str(item.get("user_level", "—")), 1),
                        _table_body_cell(str(item.get("gap_level", "—")), 1),
                        _table_body_cell(str(item.get("suggestion", "—")), 3),
                    ],
                ),
            )
        )

    return _glass_card(
        ft.Column(
            spacing=12,
            controls=[
                _section_title("Skill Gap Analysis"),
                ft.Container(content=ft.Column(controls=table_rows)),
            ],
        )
    )


def build_skill_gap_card(data: DecisionReportData) -> Optional[ft.Control]:
    """Backward-compatible alias for ``build_skill_gap_analysis_card``."""
    return build_skill_gap_analysis_card(data)


def build_learning_priorities_card(
    data: DecisionReportData,
    input_data: Optional[Mapping[str, Any]] = None,
) -> ft.Control:
    """Right-side preparation checklist derived from stack and skill gaps."""
    priorities = derive_learning_priorities(data, input_data=input_data)
    items = [
        build_priority_item(title, description, index=idx + 1)
        for idx, (title, description) in enumerate(priorities)
    ]

    return _glass_card(
        ft.Column(
            spacing=12,
            controls=[
                _section_title(
                    "Learning Priorities",
                    subtitle="What to prepare before building this stack.",
                ),
                ft.Column(spacing=8, controls=items),
            ],
        ),
        padding=18,
    )


def build_priority_item(title: str, description: str, *, index: int) -> ft.Control:
    safe_title = (title or "Priority").strip()
    safe_desc = (description or "").strip() or "Review this area before implementation."
    return ft.Container(
        bgcolor=_C_INNER,
        border=ft.border.all(1, _C_INNER_BD),
        border_radius=12,
        padding=12,
        content=ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=10,
            controls=[
                ft.Container(
                    width=26,
                    height=26,
                    border_radius=999,
                    bgcolor=ft.colors.with_opacity(0.15, _C_CYAN),
                    border=ft.border.all(1, ft.colors.with_opacity(0.35, _C_CYAN)),
                    alignment=ft.alignment.center,
                    content=ft.Text(
                        str(index),
                        size=11,
                        weight=ft.FontWeight.W_700,
                        color=_C_CYAN,
                    ),
                ),
                ft.Column(
                    spacing=4,
                    expand=True,
                    controls=[
                        ft.Text(
                            safe_title,
                            size=13,
                            weight=ft.FontWeight.W_600,
                            color=_C_PRIMARY,
                            selectable=True,
                        ),
                        ft.Text(
                            safe_desc,
                            size=12,
                            color=_C_SECONDARY,
                            selectable=True,
                        ),
                    ],
                ),
            ],
        ),
    )


def derive_learning_priorities(
    data: DecisionReportData,
    input_data: Optional[Mapping[str, Any]] = None,
) -> list[tuple[str, str]]:
    """Display-only priorities from skill gaps and recommended stack (no scoring)."""
    ctx = {**dict(data.reason_context or {}), **dict(input_data or {})}
    priorities: list[tuple[str, str]] = []

    rows = list(data.skill_gap_analysis or [])
    rows.sort(key=lambda row: _gap_sort_key(str(row.get("gap_level", "") or "")))

    for item in rows:
        if len(priorities) >= 5:
            break
        skill = str(item.get("skill", "") or "").strip()
        if not skill:
            continue
        gap = str(item.get("gap_level", "") or "").strip()
        suggestion = str(item.get("suggestion", "") or "").strip()
        if gap and gap.lower() not in ("—", "-", "none", "no gap", ""):
            title = f"Close {gap} gap: {skill}"
        else:
            title = f"Strengthen {skill}"
        desc = (
            suggestion
            or f"Practice {skill} fundamentals so delivery matches project requirements."
        )
        priorities.append((title, desc))

    stack_items = _stack_learning_fallbacks(
        data.recommended_language,
        data.recommended_framework,
        data.recommended_sdlc,
        ctx,
    )
    for title, desc in stack_items:
        if len(priorities) >= 5:
            break
        if not _priority_exists(priorities, title, desc):
            priorities.append((title, desc))

    if len(priorities) < 3:
        for title, desc in _generic_learning_priorities(data, ctx):
            if len(priorities) >= 5:
                break
            if not _priority_exists(priorities, title, desc):
                priorities.append((title, desc))

    return priorities[:5]


def _as_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    text = str(value).strip()
    if not text:
        return []
    if ";" in text:
        return [p.strip() for p in text.split(";") if p.strip()]
    if "," in text and len(text) > 40:
        return [p.strip() for p in text.split(",") if p.strip()]
    return [text]


def _normalize_focus_label(raw: Any) -> str:
    text = str(raw or "").strip()
    if not text:
        return ""
    if "%" in text:
        return text
    if any(ch.isdigit() for ch in text):
        return text if "%" in text else f"{text}%"
    return text


def _sdlc_roadmap_family(sdlc: str) -> str:
    s = (sdlc or "").strip().lower()
    if any(k in s for k in ("agile", "scrum", "kanban")):
        return "agile"
    if "spiral" in s:
        return "spiral"
    if "v-model" in s or "v model" in s:
        return "vmodel"
    if "waterfall" in s:
        return "waterfall"
    if "iterative" in s or "incremental" in s:
        return "iterative"
    if "rad" in s or "prototype" in s:
        return "rad"
    if "devops" in s:
        return "devops"
    return "agile"


def _roadmap_phase_template(
    phase: str,
    title: str,
    description: str,
    *,
    objectives: list[str],
    deliverables: list[str],
    priorities: list[str],
    estimated_focus: str,
) -> dict[str, Any]:
    return {
        "phase": phase,
        "title": title,
        "description": description,
        "objectives": objectives,
        "deliverables": deliverables,
        "priorities": priorities,
        "estimated_focus": estimated_focus,
    }


def _roadmap_templates_by_family(
    family: str,
    *,
    lang: str,
    fw: str,
    sdlc: str,
    ptype: str,
    timeline: str,
    team: str,
) -> list[dict[str, Any]]:
    timeline_note = f" ({timeline} timeline)" if timeline else ""
    team_note = f" for a {team.lower()} team" if team else ""

    if family == "spiral":
        return [
            _roadmap_phase_template(
                "1",
                "Planning",
                f"Define objectives, constraints, and success criteria for {ptype}{timeline_note}.",
                objectives=[
                    "Define problem statement and measurable goals",
                    "Identify stakeholders and decision points",
                    "Prepare initial scope and milestone plan",
                ],
                deliverables=["Project plan", "Scope baseline", "Initial risk list"],
                priorities=["Confirm must-have scope", "Align plan with timeline and team capacity", "Document assumptions"],
                estimated_focus="12%",
            ),
            _roadmap_phase_template(
                "2",
                "Risk Analysis",
                "Analyze technical, security, and delivery risks before major implementation.",
                objectives=[
                    "Identify high-risk modules and dependencies",
                    "Evaluate security and performance constraints",
                    "Define mitigation strategies per risk",
                ],
                deliverables=["Risk register", "Mitigation plan", "Review notes"],
                priorities=["Prioritize high-impact risks", "Link risks to architecture decisions", "Plan validation checkpoints"],
                estimated_focus="14%",
            ),
            _roadmap_phase_template(
                "3",
                "Prototype",
                f"Build focused prototypes for risky areas using {fw} and {lang}.",
                objectives=[
                    "Validate critical workflows with a prototype",
                    "Test integration points early",
                    "Collect feedback before full build",
                ],
                deliverables=["Working prototype", "Prototype evaluation notes", "Revised design decisions"],
                priorities=["Target highest-risk features first", "Keep prototype scope narrow", "Record lessons learned"],
                estimated_focus="18%",
            ),
            _roadmap_phase_template(
                "4",
                "Engineering",
                f"Implement production-quality modules with {fw} and {lang}{team_note}.",
                objectives=[
                    "Implement core modules and APIs",
                    "Apply coding standards and reviews",
                    "Integrate selected project features",
                ],
                deliverables=["Working MVP", "Feature increments", "Technical changelog"],
                priorities=["Build core CRUD/main workflows first", "Keep modules testable", "Review progress each milestone"],
                estimated_focus="32%",
            ),
            _roadmap_phase_template(
                "5",
                "Evaluation",
                "Review quality, risks, and readiness before wider release.",
                objectives=[
                    "Validate behavior against requirements",
                    "Review defects and technical debt",
                    "Decide next iteration or release readiness",
                ],
                deliverables=["Test summary", "Defect log", "Release readiness checklist"],
                priorities=["Test critical flows first", "Confirm security and data protection", "Document open issues"],
                estimated_focus="14%",
            ),
            _roadmap_phase_template(
                "6",
                "Next Iteration / Maintenance",
                "Plan improvements, fixes, and the next development cycle.",
                objectives=[
                    "Collect user/stakeholder feedback",
                    "Prioritize fixes and enhancements",
                    "Update documentation and support notes",
                ],
                deliverables=["Maintenance checklist", "Version 2 backlog", "Updated documentation"],
                priorities=["Address high-severity issues first", "Improve bottlenecks", "Plan next spiral cycle if needed"],
                estimated_focus="10%",
            ),
        ]

    if family == "vmodel":
        return [
            _roadmap_phase_template(
                "1",
                "Requirement Analysis",
                f"Define requirements and validation criteria for {ptype}.",
                objectives=["Capture functional requirements", "Define acceptance criteria", "Map requirements to tests"],
                deliverables=["Requirements specification", "Acceptance criteria list", "Traceability matrix"],
                priorities=["Confirm scope completeness", "Define non-functional requirements", "Align with stakeholders"],
                estimated_focus="15%",
            ),
            _roadmap_phase_template(
                "2",
                "System Design",
                f"Design architecture for {fw} on {lang}.",
                objectives=["Create system architecture diagram", "Define module boundaries", "Plan integration interfaces"],
                deliverables=["Architecture document", "Interface contracts", "Design review notes"],
                priorities=["Separate modules clearly", "Plan testability hooks", "Document design decisions"],
                estimated_focus="15%",
            ),
            _roadmap_phase_template(
                "3",
                "Module Design",
                "Prepare detailed module, database, and UI designs.",
                objectives=["Design database ERD", "Define API/service contracts", "Prepare UI flow or wireframes"],
                deliverables=["Detailed design specs", "Database ERD", "UI flow/wireframes"],
                priorities=["Define team responsibilities", "Prepare coding standards", "Validate design against requirements"],
                estimated_focus="15%",
            ),
            _roadmap_phase_template(
                "4",
                "Implementation",
                f"Build modules according to design using {fw}.",
                objectives=["Implement core business logic", "Integrate authentication if required", "Maintain modular code structure"],
                deliverables=["Implemented modules", "API endpoints/services", "Developer setup guide"],
                priorities=["Implement critical workflows first", "Keep commits small and reviewable", "Track feature completion"],
                estimated_focus="30%",
            ),
            _roadmap_phase_template(
                "5",
                "Verification & Validation",
                "Execute tests mapped to requirements and design levels.",
                objectives=["Run unit and integration tests", "Validate security and performance basics", "Fix defects before release"],
                deliverables=["Test reports", "Bug list and fixes", "Validation checklist"],
                priorities=["Test critical paths first", "Add regression tests", "Confirm role-based access if applicable"],
                estimated_focus="15%",
            ),
            _roadmap_phase_template(
                "6",
                "Deployment & Maintenance",
                "Deploy, verify, and maintain the system after release.",
                objectives=["Prepare production environment", "Deploy and smoke test", "Plan maintenance and monitoring"],
                deliverables=["Deployed system", "Deployment notes", "Maintenance checklist"],
                priorities=["Use staging before production", "Verify backups and rollback", "Monitor first release"],
                estimated_focus="10%",
            ),
        ]

    if family == "waterfall":
        return [
            _roadmap_phase_template("1", "Requirement Analysis", f"Document complete requirements for {ptype}.", objectives=["Define scope and constraints", "Identify users and roles", "List core and optional features"], deliverables=["SRS or scope document", "Feature list", "Initial risk list"], priorities=["Confirm must-have features", "Define non-functional requirements", "Freeze baseline scope"], estimated_focus="15%"),
            _roadmap_phase_template("2", "System Design", f"Design architecture, database, and UI for {fw}.", objectives=["Create architecture diagram", "Prepare database ERD", "Design major user flows"], deliverables=["Architecture plan", "Database ERD", "UI wireframes"], priorities=["Define module boundaries", "Assign team responsibilities", "Review design before coding"], estimated_focus="15%"),
            _roadmap_phase_template("3", "Implementation", f"Implement the full solution using {lang} and {fw}{team_note}.", objectives=["Build core modules", "Integrate selected features", "Follow coding standards"], deliverables=["Complete codebase", "Module documentation", "Changelog"], priorities=["Deliver modules in planned order", "Conduct code reviews", "Track scope changes carefully"], estimated_focus="35%"),
            _roadmap_phase_template("4", "Testing", "Validate functionality, security, and performance before deployment.", objectives=["Execute test cases", "Fix defects", "Prepare UAT materials"], deliverables=["Test report", "Bug fixes", "UAT sign-off"], priorities=["Test critical flows first", "Confirm data integrity", "Validate reporting features if included"], estimated_focus="20%"),
            _roadmap_phase_template("5", "Deployment", "Deploy the system and verify production readiness.", objectives=["Configure environments", "Deploy application and database", "Run smoke tests"], deliverables=["Deployed system", "Deployment guide", "Rollback plan"], priorities=["Stage before production", "Verify backups", "Monitor initial usage"], estimated_focus="10%"),
            _roadmap_phase_template("6", "Maintenance", "Support post-release fixes and improvements.", objectives=["Collect feedback", "Fix post-release defects", "Plan next version"], deliverables=["Maintenance log", "Version 2 backlog", "Updated docs"], priorities=["Prioritize severe defects", "Improve performance bottlenecks", "Keep documentation current"], estimated_focus="5%"),
        ]

    if family == "iterative":
        return [
            _roadmap_phase_template("1", "Initial Planning", f"Plan iterations and MVP scope for {ptype}{timeline_note}.", objectives=["Define MVP scope", "Prioritize modules", "Set iteration goals"], deliverables=["Iteration plan", "Prioritized backlog", "Milestone schedule"], priorities=["Focus on MVP first", "Control scope creep", "Align with team capacity"], estimated_focus="12%"),
            _roadmap_phase_template("2", "Core Version Development", f"Deliver the first working version with {fw}.", objectives=["Implement core workflows", "Set up project structure", "Establish baseline quality"], deliverables=["Core version build", "Setup documentation", "Sprint/iteration notes"], priorities=["Ship usable core flows", "Keep architecture modular", "Review after each iteration"], estimated_focus="28%"),
            _roadmap_phase_template("3", "Module Expansion", "Add remaining modules and selected features incrementally.", objectives=["Integrate additional features", "Refactor where needed", "Improve usability"], deliverables=["Expanded feature set", "Updated modules", "Change log"], priorities=["Add features in priority order", "Maintain test coverage", "Validate integrations"], estimated_focus="25%"),
            _roadmap_phase_template("4", "Testing & Feedback", "Test each increment and incorporate feedback.", objectives=["Run functional and regression tests", "Collect stakeholder feedback", "Fix high-priority defects"], deliverables=["Test results", "Feedback summary", "Defect fixes"], priorities=["Test new modules immediately", "Track recurring issues", "Validate security controls"], estimated_focus="15%"),
            _roadmap_phase_template("5", "Integration", "Integrate modules, data flows, and external services.", objectives=["Validate end-to-end workflows", "Resolve integration defects", "Confirm deployment configuration"], deliverables=["Integrated build", "Integration test notes", "Release candidate"], priorities=["Test cross-module flows", "Verify API contracts", "Confirm environment settings"], estimated_focus="12%"),
            _roadmap_phase_template("6", "Release & Improvement", "Release the product and plan the next improvement cycle.", objectives=["Deploy release", "Monitor stability", "Plan next iteration"], deliverables=["Production release", "Release notes", "Improvement backlog"], priorities=["Use staged rollout if possible", "Monitor errors and performance", "Document lessons learned"], estimated_focus="8%"),
        ]

    if family == "rad":
        return [
            _roadmap_phase_template("1", "Quick Requirement Gathering", f"Capture essential requirements quickly for {ptype}.", objectives=["Identify core users and goals", "Define MVP features", "Confirm constraints"], deliverables=["Short requirements brief", "Feature shortlist", "Quick risk list"], priorities=["Avoid over-analysis", "Focus on demo-ready scope", "Confirm timeline"], estimated_focus="12%"),
            _roadmap_phase_template("2", "Prototype Design", "Create prototypes for UI and core workflows.", objectives=["Design key screens", "Validate workflow assumptions", "Identify technical spikes"], deliverables=["UI prototype", "Workflow sketches", "Prototype review notes"], priorities=["Prioritize visible user flows", "Get early feedback", "Keep prototype focused"], estimated_focus="14%"),
            _roadmap_phase_template("3", "User Feedback", "Review prototype feedback and refine scope.", objectives=["Collect user comments", "Prioritize changes", "Update requirements"], deliverables=["Feedback summary", "Revised scope", "Updated prototype plan"], priorities=["Resolve conflicting feedback", "Protect MVP scope", "Document decisions"], estimated_focus="10%"),
            _roadmap_phase_template("4", "Rapid Development", f"Build the system rapidly using {lang} and {fw}.", objectives=["Implement MVP modules", "Integrate critical features", "Maintain frequent demos"], deliverables=["Working MVP", "Demo build", "Feature increments"], priorities=["Deliver visible progress early", "Refactor only when needed", "Keep modules independent"], estimated_focus="38%"),
            _roadmap_phase_template("5", "Testing & Refinement", "Test, refine, and stabilize before release.", objectives=["Run focused test cycles", "Fix critical defects", "Improve usability"], deliverables=["Test report", "Refined build", "Known issues list"], priorities=["Test core flows first", "Validate security basics", "Polish high-traffic screens"], estimated_focus="16%"),
            _roadmap_phase_template("6", "Deployment", "Deploy and hand over the solution.", objectives=["Prepare deployment package", "Configure environments", "Verify release"], deliverables=["Deployed app", "Deployment notes", "User guide updates"], priorities=["Smoke test after deploy", "Verify rollback steps", "Capture support notes"], estimated_focus="10%"),
        ]

    if family == "devops":
        return [
            _roadmap_phase_template("1", "Planning & Backlog", f"Plan delivery backlog and environments for {ptype}.", objectives=["Define backlog and priorities", "Plan environments", "Set quality gates"], deliverables=["Prioritized backlog", "Environment plan", "Definition of done"], priorities=["Keep backlog MVP-focused", "Define CI/CD goals", "Align with operations"], estimated_focus="12%"),
            _roadmap_phase_template("2", "Development", f"Implement features with {fw} and {lang}{team_note}.", objectives=["Build core services/modules", "Maintain trunk-based workflow", "Automate local checks"], deliverables=["Feature branches merged", "Core modules", "Developer docs"], priorities=["Small frequent integrations", "Code review every merge", "Keep modules testable"], estimated_focus="30%"),
            _roadmap_phase_template("3", "Continuous Integration", "Automate build, test, and quality checks.", objectives=["Set up CI pipeline", "Run automated tests on commits", "Track build health"], deliverables=["CI pipeline", "Build status dashboard", "Test automation baseline"], priorities=["Fail fast on broken builds", "Keep pipelines maintainable", "Add linting and basic security scans"], estimated_focus="18%"),
            _roadmap_phase_template("4", "Testing & Security Checks", "Validate releases with automated and manual checks.", objectives=["Run integration tests", "Check security basics", "Validate deployment artifacts"], deliverables=["Test reports", "Security checklist", "Release candidate"], priorities=["Automate regression where possible", "Review secrets and permissions", "Validate monitoring hooks"], estimated_focus="18%"),
            _roadmap_phase_template("5", "Deployment Automation", "Automate deployment to target environments.", objectives=["Configure deployment pipeline", "Prepare environment variables", "Run staged deployment"], deliverables=["Deployment pipeline", "Release notes", "Rollback script/plan"], priorities=["Deploy to staging first", "Verify backups", "Document release steps"], estimated_focus="14%"),
            _roadmap_phase_template("6", "Monitoring & Maintenance", "Monitor production and maintain reliability.", objectives=["Set up logging and alerts", "Track incidents", "Plan improvements"], deliverables=["Monitoring dashboard", "Incident log", "Maintenance backlog"], priorities=["Watch error rates after release", "Improve bottlenecks", "Keep runbooks updated"], estimated_focus="8%"),
        ]

    # Default Agile / Scrum style (6 phases)
    return [
        _roadmap_phase_template(
            "1",
            "Requirement Gathering",
            f"Clarify scope, users, roles, and success criteria for {ptype}{timeline_note}.",
            objectives=[
                "Define problem statement and project scope",
                "Identify users, roles, and permissions",
                "List core and optional features",
            ],
            deliverables=["Requirements checklist", "Feature list (MoSCoW)", "Initial risk list"],
            priorities=[
                "Confirm must-have features",
                "Define non-functional requirements",
                "Align scope with timeline and team capacity",
            ],
            estimated_focus="12%",
        ),
        _roadmap_phase_template(
            "2",
            "Planning & Design",
            f"Design architecture, database schema, and major flows for {fw} on {lang}.",
            objectives=[
                "Create system architecture diagram",
                "Prepare database ERD",
                "Design UI wireframes or screen flows",
            ],
            deliverables=["Architecture plan", "Database ERD", "UI flow/wireframe"],
            priorities=[
                "Separate modules clearly",
                "Define team responsibilities",
                "Prepare coding standards",
            ],
            estimated_focus="14%",
        ),
        _roadmap_phase_template(
            "3",
            "Sprint Development" if "scrum" in sdlc.lower() else "Development",
            f"Build features in priority order using {sdlc} practices{team_note}.",
            objectives=[
                "Implement authentication and authorization if required",
                "Build core modules first",
                "Integrate selected features gradually",
            ],
            deliverables=["Working MVP", "Feature increments", "Changelog"],
            priorities=[
                "Implement core CRUD/main workflows first",
                "Keep code modular and testable",
                "Review progress every milestone",
            ],
            estimated_focus="42%",
        ),
        _roadmap_phase_template(
            "4",
            "Testing & Review",
            "Validate behavior, security, performance, and usability before deployment.",
            objectives=[
                "Validate system behavior",
                "Test security, performance, and usability",
                "Fix defects before deployment",
            ],
            deliverables=["Test report", "Bug list and fixes", "Final validation checklist"],
            priorities=[
                "Test critical flows first",
                "Add regression tests for important modules",
                "Confirm role-based access and data protection",
            ],
            estimated_focus="16%",
        ),
        _roadmap_phase_template(
            "5",
            "Deployment",
            "Prepare environments, deploy, and verify the release.",
            objectives=[
                "Prepare production environment",
                "Configure database and environment variables",
                "Deploy and verify release",
            ],
            deliverables=["Deployed system", "Deployment notes", "Backup and rollback plan"],
            priorities=[
                "Use staging before production",
                "Verify backups and rollback steps",
                "Monitor first release",
            ],
            estimated_focus="8%",
        ),
        _roadmap_phase_template(
            "6",
            "Maintenance",
            "Plan post-release improvements, documentation, and future iterations.",
            objectives=[
                "Collect user feedback",
                "Fix post-release issues",
                "Plan next version",
            ],
            deliverables=["Maintenance checklist", "Backlog for version 2", "Documentation updates"],
            priorities=[
                "Address high-severity issues first",
                "Improve performance bottlenecks",
                "Update documentation and support notes",
            ],
            estimated_focus="8%",
        ),
    ]


def _apply_roadmap_context(
    phase: dict[str, Any],
    data: DecisionReportData,
    input_data: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    """Add project-specific bullets to roadmap phases (display only)."""
    out = dict(phase)
    ctx = {**dict(data.reason_context or {}), **dict(input_data or {})}
    title_l = str(out.get("title", "")).lower()
    features_blob = _format_features(ctx.get("selected_features"), default="").lower()
    security = _ctx_label(ctx.get("security_requirements")).lower()
    performance = _ctx_label(ctx.get("performance_requirements")).lower()
    deployment = _ctx_label(ctx.get("deployment_preference")).lower()
    timeline = _ctx_label(ctx.get("timeline")).lower()
    team = _ctx_label(ctx.get("team_size")).lower()

    def add_unique(key: str, text: str) -> None:
        items = list(out.get(key) or [])
        if text and text not in items:
            items.append(text)
        out[key] = items[:5]

    if any(k in features_blob for k in ("auth", "login", "role", "access")):
        if any(k in title_l for k in ("develop", "engineer", "sprint", "implement", "rapid")):
            add_unique("priorities", "Implement access control, roles, and protected routes early")
            add_unique("objectives", "Define authentication and authorization requirements")

    if any(k in features_blob for k in ("report", "analytic", "dashboard")):
        if any(k in title_l for k in ("test", "develop", "engineer", "implement")):
            add_unique("deliverables", "Validated report queries and dashboard views")
            add_unique("priorities", "Test report generation and export accuracy")

    if any(k in features_blob for k in ("real-time", "realtime", "chat", "notification")):
        if any(k in title_l for k in ("develop", "test", "engineer", "integration")):
            add_unique("priorities", "Test event flow, notifications, and connection handling")
            add_unique("objectives", "Validate real-time update behavior under load")

    if "high" in security:
        for key in ("objectives", "priorities"):
            if any(k in title_l for k in ("test", "risk", "engineer", "develop", "verification")):
                add_unique(key, "Review input validation, access control, and audit logging")

    if "high" in performance:
        if any(k in title_l for k in ("test", "engineer", "develop", "evaluation")):
            add_unique("priorities", "Run performance checks, query optimization, and caching review")

    if deployment and any(k in title_l for k in ("deploy", "release", "cutover", "maintenance")):
        if "cloud" in deployment:
            add_unique("priorities", "Configure cloud environment variables, monitoring, and backup/rollback")
        elif "local" in deployment:
            add_unique("priorities", "Prepare local installer/package and offline/device testing steps")

    if timeline and any(w in timeline for w in ("short", "tight", "1 month", "2 month")):
        if any(k in title_l for k in ("requirement", "planning", "develop", "sprint")):
            add_unique("priorities", "Prioritize MVP features and timebox non-critical scope")

    if team and any(w in team for w in ("1", "2", "3", "small")):
        if any(k in title_l for k in ("plan", "develop", "sprint")):
            add_unique("priorities", "Control scope and avoid parallel work beyond team capacity")

    fw = _ctx_label(data.recommended_framework)
    lang = _ctx_label(data.recommended_language)
    if fw and lang and any(k in title_l for k in ("design", "develop", "engineer", "sprint")):
        desc = str(out.get("description", ""))
        if fw.lower() not in desc.lower():
            out["description"] = f"{desc} Uses {lang} with {fw}.".strip()

    return out


def build_project_roadmap_section(
    data: DecisionReportData,
    input_data: Optional[Mapping[str, Any]] = None,
) -> Optional[ft.Control]:
    """Full-width Suggested Project Roadmap section (below Skill Gap)."""
    return build_roadmap_card(data, input_data=input_data)


def build_roadmap_card(
    data: DecisionReportData,
    input_data: Optional[Mapping[str, Any]] = None,
) -> Optional[ft.Control]:
    phases = resolve_roadmap_phases_for_display(data, input_data=input_data)
    if not phases:
        return None

    phase_cards = [
        ft.Container(
            col={"xs": 12, "sm": 6, "md": 4},
            content=build_roadmap_phase_card(phase, idx),
        )
        for idx, phase in enumerate(phases)
    ]

    return _glass_card(
        ft.Column(
            spacing=14,
            controls=[
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Column(
                            spacing=4,
                            tight=True,
                            expand=True,
                            controls=[
                                ft.Text(
                                    "Suggested Project Roadmap",
                                    size=17,
                                    weight=ft.FontWeight.W_600,
                                    color=_C_PRIMARY,
                                ),
                                ft.Text(
                                    "A presentation-friendly delivery plan for the project.",
                                    size=13,
                                    color=_C_SECONDARY,
                                ),
                            ],
                        ),
                        ft.Container(
                            content=ft.Text(
                                f"{len(phases)} phases",
                                size=11,
                                weight=ft.FontWeight.W_600,
                                color=_C_SUCCESS,
                            ),
                            bgcolor=ft.colors.with_opacity(0.12, _C_SUCCESS),
                            border=ft.border.all(1, ft.colors.with_opacity(0.35, _C_SUCCESS)),
                            border_radius=Radii.pill,
                            padding=ft.padding.symmetric(horizontal=10, vertical=4),
                        ),
                    ],
                ),
                ft.ResponsiveRow(spacing=_CARD_GAP, run_spacing=_CARD_GAP, controls=phase_cards),
            ],
        )
    )


def resolve_roadmap_phases_for_display(
    data: DecisionReportData,
    input_data: Optional[Mapping[str, Any]] = None,
) -> list[dict[str, Any]]:
    """Normalize, enrich, or fall back to contextual roadmap phases (display only)."""
    fallback = generate_contextual_roadmap_fallback(data, input_data=input_data)
    raw = list(data.roadmap_phases or [])

    if not raw:
        return [_apply_roadmap_context(phase, data, input_data) for phase in fallback]

    enriched = [
        enrich_roadmap_item_if_needed(item, idx, data, fallback, input_data=input_data)
        for idx, item in enumerate(raw)
    ]

    if _should_use_full_roadmap_fallback(enriched):
        return [_apply_roadmap_context(phase, data, input_data) for phase in fallback]

    if len(enriched) < len(fallback):
        for idx in range(len(enriched), min(len(fallback), 6)):
            enriched.append(
                _apply_roadmap_context(
                    enrich_roadmap_item_if_needed({}, idx, data, fallback, input_data=input_data),
                    data,
                    input_data,
                )
            )

    return enriched[:6]


def _should_use_full_roadmap_fallback(phases: list[dict[str, Any]]) -> bool:
    if len(phases) < 5:
        return True
    scores = [_phase_content_score(phase) for phase in phases]
    return (sum(scores) / max(len(scores), 1)) < 160


def _phase_content_score(phase: dict[str, Any]) -> int:
    total = len(str(phase.get("description", "") or ""))
    for key in ("objectives", "deliverables", "priorities"):
        for item in phase.get(key) or []:
            total += len(str(item))
    return total


def normalize_roadmap_item(
    phase_item: Mapping[str, Any],
    index: int,
    data: DecisionReportData,
    input_data: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    p = dict(phase_item or {})
    return {
        "phase": str(p.get("phase") or p.get("phase_number") or index + 1),
        "title": str(p.get("title") or p.get("name") or f"Phase {index + 1}").strip(),
        "description": str(p.get("description") or "").strip(),
        "objectives": _as_string_list(p.get("objectives") or p.get("tasks")),
        "deliverables": _as_string_list(p.get("deliverables")),
        "priorities": _as_string_list(p.get("priorities")),
        "estimated_focus": _normalize_focus_label(
            p.get("estimated_focus") or p.get("focus") or ""
        ),
    }


def enrich_roadmap_item_if_needed(
    phase_item: Mapping[str, Any],
    index: int,
    data: DecisionReportData,
    template_phases: list[dict[str, Any]],
    input_data: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    normalized = normalize_roadmap_item(phase_item, index, data, input_data)
    if _phase_content_score(normalized) >= 220:
        return _apply_roadmap_context(normalized, data, input_data)

    template = template_phases[index] if index < len(template_phases) else template_phases[-1]
    merged = dict(template)
    merged["phase"] = normalized["phase"] or template.get("phase")

    if len(normalized["title"]) > 8 and normalized["title"].lower() != f"phase {index + 1}".lower():
        merged["title"] = normalized["title"]
    if len(normalized["description"]) >= 50:
        merged["description"] = normalized["description"]
    if normalized["estimated_focus"]:
        merged["estimated_focus"] = normalized["estimated_focus"]

    for key in ("objectives", "deliverables", "priorities"):
        norm_items = normalized[key]
        tmpl_items = list(template.get(key) or [])
        if len(norm_items) >= 2 and sum(len(x) for x in norm_items) >= 40:
            merged[key] = norm_items[:5]
        else:
            merged[key] = tmpl_items[:5]

    return _apply_roadmap_context(merged, data, input_data)


def generate_contextual_roadmap_fallback(
    data: DecisionReportData,
    input_data: Optional[Mapping[str, Any]] = None,
) -> list[dict[str, Any]]:
    """Six-phase presentation roadmap keyed by recommended SDLC (display only)."""
    family = _sdlc_roadmap_family(data.recommended_sdlc)
    ctx = {**dict(data.reason_context or {}), **dict(input_data or {})}
    lang = _ctx_label(data.recommended_language) or "the selected language"
    fw = _ctx_label(data.recommended_framework) or "the selected framework"
    sdlc = _ctx_label(data.recommended_sdlc) or "the selected SDLC"
    ptype = _ctx_label(data.project_type) or "this project"
    timeline = _ctx_label(ctx.get("timeline") or data.reason_context.get("timeline"))
    team = _ctx_label(ctx.get("team_size"))

    templates = _roadmap_templates_by_family(
        family,
        lang=lang,
        fw=fw,
        sdlc=sdlc,
        ptype=ptype,
        timeline=timeline,
        team=team,
    )
    return [dict(phase) for phase in templates]


def build_roadmap_phase_card(phase: dict[str, Any], index: int) -> ft.Control:
    """Single roadmap phase card for the responsive grid."""
    phase_no = str(phase.get("phase", "") or index + 1)
    title = str(phase.get("title", "") or f"Phase {phase_no}")
    desc = str(phase.get("description", "") or "").strip()
    focus = _normalize_focus_label(phase.get("estimated_focus", "") or "")

    list_blocks: list[ft.Control] = []
    for label, key in (
        ("Objectives", "objectives"),
        ("Deliverables", "deliverables"),
        ("Priorities", "priorities"),
    ):
        block = build_roadmap_list_block(label, list(phase.get(key) or []))
        if block is not None:
            list_blocks.append(block)

    body: list[ft.Control] = [
        ft.Text(f"PHASE {phase_no}", size=10, weight=ft.FontWeight.W_700, color=_C_CYAN),
        ft.Text(title, size=15, weight=ft.FontWeight.W_600, color=_C_PRIMARY, selectable=True),
    ]
    if desc:
        body.append(
            ft.Text(desc, size=12, color=_C_SECONDARY, selectable=True),
        )
    if focus:
        body.append(
            ft.Text(
                f"ESTIMATED FOCUS: {focus}",
                size=10,
                weight=ft.FontWeight.W_700,
                color=_C_MUTED,
            )
        )
    body.extend(list_blocks)

    return _inner_card(ft.Column(spacing=8, controls=body), padding=14)


def build_roadmap_list_block(title: str, items: list[str]) -> Optional[ft.Control]:
    bullets = [str(i).strip() for i in items if str(i).strip()]
    if not bullets:
        return None
    return ft.Column(
        spacing=4,
        controls=[
            ft.Text(title.upper(), size=10, weight=ft.FontWeight.W_700, color=_C_MUTED),
            ft.Column(
                spacing=3,
                controls=[_mini_bullet(item) for item in bullets[:5]],
            ),
        ],
    )


def chunk_items(items: list[Any], chunk_size: int) -> list[list[Any]]:
    if chunk_size <= 0:
        return [items]
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]


def build_feedback_and_report_actions_section(
    theme: Mapping[str, Any],
    *,
    show_feedback: bool = False,
    existing_feedback: Optional[RecommendationFeedback] = None,
    feedback_section_ref: Optional[ft.Ref[ft.Container]] = None,
    feedback_rating_ref: Optional[ft.Ref[ft.RadioGroup]] = None,
    feedback_comment_ref: Optional[ft.Ref[ft.TextField]] = None,
    feedback_error_ref: Optional[ft.Ref[ft.Text]] = None,
    feedback_success_ref: Optional[ft.Ref[ft.Text]] = None,
    feedback_submit_btn_ref: Optional[ft.Ref[ft.Container]] = None,
    on_submit_feedback: Optional[Callable[[ft.ControlEvent], None]] = None,
    on_generate_another: Callable[[ft.ControlEvent], None],
    on_history: Callable[[ft.ControlEvent], None],
    on_dashboard: Optional[Callable[[ft.ControlEvent], None]] = None,
    on_copy_summary: Optional[Callable[[ft.ControlEvent], None]] = None,
) -> Optional[ft.Control]:
    """Bottom row: Feedback (~65%) + Report Actions (~35%)."""
    actions = build_report_actions_card(
        on_generate_another=on_generate_another,
        on_history=on_history,
        on_dashboard=on_dashboard,
        on_copy_summary=on_copy_summary,
    )

    if not show_feedback:
        return ft.ResponsiveRow(
            spacing=_SECTION_GAP,
            run_spacing=_SECTION_GAP,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[ft.Container(col={"xs": 12}, content=actions)],
        )

    feedback = build_feedback_card(
        theme,
        existing_feedback=existing_feedback,
        section_ref=feedback_section_ref,
        rating_ref=feedback_rating_ref,
        comment_ref=feedback_comment_ref,
        error_ref=feedback_error_ref,
        success_ref=feedback_success_ref,
        submit_btn_ref=feedback_submit_btn_ref,
        on_submit=on_submit_feedback,
        can_submit=existing_feedback is None and on_submit_feedback is not None,
    )

    return ft.ResponsiveRow(
        spacing=_SECTION_GAP,
        run_spacing=_SECTION_GAP,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[
            ft.Container(col={"xs": 12, "lg": 8}, content=feedback),
            ft.Container(col={"xs": 12, "lg": 4}, content=actions),
        ],
    )


def build_feedback_card(
    theme: Mapping[str, Any],
    *,
    existing_feedback: Optional[RecommendationFeedback],
    section_ref: Optional[ft.Ref[ft.Container]],
    rating_ref: Optional[ft.Ref[ft.RadioGroup]],
    comment_ref: Optional[ft.Ref[ft.TextField]],
    error_ref: Optional[ft.Ref[ft.Text]],
    success_ref: Optional[ft.Ref[ft.Text]],
    submit_btn_ref: Optional[ft.Ref[ft.Container]] = None,
    on_submit: Optional[Callable[[ft.ControlEvent], None]] = None,
    can_submit: bool = True,
) -> ft.Control:
    """Feedback card: saved entries panel + optional submit form."""
    return ft.Container(
        key="recommendation_feedback_section",
        ref=section_ref,
        visible=True,
        content=build_feedback_card_content(
            theme,
            existing_feedback=existing_feedback,
            rating_ref=rating_ref,
            comment_ref=comment_ref,
            error_ref=error_ref,
            success_ref=success_ref,
            submit_btn_ref=submit_btn_ref,
            on_submit=on_submit,
            can_submit=can_submit,
        ),
    )


def build_feedback_card_content(
    theme: Mapping[str, Any],
    *,
    existing_feedback: Optional[RecommendationFeedback],
    rating_ref: Optional[ft.Ref[ft.RadioGroup]] = None,
    comment_ref: Optional[ft.Ref[ft.TextField]] = None,
    error_ref: Optional[ft.Ref[ft.Text]] = None,
    success_ref: Optional[ft.Ref[ft.Text]] = None,
    submit_btn_ref: Optional[ft.Ref[ft.Container]] = None,
    on_submit: Optional[Callable[[ft.ControlEvent], None]] = None,
    can_submit: bool = True,
) -> ft.Control:
    """Inner feedback card body (used for in-place refresh after submit)."""
    entries = [existing_feedback] if existing_feedback is not None else []
    entry_count = len(entries)

    header = ft.Row(
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[
            ft.Column(
                spacing=4,
                tight=True,
                expand=True,
                controls=[
                    ft.Text("Feedback", size=17, weight=ft.FontWeight.W_600, color=_C_PRIMARY),
                    ft.Text(
                        "Saved feedback entries linked to this recommendation.",
                        size=12,
                        color=_C_SECONDARY,
                    ),
                ],
            ),
            ft.Container(
                content=ft.Text(
                    f"{entry_count} {'entry' if entry_count == 1 else 'entries'}",
                    size=11,
                    weight=ft.FontWeight.W_600,
                    color=_C_MUTED,
                ),
                border=ft.border.all(1, _C_INNER_BD),
                border_radius=Radii.pill,
                padding=ft.padding.symmetric(horizontal=10, vertical=4),
            ),
        ],
    )

    body_controls: list[ft.Control] = [
        header,
        build_saved_feedback_panel(entries),
    ]

    if can_submit and on_submit is not None:
        error_text = ft.Text("", size=12, color=_C_WARNING, ref=error_ref, visible=False)
        success_text = ft.Text("", size=12, color=_C_CYAN, ref=success_ref, visible=False)

        comment_field = input_field(
            "Comment",
            hint="Share a short comment about this recommendation.",
            multiline=True,
            min_lines=3,
            max_lines=4,
            theme=theme,
        )
        comment_field.ref = comment_ref
        comment_field.bgcolor = _C_INNER
        comment_field.border_color = _C_INNER_BD

        submit_btn = primary_button(
            "Submit Feedback",
            on_click=on_submit,
            icon=ft.icons.SEND_ROUNDED,
            theme=theme,
            mint_fill=True,
            border_radius=Radii.pill,
            ref=submit_btn_ref,
        )

        body_controls.extend(
            [
                ft.Container(height=4),
                ft.Text("Rating", size=12, weight=ft.FontWeight.W_600, color=_C_MUTED),
                build_rating_selector(rating_ref),
                comment_field,
                submit_btn,
                error_text,
                success_text,
            ]
        )
    elif existing_feedback is not None:
        body_controls.append(
            ft.Text(
                "Feedback already submitted for this recommendation.",
                size=12,
                color=_C_MUTED,
                italic=True,
            )
        )

    body_controls.append(
        ft.Text(
            "Your feedback helps improve future decision reports.",
            size=11,
            color=_C_MUTED,
            italic=True,
        )
    )

    return _glass_card(ft.Column(spacing=12, controls=body_controls), padding=20)


def build_saved_feedback_panel(
    entries: list[RecommendationFeedback],
) -> ft.Control:
    """Saved feedback list (0, 1, or more entries)."""
    if not entries:
        return _inner_card(
            ft.Text(
                "No feedback has been submitted for this recommendation yet.",
                size=13,
                color=_C_MUTED,
            ),
            padding=16,
        )

    cards = [build_saved_feedback_entry_card(entry) for entry in entries]
    return ft.Column(spacing=8, controls=cards)


def build_saved_feedback_entry_card(entry: RecommendationFeedback) -> ft.Control:
    rating_line = f"Rating: {max(1, min(5, int(entry.rating)))}/5"
    comment_line = f"Comment: {entry.comment.strip() if entry.comment else '—'}"
    submitted_line = f"Submitted: {_format_feedback_submitted_date(entry.created_at)}"

    return _inner_card(
        ft.Column(
            spacing=6,
            controls=[
                ft.Text(rating_line, size=13, weight=ft.FontWeight.W_600, color=_C_CYAN),
                ft.Text(comment_line, size=13, color=_C_SECONDARY, selectable=True),
                ft.Text(submitted_line, size=11, color=_C_MUTED),
            ],
        ),
        padding=14,
    )


def build_feedback_section(
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
    """Backward-compatible alias for ``build_feedback_card``."""
    return build_feedback_card(
        theme,
        existing_feedback=existing_feedback,
        section_ref=section_ref,
        rating_ref=rating_ref,
        comment_ref=comment_ref,
        error_ref=error_ref,
        success_ref=success_ref,
        on_submit=on_submit,
    )


def build_rating_selector(
    rating_ref: Optional[ft.Ref[ft.RadioGroup]],
) -> ft.Control:
    """Horizontal 1–5 star rating (RadioGroup values preserved for save logic)."""
    return ft.RadioGroup(
        ref=rating_ref,
        value=None,
        content=ft.Row(
            spacing=14,
            wrap=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Radio(
                    value=str(n),
                    label=f"{n} ★",
                    label_style=ft.TextStyle(size=13, color=_C_PRIMARY),
                )
                for n in range(1, 6)
            ],
        ),
    )


def build_report_actions_card(
    *,
    on_generate_another: Callable[[ft.ControlEvent], None],
    on_history: Callable[[ft.ControlEvent], None],
    on_dashboard: Optional[Callable[[ft.ControlEvent], None]] = None,
    on_copy_summary: Optional[Callable[[ft.ControlEvent], None]] = None,
) -> ft.Control:
    """Compact report actions for the bottom-right column."""
    buttons: list[ft.Control] = [
        build_report_action_button(
            "Generate Another",
            ft.icons.AUTO_AWESOME,
            on_generate_another,
            primary=True,
        ),
    ]
    if on_dashboard:
        buttons.append(
            build_report_action_button(
                "View Dashboard",
                ft.icons.DASHBOARD_OUTLINED,
                on_dashboard,
            )
        )
    buttons.append(
        build_report_action_button("View History", ft.icons.HISTORY, on_history)
    )
    if on_copy_summary:
        buttons.append(
            build_report_action_button(
                "Copy Summary",
                ft.icons.CONTENT_COPY_OUTLINED,
                on_copy_summary,
            )
        )

    return _glass_card(
        ft.Column(
            spacing=10,
            controls=[
                _section_title(
                    "Report Actions",
                    subtitle="Continue after reviewing this recommendation.",
                ),
                ft.Column(spacing=8, controls=buttons),
                ft.Text(
                    "You can generate another report, review saved results, or copy "
                    "this recommendation summary.",
                    size=11,
                    color=_C_MUTED,
                    italic=True,
                ),
            ],
        ),
        padding=18,
    )


def build_report_action_button(
    label: str,
    icon: str,
    on_click: Callable[[ft.ControlEvent], None],
    *,
    primary: bool = False,
) -> ft.Control:
    """Full-width action button inside the Report Actions card."""
    action = _primary_action if primary else _outline_action
    return ft.Row(
        controls=[
            ft.Container(
                expand=True,
                content=action(label, icon, on_click),
            ),
        ],
    )


def build_quick_actions_card(
    *,
    on_generate_another: Callable[[ft.ControlEvent], None],
    on_history: Callable[[ft.ControlEvent], None],
    on_dashboard: Optional[Callable[[ft.ControlEvent], None]] = None,
    on_copy_summary: Optional[Callable[[ft.ControlEvent], None]] = None,
    on_feedback: Optional[Callable[[ft.ControlEvent], None]] = None,
) -> ft.Control:
    buttons: list[ft.Control] = [
        _outline_action("Generate Another", ft.icons.AUTO_AWESOME, on_generate_another),
    ]
    if on_dashboard:
        buttons.append(_outline_action("View Dashboard", ft.icons.DASHBOARD_OUTLINED, on_dashboard))
    buttons.append(_outline_action("View History", ft.icons.HISTORY, on_history))
    if on_copy_summary:
        buttons.append(_outline_action("Copy Summary", ft.icons.CONTENT_COPY_OUTLINED, on_copy_summary))
    if on_feedback:
        buttons.append(_primary_action("Submit Feedback", ft.icons.RATE_REVIEW_OUTLINED, on_feedback))

    return _glass_card(
        ft.Column(
            spacing=10,
            controls=[_section_title("Quick Actions"), *buttons],
        ),
        padding=18,
    )


# ---------- internal layout helpers ----------


def _left_column(
    data: DecisionReportData,
    theme: Mapping[str, Any],
) -> list[ft.Control]:
    sections: list[ft.Control] = []

    pref = build_user_preference_card(data)
    if pref is not None:
        sections.append(pref)

    return sections


def _roadmap_phase_card(phase: dict[str, Any], index: int) -> ft.Control:
    """Backward-compatible alias for ``build_roadmap_phase_card``."""
    return build_roadmap_phase_card(phase, index)


def _why_block(title: str, points: list[str], fallback: str) -> Optional[ft.Control]:
    bullets = [p for p in points if p.strip()]
    if not bullets and fallback.strip():
        bullets = _text_to_points(fallback)
    if not bullets:
        return None
    return ft.Column(
        spacing=8,
        controls=[
            ft.Text(title, size=14, weight=ft.FontWeight.W_600, color=_C_PRIMARY),
            ft.Column(spacing=4, controls=[_bullet(p) for p in bullets]),
        ],
    )


def _impact_label_for_badge(raw: str) -> str:
    """Short High/Medium/Low label for the pill; long engine strings stay in reason text."""
    s = (raw or "Medium").strip() or "Medium"
    low = s.lower()
    if low in ("high", "medium", "low"):
        return s.title()
    if len(s) <= 18:
        return s
    if any(w in low for w in ("critical", "severe", "significant")) or "high" in low:
        return "High"
    if "low" in low or "minor" in low:
        return "Low"
    return "Medium"


def _impact_badge(impact: str) -> ft.Control:
    label = _impact_label_for_badge(impact)
    level = label.lower()
    if "high" in level:
        color = _C_WARNING
    elif "low" in level:
        color = _C_MUTED
    else:
        color = _C_CYAN
    return ft.Container(
        content=ft.Text(
            label,
            size=10,
            weight=ft.FontWeight.W_700,
            color=_C_PRIMARY,
            no_wrap=True,
        ),
        bgcolor=ft.colors.with_opacity(0.18, color),
        border=ft.border.all(1, ft.colors.with_opacity(0.4, color)),
        border_radius=Radii.pill,
        padding=ft.padding.symmetric(horizontal=8, vertical=3),
    )


def _glass_card(
    body: ft.Control,
    *,
    padding: int = _PANEL_PAD,
    border_color: Optional[str] = None,
) -> ft.Control:
    return ft.Container(
        bgcolor=_C_PANEL,
        border=ft.border.all(1, border_color or _C_PANEL_BD),
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
            spacing=6,
            tight=True,
            controls=[
                ft.Icon(ft.icons.DESCRIPTION_OUTLINED, size=12, color=_C_CYAN),
                ft.Text(
                    "RECOMMENDATION DETAILS",
                    size=10,
                    weight=ft.FontWeight.W_700,
                    color=_C_CYAN,
                ),
            ],
        ),
        bgcolor=ft.colors.with_opacity(0.1, _C_CYAN),
        border=ft.border.all(1, ft.colors.with_opacity(0.35, _C_CYAN)),
        border_radius=Radii.pill,
        padding=ft.padding.symmetric(horizontal=10, vertical=5),
    )


def _meta_chip(label: str, value: str) -> ft.Control:
    return _inner_card(
        ft.Column(
            spacing=4,
            tight=True,
            controls=[
                ft.Text(label.upper(), size=10, weight=ft.FontWeight.W_700, color=_C_MUTED),
                ft.Text(value, size=14, weight=ft.FontWeight.W_700, color=_C_PRIMARY),
            ],
        ),
        padding=12,
    )


def _header_confidence_badge(text: str) -> ft.Control:
    return ft.Container(
        content=ft.Text(text, size=12, weight=ft.FontWeight.W_600, color=_C_CYAN),
        bgcolor=ft.colors.with_opacity(0.1, _C_CYAN),
        border=ft.border.all(1, ft.colors.with_opacity(0.22, _C_CYAN)),
        border_radius=Radii.pill,
        padding=ft.padding.symmetric(horizontal=12, vertical=5),
    )


def _header_meta_chip(label: str, value: str) -> ft.Control:
    return ft.Container(
        bgcolor=_C_INNER,
        border=ft.border.all(1, _C_INNER_BD),
        border_radius=14,
        padding=ft.padding.symmetric(horizontal=14, vertical=12),
        content=ft.Column(
            spacing=4,
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Text(label.upper(), size=10, weight=ft.FontWeight.W_700, color=_C_MUTED),
                ft.Text(
                    value,
                    size=15,
                    weight=ft.FontWeight.W_700,
                    color=_C_PRIMARY,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
        ),
    )


def _profile_kv(label: str, value: str, *, wide: bool = False) -> ft.Control:
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
                max_lines=8 if wide else 3,
            ),
        ],
    )


def _table_head_cell(text: str, flex: int) -> ft.Control:
    return ft.Container(
        expand=flex,
        content=ft.Text(text.upper(), size=10, weight=ft.FontWeight.W_700, color=_C_MUTED),
    )


def _table_body_cell(text: str, flex: int) -> ft.Container:
    return ft.Container(
        expand=flex,
        content=ft.Text(text, size=12, color=_C_SECONDARY, selectable=True),
    )


def _outline_action(label: str, icon: str, on_click: Callable[[ft.ControlEvent], None]) -> ft.Control:
    return ft.Container(
        height=38,
        bgcolor=_C_INNER,
        border=ft.border.all(1, _C_PANEL_BD),
        border_radius=12,
        alignment=ft.alignment.center,
        ink=True,
        on_click=on_click,
        padding=ft.padding.symmetric(horizontal=14),
        content=ft.Row(
            spacing=6,
            tight=True,
            controls=[
                ft.Icon(icon, size=16, color=_C_SECONDARY),
                ft.Text(label, size=12, weight=ft.FontWeight.W_600, color=_C_PRIMARY),
            ],
        ),
    )


def _primary_action(label: str, icon: str, on_click: Callable[[ft.ControlEvent], None]) -> ft.Control:
    return ft.Container(
        height=38,
        bgcolor=_C_CYAN,
        border_radius=12,
        alignment=ft.alignment.center,
        ink=True,
        on_click=on_click,
        padding=ft.padding.symmetric(horizontal=14),
        content=ft.Row(
            spacing=6,
            tight=True,
            controls=[
                ft.Icon(icon, size=16, color="#06111F"),
                ft.Text(label, size=12, weight=ft.FontWeight.W_600, color="#06111F"),
            ],
        ),
    )


def _bullet(text: str) -> ft.Control:
    return ft.Row(
        spacing=8,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[
            ft.Container(
                width=6,
                height=6,
                border_radius=999,
                bgcolor=_C_CYAN,
                margin=ft.margin.only(top=6),
            ),
            ft.Text(text, size=12, color=_C_SECONDARY, expand=True),
        ],
    )


def _mini_bullet(text: str) -> ft.Control:
    return ft.Text(f"• {text}", size=11, color=_C_SECONDARY)


def _format_feedback_submitted_date(dt: Any) -> str:
    if isinstance(dt, datetime):
        return dt.strftime("%b %d, %Y")
    return str(dt or "—")


def _rating_stars_label(rating: int) -> str:
    rating = max(1, min(5, int(rating)))
    return f"{'★' * rating}{'☆' * (5 - rating)}  ({rating}/5)"


def _confidence_int(result: dict[str, Any]) -> int:
    try:
        score = int(round(float(result.get("confidence_score", 0))))
    except (TypeError, ValueError):
        score = 0
    return max(0, min(100, score))


def _display(value: Any, *, default: str = "Not specified") -> str:
    if value is None:
        return default
    if isinstance(value, list):
        parts = [str(v).strip() for v in value if str(v).strip()]
        return ", ".join(parts) if parts else default
    text = str(value).strip()
    return text if text else default


def _text_to_points(text: str) -> list[str]:
    raw = (text or "").strip()
    if not raw:
        return []
    parts = re.split(r"[.\n]\s+", raw)
    return [p.strip() for p in parts if len(p.strip()) > 12][:6]


def _why_points_from_explanation(expl: dict) -> tuple[list[str], list[str], list[str]]:
    lang: list[str] = []
    fw: list[str] = []
    sdlc: list[str] = []
    for key, target in (
        ("why_language", lang),
        ("why_framework", fw),
        ("why_sdlc", sdlc),
    ):
        section = expl.get(key) or {}
        if isinstance(section, dict):
            target.extend([str(p) for p in (section.get("points") or []) if str(p).strip()])
    return lang, fw, sdlc


def _parse_explanation_text(raw: str) -> tuple[str, dict[str, str]]:
    if not raw.strip():
        return "", {}
    whys: dict[str, str] = {}
    markers = (
        ("language", "Language:"),
        ("framework", "Framework:"),
        ("sdlc", "SDLC:"),
    )
    summary_parts: list[str] = []
    for block in re.split(r"\n\s*\n", raw):
        block = block.strip()
        if not block:
            continue
        matched = False
        for key, prefix in markers:
            if block.startswith(prefix):
                whys[key] = block
                matched = True
                break
        if not matched:
            summary_parts.append(block)
    return "\n\n".join(summary_parts).strip(), whys


def _profile_fields_from_rec(rec: Recommendation, profile: dict) -> list[tuple[str, str]]:
    name = (rec.project_name or "").strip() or "Untitled Project"
    return [
        ("Project Name", name),
        ("Project Type", _display(rec.project_type, default="—")),
        ("Selected Features", _format_features(profile.get("selected_features"), default="—")),
        ("Team Size", _display(rec.team_size, default="—")),
        ("Complexity", _display(rec.complexity, default="—")),
        ("Preferred Platform", _display(profile.get("preferred_platform") or rec.platform, default="—")),
        (
            "Development Experience",
            _display(profile.get("development_experience") or rec.experience, default="—"),
        ),
        ("Timeline", _display(rec.timeline, default="—")),
        ("Project Goal", _display(profile.get("project_goal") or rec.project_goal, default="—")),
        ("Scalability Needs", _display(profile.get("scalability_needs") or rec.scalability, default="—")),
        (
            "Security Requirements",
            _display(profile.get("security_requirements") or rec.security, default="—"),
        ),
        ("Performance Requirements", _display(profile.get("performance_requirements"), default="—")),
        ("Budget Constraints", _display(profile.get("budget_constraints"), default="—")),
        (
            "Maintenance Expectations",
            _display(profile.get("maintenance_expectations"), default="—"),
        ),
        ("Deployment Preference", _display(profile.get("deployment_preference"), default="—")),
    ]


def _profile_fields_from_input(inp: dict) -> list[tuple[str, str]]:
    name = str(inp.get("project_name", "") or "").strip() or "Untitled Project"
    return [
        ("Project Name", name),
        ("Project Type", _display(inp.get("project_type"), default="—")),
        ("Selected Features", _format_features(inp.get("selected_features"), default="—")),
        ("Team Size", _display(inp.get("team_size"), default="—")),
        ("Complexity", _display(inp.get("complexity"), default="—")),
        ("Preferred Platform", _display(inp.get("preferred_platform"), default="—")),
        ("Development Experience", _display(inp.get("development_experience"), default="—")),
        ("Timeline", _display(inp.get("timeline"), default="—")),
        ("Project Goal", _display(inp.get("project_goal"), default="—")),
        ("Scalability Needs", _display(inp.get("scalability_needs"), default="—")),
        ("Security Requirements", _display(inp.get("security_requirements"), default="—")),
        ("Performance Requirements", _display(inp.get("performance_requirements"), default="—")),
        ("Budget Constraints", _display(inp.get("budget_constraints"), default="—")),
        ("Maintenance Expectations", _display(inp.get("maintenance_expectations"), default="—")),
        ("Deployment Preference", _display(inp.get("deployment_preference"), default="—")),
    ]


def _format_features(raw: Any, *, default: str = "—") -> str:
    if raw is None:
        return default
    if isinstance(raw, str):
        features = [p.strip() for p in raw.replace("|", ",").split(",") if p.strip()]
    elif isinstance(raw, list):
        features = [str(x).strip() for x in raw if str(x).strip()]
    else:
        return default
    return ", ".join(features) if features else default


def build_summary_row(label: str, value: str) -> ft.Control:
    """Label left, value right, thin divider (Laravel Project Summary rows)."""
    return ft.Container(
        padding=ft.padding.symmetric(vertical=10),
        border=ft.border.only(
            bottom=ft.BorderSide(1, ft.colors.with_opacity(0.35, _C_INNER_BD))
        ),
        content=ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=12,
            controls=[
                ft.Text(label, size=12, color=_C_MUTED, width=148),
                ft.Text(
                    value or "—",
                    size=12,
                    weight=ft.FontWeight.W_600,
                    color=_C_PRIMARY,
                    expand=True,
                    text_align=ft.TextAlign.RIGHT,
                    selectable=True,
                ),
            ],
        ),
    )


def build_stack_mini_card(
    label: str,
    value: str,
    *,
    highlight: bool = False,
) -> ft.Control:
    """Mini stat tile for Saved Recommendation stack row (navy/cyan glass)."""
    bg = _CARD_BG_ACCENT if highlight else _CARD_BG_SOFT
    border_color = ft.colors.with_opacity(0.5 if highlight else 0.36, _C_CYAN)
    label_color = _C_CYAN if highlight else _C_MUTED
    shadow = (
        [
            ft.BoxShadow(
                spread_radius=0,
                blur_radius=14,
                color=ft.colors.with_opacity(0.14, _C_CYAN),
                offset=ft.Offset(0, 4),
            ),
        ]
        if highlight
        else None
    )
    return ft.Container(
        bgcolor=bg,
        border=ft.border.all(1, border_color),
        border_radius=14,
        padding=ft.padding.symmetric(horizontal=12, vertical=14),
        shadow=shadow,
        content=ft.Column(
            spacing=6,
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    label.upper(),
                    size=10,
                    weight=ft.FontWeight.W_700,
                    color=label_color,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    value or "—",
                    size=20 if highlight else 16,
                    weight=ft.FontWeight.W_700,
                    color=_C_PRIMARY,
                    text_align=ft.TextAlign.CENTER,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
        ),
    )


def build_reason_card(title: str, text: str) -> ft.Control:
    """Navy/cyan glass reason panel (Saved Recommendation)."""
    body = (text or "").strip() or "No detailed reason available."
    return ft.Container(
        bgcolor=_CARD_BG_SOFT,
        border=ft.border.all(
            1, ft.colors.with_opacity(_SAVED_CARD_BORDER_CYAN, _C_CYAN)
        ),
        border_radius=14,
        padding=14,
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Text(title, size=13, weight=ft.FontWeight.W_600, color=_C_CYAN),
                ft.Text(body, size=12, color=_C_SECONDARY, selectable=True),
            ],
        ),
    )


def build_confidence_badge(score: int) -> ft.Control:
    """Card-level confidence pill (e.g. 77% Confidence)."""
    safe = max(0, min(100, int(score)))
    return ft.Container(
        content=ft.Text(
            f"{safe}% Confidence",
            size=11,
            weight=ft.FontWeight.W_600,
            color=_C_CYAN,
        ),
        bgcolor=ft.colors.with_opacity(0.12, _C_CYAN),
        border=ft.border.all(1, ft.colors.with_opacity(0.28, _C_CYAN)),
        border_radius=Radii.pill,
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
    )


def _gap_sort_key(gap_level: str) -> int:
    level = (gap_level or "").strip().lower()
    if "high" in level:
        return 0
    if "medium" in level or "med" in level:
        return 1
    if "low" in level:
        return 2
    return 3


def _priority_exists(
    priorities: list[tuple[str, str]],
    title: str,
    description: str,
) -> bool:
    title_key = title.strip().lower()
    desc_key = description.strip().lower()
    for existing_title, existing_desc in priorities:
        if existing_title.strip().lower() == title_key:
            return True
        if desc_key and existing_desc.strip().lower() == desc_key:
            return True
    return False


def _stack_blob(language: str, framework: str, sdlc: str) -> str:
    return f"{language} {framework} {sdlc}".lower()


def _stack_learning_fallbacks(
    language: str,
    framework: str,
    sdlc: str,
    ctx: Mapping[str, Any],
) -> list[tuple[str, str]]:
    blob = _stack_blob(language, framework, sdlc)
    lang = _ctx_label(language) or "the language"
    fw = _ctx_label(framework) or "the framework"
    sdlc_label = _ctx_label(sdlc) or "the SDLC model"

    catalog: list[tuple[str, str, list[tuple[str, str]]]] = [
        (
            "laravel",
            ("laravel", "php"),
            [
                ("PHP and Laravel MVC fundamentals", f"Review core {lang} patterns and Laravel MVC structure."),
                ("Routing, controllers, validation, and Eloquent", "Practice request flow, validation rules, and database models."),
                ("Authentication and role-based access", "Prepare login, roles, middleware, and protected routes."),
                ("MySQL database design", "Plan entities, relationships, migrations, and reporting queries."),
                ("Deployment basics", "Set up environment variables, testing, and release steps."),
            ],
        ),
        (
            "django",
            ("django",),
            [
                ("Python and Django fundamentals", f"Review {lang} syntax and Django project structure."),
                ("Models, views, and templates", "Practice ORM models, views, and template rendering."),
                ("Django admin and permissions", "Configure admin workflows and permission checks."),
                ("Database migrations", "Plan schema changes and migration workflow early."),
                ("Deployment basics", "Prepare settings, static files, and hosting steps."),
            ],
        ),
        (
            "fastapi",
            ("fastapi",),
            [
                ("Python API fundamentals", f"Review {lang} basics for API development."),
                ("Pydantic schemas", "Define request/response models and validation rules."),
                ("REST endpoint structure", f"Organize routes and services for {fw}."),
                ("Authentication and JWT", "Prepare token-based auth and protected endpoints."),
                ("API testing and deployment", "Add tests, environment config, and deployment workflow."),
            ],
        ),
        (
            "spring",
            ("spring boot", "spring"),
            [
                ("Java OOP and Spring Boot structure", f"Review {lang} OOP and layered Spring Boot design."),
                ("REST controllers and services", "Practice controller/service separation and DTO flow."),
                ("Spring Security basics", "Prepare authentication, authorization, and security config."),
                ("JPA/Hibernate database mapping", "Define entities, repositories, and relationships."),
                ("Testing and deployment", "Add unit/integration tests and deployment pipeline steps."),
            ],
        ),
        (
            "aspnet",
            ("asp.net", "aspnet", ".net"),
            [
                ("C# and ASP.NET Core fundamentals", f"Review {lang} and {fw} project structure."),
                ("Entity Framework Core", "Plan entities, DbContext, and migrations."),
                ("Authentication and authorization", "Prepare identity, roles, and protected endpoints."),
                ("SQL Server/database structure", "Design tables, relationships, and query patterns."),
                ("Cloud/IIS deployment basics", "Prepare hosting, configuration, and release workflow."),
            ],
        ),
        (
            "flutter",
            ("flutter",),
            [
                ("Dart fundamentals", f"Review {lang} syntax and core language patterns."),
                ("Widgets and state management", "Practice UI composition and state updates."),
                ("API integration", f"Connect {fw} UI to backend services safely."),
                ("Mobile UI navigation", "Plan routes, screens, and user flows."),
                ("Build and deployment", "Prepare build targets, signing, and release steps."),
            ],
        ),
        (
            "tauri",
            ("tauri",),
            [
                ("Rust or TypeScript basics", "Review the core language used in the desktop shell."),
                ("Tauri app structure", "Understand commands, frontend bridge, and packaging."),
                ("Local storage and security", "Plan secure local data handling and permissions."),
                ("Desktop packaging", "Prepare installers and platform-specific build steps."),
                ("Performance testing", "Validate startup time, memory use, and UI responsiveness."),
            ],
        ),
        (
            "nestjs",
            ("nestjs", "nest.js"),
            [
                ("TypeScript backend fundamentals", f"Review {lang} patterns for backend modules."),
                ("Modules, controllers, and services", f"Structure {fw} features with clear boundaries."),
                ("Authentication and guards", "Prepare guards, roles, and protected routes."),
                ("Database integration", "Plan ORM models, migrations, and repository usage."),
                ("Testing and deployment", "Add API tests, config, and deployment workflow."),
            ],
        ),
    ]

    for _key, markers, items in catalog:
        if any(marker in blob for marker in markers):
            return items

    ptype = _ctx_label(ctx.get("project_type"))
    if ptype:
        return [
            (
                f"Review {fw} project setup",
                f"Prepare a {ptype.lower()} project skeleton before feature work.",
            ),
            (
                "Plan core modules first",
                "Define authentication, data models, and API boundaries early.",
            ),
            (
                f"Practice {sdlc_label} planning",
                f"Use {sdlc_label} checkpoints for scope, risk, and review cycles.",
            ),
            (
                "Prepare deployment workflow",
                "Set up environments, testing, and release steps before launch.",
            ),
            (
                "Keep documentation updated",
                "Record setup steps, API notes, and module responsibilities.",
            ),
        ]
    return []


def _generic_learning_priorities(
    data: DecisionReportData,
    ctx: Mapping[str, Any],
) -> list[tuple[str, str]]:
    lang = _ctx_label(data.recommended_language) or "the recommended language"
    fw = _ctx_label(data.recommended_framework) or "the recommended framework"
    experience = _ctx_label(ctx.get("development_experience"))
    deployment = _ctx_label(ctx.get("deployment_preference"))

    items = [
        (
            "Review core stack basics",
            f"Focus on {lang} and {fw} fundamentals before building modules.",
        ),
        (
            "Practice authentication flow",
            "Prepare login, roles, validation, and protected routes early.",
        ),
        (
            "Plan database structure",
            "Define entities, relationships, migrations, and reporting queries.",
        ),
        (
            "Prepare deployment workflow",
            "Set up environment variables, testing, and deployment steps before release.",
        ),
        (
            "Keep documentation updated",
            "Record setup instructions, API notes, and module responsibilities.",
        ),
    ]
    if experience:
        items.insert(
            1,
            (
                "Align with team experience",
                f"Plan learning time around the team's {experience.lower()} experience level.",
            ),
        )
    if deployment:
        items[3] = (
            "Prepare deployment workflow",
            f"Set up {deployment.lower()} environments, testing, and release steps.",
        )
    return items


def _reason_text(paragraph: str, points: list[str]) -> str:
    if (paragraph or "").strip():
        return paragraph.strip()
    cleaned = [p.strip() for p in points if p.strip()]
    if cleaned:
        return " ".join(cleaned)
    return ""


_REASON_DETAIL_MIN_LEN = 85
_REASON_DETAIL_MIN_WORDS = 13


def _is_detailed_reason(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    if len(t) >= _REASON_DETAIL_MIN_LEN:
        return True
    return len(t.split()) >= _REASON_DETAIL_MIN_WORDS


def _report_result_view(data: DecisionReportData) -> dict[str, Any]:
    return {
        "recommended_language": data.recommended_language,
        "recommended_framework": data.recommended_framework,
        "recommended_sdlc": data.recommended_sdlc,
        "project_type": data.project_type,
        "complexity": data.complexity,
    }


def _build_reason_context(
    *,
    profile: dict[str, Any],
    rec: Optional[Recommendation] = None,
    result: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    p = profile or {}
    r = result or {}

    def pick(key: str, *fallback_keys: str) -> str:
        for k in (key, *fallback_keys):
            if k in p and p[k] not in (None, ""):
                return _display(p[k], default="")
            if k in r and r[k] not in (None, ""):
                return _display(r[k], default="")
        if rec is not None:
            attr_map = {
                "project_type": "project_type",
                "complexity": "complexity",
                "timeline": "timeline",
                "scalability_needs": "scalability",
                "security_requirements": "security",
                "development_experience": "experience",
                "deployment_preference": "platform",
            }
            attr = attr_map.get(key)
            if attr and getattr(rec, attr, None):
                return _display(getattr(rec, attr), default="")
        return ""

    return {
        "recommended_language": pick(
            "recommended_language",
        )
        or (rec.recommended_language if rec else r.get("recommended_language", "")),
        "recommended_framework": pick("recommended_framework")
        or (rec.recommended_framework if rec else r.get("recommended_framework", "")),
        "recommended_sdlc": pick("recommended_sdlc")
        or (rec.recommended_sdlc if rec else r.get("recommended_sdlc", "")),
        "project_type": pick("project_type") or (rec.project_type if rec else ""),
        "complexity": pick("complexity") or (rec.complexity if rec else ""),
        "timeline": pick("timeline") or (rec.timeline if rec else ""),
        "selected_features": p.get("selected_features") or r.get("selected_features"),
        "requirements_stability": pick("requirements_stability"),
        "stakeholder_involvement": pick("stakeholder_involvement"),
        "scalability_needs": pick("scalability_needs", "scalability"),
        "performance_requirements": pick("performance_requirements"),
        "security_requirements": pick("security_requirements", "security"),
        "development_experience": pick("development_experience", "experience"),
        "deployment_preference": pick("deployment_preference", "platform"),
    }


def _ctx_label(value: Any) -> str:
    text = _display(value, default="")
    return text if text and text != "—" else ""


def format_reason_text(
    kind: str,
    raw_reason: str,
    result: Mapping[str, Any],
    input_data: Mapping[str, Any],
) -> str:
    """Display-only expansion for short engine reason strings."""
    raw = (raw_reason or "").strip()
    if _is_detailed_reason(raw):
        return raw

    ctx: dict[str, Any] = {**dict(result or {}), **dict(input_data or {})}
    lang = _ctx_label(ctx.get("recommended_language"))
    fw = _ctx_label(ctx.get("recommended_framework"))
    sdlc = _ctx_label(ctx.get("recommended_sdlc"))
    ptype = _ctx_label(ctx.get("project_type"))
    complexity = _ctx_label(ctx.get("complexity"))
    timeline = _ctx_label(ctx.get("timeline"))
    features = _format_features(ctx.get("selected_features"), default="")
    stability = _ctx_label(ctx.get("requirements_stability"))
    stakeholder = _ctx_label(ctx.get("stakeholder_involvement"))
    scalability = _ctx_label(ctx.get("scalability_needs"))
    performance = _ctx_label(ctx.get("performance_requirements"))
    security = _ctx_label(ctx.get("security_requirements"))
    experience = _ctx_label(ctx.get("development_experience"))
    deployment = _ctx_label(ctx.get("deployment_preference"))

    short_note = ""
    if raw:
        short_note = (
            raw
            if raw.endswith(".")
            else f"This aligns with the recorded rationale: {raw}."
        )

    kind = (kind or "").strip().lower()

    if kind == "language":
        subject = lang or "The recommended language"
        parts: list[str] = [f"{subject} was recommended"]
        if ptype:
            parts.append(f"because this {ptype.lower()} project")
        if complexity:
            parts.append(f"has {complexity.lower()} complexity")
        tail: list[str] = []
        if timeline:
            tail.append(f"a {timeline.lower()} timeline")
        if scalability:
            tail.append(f"{scalability.lower()} scalability needs")
        if security:
            tail.append(f"{security.lower()} security requirements")
        if performance:
            tail.append(f"{performance.lower()} performance requirements")
        if deployment:
            tail.append(f"{deployment.lower()} deployment preference")
        if experience:
            tail.append(f"{experience.lower()} team experience")
        if tail:
            parts.append("with " + ", ".join(tail))
        text = " ".join(parts).strip() + "."
        if short_note and short_note not in text:
            return f"{text} {short_note}".strip()
        return text or short_note or "No detailed reason available."

    if kind == "framework":
        subject = fw or "The recommended framework"
        parts = [f"{subject} was selected"]
        if lang and ptype:
            parts.append(f"to support {lang} development for this {ptype.lower()} project")
        elif ptype:
            parts.append(f"for this {ptype.lower()} project")
        elif lang:
            parts.append(f"to complement {lang}")
        else:
            parts.append("for the recommended stack")
        tail = []
        if features:
            tail.append(f"selected features such as {features}")
        if deployment:
            tail.append(f"{deployment.lower()} deployment goals")
        if complexity:
            tail.append(f"{complexity.lower()} delivery complexity")
        if tail:
            parts.append("and fits " + ", ".join(tail))
        text = " ".join(parts).strip() + "."
        if short_note and short_note not in text:
            return f"{text} {short_note}".strip()
        return text or short_note or "No detailed reason available."

    if kind == "sdlc":
        subject = sdlc or "The recommended SDLC model"
        parts = [f"{subject} was selected"]
        if complexity or security:
            bits = []
            if complexity:
                bits.append(f"{complexity.lower()} complexity")
            if security:
                bits.append(f"{security.lower()} security requirements")
            parts.append(f"because the project has {' and '.join(bits)}")
        elif ptype:
            parts.append(f"because this {ptype.lower()} project needs structured delivery")
        else:
            parts.append("based on the project profile")
        tail = []
        if stability:
            tail.append(f"{stability.lower()} requirements stability")
        if stakeholder:
            tail.append(f"{stakeholder.lower()} stakeholder involvement")
        if timeline:
            tail.append(f"a {timeline.lower()} timeline")
        if tail:
            parts.append(", which makes " + ", ".join(tail) + " important during planning")
        text = " ".join(parts).strip() + "."
        if short_note and short_note not in text:
            return f"{text} {short_note}".strip()
        return text or short_note or "No detailed reason available."

    if raw:
        return raw
    return "No detailed reason available."
