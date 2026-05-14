"""RecommendationDetailDialog — full breakdown of a single recommendation.

Optional footer actions (regenerate, delete, copy) are only shown when the
caller passes the corresponding callbacks (e.g. History). Dashboard and
recommendation pages keep the default Close-only dialog.
"""

from __future__ import annotations

from typing import Callable, Optional

import flet as ft

from app.helpers.date_helper import humanize
from app.models.recommendation import Recommendation
from app.utils.constants import confidence_label
from ui.components.background_layers import subtle_grid_layer
from ui.components.confidence_bar import confidence_bar
from ui.components.glass_card import glass_card
from ui.themes.app_theme import Colors, Gradients, Radii, Spacing, Typography


def build_summary_clipboard_text(rec: Recommendation) -> str:
    """Plain-text export for Copy summary (clipboard-safe, no HTML)."""
    expl = rec.explanation or {}
    lines = [
        f"Project: {rec.project_name}",
        f"Project type: {rec.project_type}",
        f"Recommended language: {rec.recommended_language}",
        f"Recommended framework: {rec.recommended_framework}",
        f"Recommended SDLC: {rec.recommended_sdlc}",
        f"Confidence: {rec.confidence_score}% ({confidence_label(rec.confidence_score)})",
        f"Created: {rec.created_at.strftime('%Y-%m-%d %H:%M UTC') if rec.created_at else ''}",
        "",
    ]
    summary = expl.get("summary") or ""
    if summary:
        lines.extend(["Explanation (summary)", summary, ""])
    for key in ("why_language", "why_framework", "why_sdlc"):
        sec = expl.get(key) or {}
        title = sec.get("title")
        points = sec.get("points") or []
        if title and points:
            lines.append(title)
            lines.extend(f"  • {p}" for p in points)
            lines.append("")
    for key, label in (
        ("risk_analysis", "Risk analysis"),
        ("skill_gap_analysis", "Skill gaps"),
        ("roadmap", "Roadmap"),
    ):
        vals = expl.get(key) or []
        if vals:
            lines.append(label)
            lines.extend(f"  • {v}" for v in vals)
            lines.append("")
    return "\n".join(lines).strip()


