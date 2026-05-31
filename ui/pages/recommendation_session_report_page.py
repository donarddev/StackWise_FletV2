"""Full decision report UI for session-stored recommendation engine output."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Mapping, Optional

import flet as ft

from app.helpers.recommendation_engine_compat import normalize_engine_result_for_ui
from ui.components.empty_state import empty_state
from ui.components.primary_button import primary_button
from ui.components.recommendation_decision_report import (
    build_decision_report_body,
    report_data_from_session,
)
from ui.pages.recommendation_page import recommendation_workspace_theme
from ui.themes.app_theme import Radii

_PAGE_PAD = 40


def build_session_summary_clipboard_text(
    result: dict[str, Any],
    input_data: dict[str, Any],
) -> str:
    """Plain-text summary for Copy Summary from session report."""
    from app.utils.constants import confidence_label

    result = normalize_engine_result_for_ui(result)
    try:
        score = int(round(float(result.get("confidence_score", 0))))
    except (TypeError, ValueError):
        score = 0
    score = max(0, min(100, score))
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
    for item in result.get("risk_analysis") or result.get("risks") or []:
        if isinstance(item, dict):
            risk = item.get("risk", "")
            reason = item.get("reason", "")
            if risk:
                lines.append(f"Risk: {risk}: {reason}")
        elif str(item).strip():
            lines.append(f"Risk: {item}")
    for item in result.get("skill_gap_analysis") or result.get("skill_gaps") or []:
        if isinstance(item, dict):
            skill = item.get("skill", "")
            if skill:
                lines.append(f"Skill gap: {skill}")
        elif str(item).strip():
            lines.append(f"Skill gap: {item}")
    for phase in result.get("suggested_project_roadmap") or result.get("roadmap") or []:
        if isinstance(phase, dict):
            title = phase.get("title", "")
            desc = phase.get("description", "")
            if title or desc:
                lines.append(f"{title}: {desc}")
    return "\n".join(lines).strip()


def build_session_recommendation_report(
    *,
    result: Optional[dict[str, Any]],
    input_data: Optional[dict[str, Any]],
    theme: Mapping[str, Any],
    generated_label: str,
    record_id: Optional[int] = None,
    on_back_recommendation: Callable[[ft.ControlEvent], None],
    on_back_history: Callable[[ft.ControlEvent], None],
    on_copy_summary: Optional[Callable[[ft.ControlEvent], None]],
    on_regenerate: Optional[Callable[[ft.ControlEvent], None]],
    on_dashboard: Optional[Callable[[ft.ControlEvent], None]],
) -> ft.Control:
    """Professional decision report from page.session engine output."""
    rw = recommendation_workspace_theme(theme)
    inp = input_data or {}
    result = normalize_engine_result_for_ui(result)

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

    data = report_data_from_session(result, inp, generated_label=generated_label)
    if record_id is not None:
        data.record_id = record_id

    return build_decision_report_body(
        data,
        theme=rw,
        route_params={"id": record_id} if record_id is not None else None,
        on_back_recommendation=on_back_recommendation,
        on_back_history=on_back_history,
        on_copy_summary=on_copy_summary,
        on_regenerate=on_regenerate,
        on_dashboard=on_dashboard,
        show_feedback=False,
    )


def format_generated_label() -> str:
    """Human-readable generated timestamp for session reports."""
    return datetime.now().strftime("%b %d, %Y")