def build_recommendation_detail_dialog(
    rec: Recommendation,
    *,
    on_close: Callable[[ft.ControlEvent], None],
    on_regenerate: Optional[Callable[[ft.ControlEvent], None]] = None,
    on_delete: Optional[Callable[[ft.ControlEvent], None]] = None,
    on_copy_summary: Optional[Callable[[ft.ControlEvent], None]] = None,
    show_regenerate_hint: bool = False,
) -> ft.AlertDialog:
    action_row = _build_action_row(
        on_close=on_close,
        on_regenerate=on_regenerate,
        on_delete=on_delete,
        on_copy_summary=on_copy_summary,
    )

    body = ft.Container(
        width=760,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        border_radius=Radii.xl,
        gradient=Gradients.card_subtle(),
        border=ft.border.all(1, ft.colors.with_opacity(0.55, Colors.accent_cyan)),
        shadow=ft.BoxShadow(
            blur_radius=32,
            spread_radius=0,
            color="#8b5cf644",
            offset=ft.Offset(0, 14),
        ),
        content=ft.Stack(
            controls=[
                ft.Container(expand=True, content=subtle_grid_layer(opacity=0.07)),
                ft.Container(
                    padding=ft.padding.all(Spacing.xl),
                    content=ft.Column(
                        spacing=Spacing.lg,
                        controls=[
                            _dialog_title_row(rec),
                            *(
                                [_regenerate_hint_banner()]
                                if show_regenerate_hint
                                else []
                            ),
                            _facts_panel(rec),
                            ft.Divider(color=ft.colors.with_opacity(0.45, Colors.border_strong), height=1),
                            confidence_bar(rec.confidence_score),
                            _explanation_section(rec),
                            _alternatives_block(rec),
                            _trade_off_block(rec),
                            _list_block(rec, "risk_analysis", "Risk analysis"),
                            _list_block(rec, "skill_gap_analysis", "Skill gaps"),
                            _list_block(rec, "roadmap", "Roadmap"),
                            _project_profile_block(rec),
                        ],
                        scroll=ft.ScrollMode.AUTO,
                        height=520,
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
        content=body,
        actions=[action_row],
        actions_alignment=ft.MainAxisAlignment.END,
        actions_padding=ft.padding.symmetric(horizontal=Spacing.xl, vertical=Spacing.md),
        shape=ft.RoundedRectangleBorder(radius=Radii.xl + 4),
    )


def _build_action_row(
    *,
    on_close: Callable[[ft.ControlEvent], None],
    on_regenerate: Optional[Callable[[ft.ControlEvent], None]],
    on_delete: Optional[Callable[[ft.ControlEvent], None]],
    on_copy_summary: Optional[Callable[[ft.ControlEvent], None]],
) -> ft.Control:
    buttons: list[ft.Control] = [
        ft.TextButton("Close", on_click=on_close, tooltip="Close"),
    ]
    if on_copy_summary is not None:
        buttons.append(
            ft.TextButton(
                "Copy summary",
                icon=ft.icons.CONTENT_COPY_OUTLINED,
                on_click=on_copy_summary,
                tooltip="Copy a text summary to the clipboard",
            )
        )
    if on_regenerate is not None:
        buttons.append(
            ft.TextButton(
                "Regenerate",
                icon=ft.icons.REFRESH_ROUNDED,
                on_click=on_regenerate,
                tooltip="Re-run recommendation from the saved project profile",
            )
        )
    if on_delete is not None:
        buttons.append(
            ft.TextButton(
                "Delete",
                icon=ft.icons.DELETE_OUTLINE,
                icon_color=Colors.danger,
                style=ft.ButtonStyle(color=Colors.danger),
                on_click=on_delete,
                tooltip="Remove this recommendation",
            )
        )
    return ft.Row(
        controls=buttons,
        spacing=Spacing.sm,
        alignment=ft.MainAxisAlignment.END,
        wrap=True,
    )


def _dialog_title_row(rec: Recommendation) -> ft.Control:
    return ft.Column(
        spacing=Spacing.sm,
        tight=True,
        controls=[
            ft.Text("Recommendation details", style=Typography.caption()),
            ft.Text(rec.project_name, style=Typography.heading(size=22)),
            ft.Text(
                f"{rec.project_type} · {rec.complexity}",
                style=Typography.body(size=13),
            ),
        ],
    )


def _regenerate_hint_banner() -> ft.Control:
    return ft.Container(
        padding=ft.padding.all(Spacing.md),
        border_radius=Radii.md,
        bgcolor=ft.colors.with_opacity(0.12, Colors.primary),
        border=ft.border.all(1, ft.colors.with_opacity(0.4, Colors.primary)),
        content=ft.Row(
            spacing=Spacing.md,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Icon(ft.icons.INFO_OUTLINE, size=20, color=Colors.primary_soft),
                ft.Text(
                    "Regenerate will re-run the recommendation using the saved project profile. "
                    "Older records may use form fields only where the profile was not stored.",
                    style=Typography.body(size=13),
                    expand=True,
                ),
            ],
        ),
    )


def _facts_panel(rec: Recommendation) -> ft.Control:
    created_full = (
        rec.created_at.strftime("%b %d, %Y · %H:%M UTC")
        if rec.created_at
        else "—"
    )
    created_rel = humanize(rec.created_at) if rec.created_at else "—"
    rows: list[tuple[str, str]] = [
        ("Project name", rec.project_name),
        ("Project type", rec.project_type),
        ("Recommended language", rec.recommended_language),
        ("Recommended framework", rec.recommended_framework),
        ("Recommended SDLC model", rec.recommended_sdlc),
        ("Confidence score", f"{rec.confidence_score}% · {confidence_label(rec.confidence_score)}"),
        ("Created", f"{created_full} ({created_rel})"),
    ]
    inner = ft.Column(
        spacing=Spacing.sm,
        controls=[_fact_row(k, v) for k, v in rows],
    )
    return glass_card(
        inner,
        padding=Spacing.lg,
        bgcolor=ft.colors.with_opacity(0.5, Colors.surface_2),
        border_color=ft.colors.with_opacity(0.5, Colors.border_strong),
        glow=False,
    )


def _fact_row(label: str, value: str) -> ft.Control:
    return ft.Row(
        spacing=Spacing.md,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[
            ft.Container(
                width=200,
                content=ft.Text(label, size=12.5, color=Colors.text_muted, weight=ft.FontWeight.W_500),
            ),
            ft.Text(value, size=13.5, weight=ft.FontWeight.W_600, color=Colors.text_primary, expand=True),
        ],
    )


def _explanation_section(rec: Recommendation) -> ft.Control:
    expl = rec.explanation or {}
    has_summary = bool(str(expl.get("summary", "")).strip())
    why_col = _why_blocks(rec)
    has_why = bool(why_col.controls)
    if not has_summary and not has_why:
        return ft.Container(visible=False)
    parts: list[ft.Control] = []
    if has_summary:
        parts.append(ft.Text(str(expl.get("summary")), style=Typography.body(size=13.5)))
    if has_why:
        parts.append(why_col)
    return _block(title="Explanation", body=ft.Column(spacing=Spacing.md, controls=parts))


def _why_blocks(rec: Recommendation) -> ft.Control:
    expl = rec.explanation or {}
    items: list[ft.Control] = []
    for key in ("why_language", "why_framework", "why_sdlc"):
        section = expl.get(key) or {}
        title = section.get("title")
        points = section.get("points") or []
        if not title or not points:
            continue
        items.append(
            ft.Column(
                spacing=Spacing.xs,
                tight=True,
                controls=[
                    ft.Text(title, style=Typography.subheading(size=14)),
                    ft.Column(spacing=6, controls=[_bullet(p) for p in points]),
                ],
            )
        )
    return ft.Column(controls=items, spacing=Spacing.md)


def _alternatives_block(rec: Recommendation) -> ft.Control:
    expl = rec.explanation or {}
    alts = rec.alternatives or {}
    if not alts and not any(expl.get(k) for k in ("why_not_languages", "why_not_frameworks", "why_not_sdlc")):
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
                            ft.Text(
                                runner.get("name", ""),
                                size=13.5,
                                weight=ft.FontWeight.W_700,
                                color=Colors.text_primary,
                            ),
                            ft.Text(runner.get("reason", ""), style=Typography.body(size=12.5)),
                        ],
                    ),
                )
            )
        if not rows:
            return ft.Container(visible=False)
        return _block(title=f"Alternatives — why not the other {label}", body=ft.Column(spacing=Spacing.sm, controls=rows))

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


def _list_block(rec: Recommendation, key: str, title: str) -> ft.Control:
    values = (rec.explanation or {}).get(key) or []
    if not values:
        return ft.Container(visible=False)
    return _block(title=title, body=ft.Column(spacing=6, controls=[_bullet(v) for v in values]))


def _project_profile_block(rec: Recommendation) -> ft.Control:
    profile = rec.project_profile or {}
    features = ", ".join(profile.get("selected_features", [])[:6]) or "-"
    items = [
        ("Project type", rec.project_type),
        ("Goal", profile.get("project_goal", rec.project_goal)),
        ("Complexity", rec.complexity),
        ("Team", rec.team_size),
        ("Timeline", rec.timeline),
        ("Requirements", profile.get("requirements_stability", "-")),
        ("Stakeholders", profile.get("stakeholder_involvement", "-")),
        ("Scalability", rec.scalability),
        ("Performance", profile.get("performance_requirements", "-")),
        ("Security", rec.security),
        ("Budget", profile.get("budget_constraints", "-")),
        ("Platform", rec.platform),
        ("Experience", rec.experience),
        ("Features", features),
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
    return _block(title="Project profile (saved inputs)", body=ft.Column(spacing=6, controls=rows))


def _block(*, title: str, body: ft.Control) -> ft.Control:
    return ft.Container(
        padding=Spacing.lg,
        bgcolor=ft.colors.with_opacity(0.55, Colors.surface_2),
        border=ft.border.all(1, ft.colors.with_opacity(0.55, Colors.border_strong)),
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
                width=6,
                height=6,
                border_radius=999,
                bgcolor=Colors.accent_cyan,
                margin=ft.margin.only(top=8),
            ),
            ft.Text(text, style=Typography.body(size=13), expand=True),
        ],
        spacing=Spacing.sm,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )
