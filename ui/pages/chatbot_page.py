# ACTIVE CHATBOT PAGE
"""Chatbot page — full-height chat panel."""

from __future__ import annotations

from typing import Any, Callable, Mapping

import flet as ft

from app.models.chatbot_log import ChatbotLog
from ui.components.brand_logo import brand_icon
from ui.components.dashboard.glass_tokens import dashboard_glass_tokens
from ui.components.input_field import input_field
from ui.components.primary_button import secondary_button
from ui.themes.app_theme import Radii, Spacing
from ui.theme import caption_style, display_style, subheading_style, text_style
from ui.widgets.chat_bubble import chat_bubble

# Right panel — suggested questions send immediately; quick topics fill the input.
SUGGESTED_QUESTIONS = [
    "Suggest a stack for a student capstone web app with auth + CRUD.",
    "What SDLC model fits a short timeline with changing requirements?",
    "Given these constraints, what language/framework should I pick?",
    "What are the trade-offs between Laravel and FastAPI for an API project?",
    "How should I plan my project roadmap for the next 8 weeks?",
]

QUICK_TOPICS = [
    "Compare FastAPI vs Django",
    "MVP architecture for SaaS",
    "Testing strategy for backend APIs",
    "Cost-effective cloud options",
]

HELP_ITEMS = [
    "Explain programming languages",
    "Compare frameworks",
    "Explain SDLC models",
    "Clarify recommendation results",
    "Suggest beginner-friendly project direction",
]

# Chat transcript region height when embedded in app_layout's scroll Column.
# expand=True inside a scroll parent yields unbounded height → fixed body height.
# Composer floats over the bottom of this region; transcript has bottom padding so
# the last message stays clear of the input shell.
_CHAT_BODY_HEIGHT = 628
# Wide lane when Assistant Tips is closed (matches prior layout).
_CHAT_LANE_MAX_W = 920
# Narrower lane when the right drawer is open so bubbles never paint under the panel.
_CHAT_LANE_WITH_PANEL_W = 760
_ASSISTANT_PANEL_W = 328
_PANEL_GAP = 24
# Input shell max width (floating composer), aligned with chat lane when tips open.
_INPUT_SHELL_WIDE_W = 840
_INPUT_SHELL_WITH_PANEL_W = 720
_MSG_SPACING = 20
_MSG_LIST_TOP_PAD = 16
# Space above floating composer so the last bubble stays readable when scrolled to end.
_CHAT_SCROLL_BOTTOM_PAD = 108

# Empty-state chips (send immediately).
EMPTY_STATE_PROMPTS = [
    "What language should I use for an AI side-project?",
    "Explain Agile, Kanban, and Waterfall.",
    "When should I pick FastAPI over Django?",
    "Help me choose between Flutter and React Native.",
    "How can I reduce time-to-market for a SaaS MVP?",
]


def _chatbot_page_header(
    *,
    theme: Mapping[str, Any],
    glass: dict[str, str],
    subtitle: str,
    trailing: ft.Control,
) -> ft.Row:
    """Chatbot-only header — teal/cyan eyebrow to match dashboard glass (no global page_header change)."""
    teal = glass["teal"]
    pill = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.icons.AUTO_AWESOME, size=12, color=teal),
                ft.Text(
                    "AI CHATBOT",
                    style=ft.TextStyle(
                        size=11,
                        weight=ft.FontWeight.W_700,
                        color=teal,
                    ),
                ),
            ],
            spacing=6,
            tight=True,
        ),
        bgcolor=ft.colors.with_opacity(0.12, teal),
        border=ft.border.all(1, ft.colors.with_opacity(0.32, teal)),
        border_radius=Radii.pill,
        padding=ft.padding.symmetric(horizontal=10, vertical=5),
    )
    return ft.Row(
        controls=[
            ft.Column(
                controls=[
                    pill,
                    ft.Container(height=Spacing.sm),
                    ft.Text("Talk to StackWise.", style=display_style(theme, size=30)),
                    ft.Text(subtitle, style=text_style(theme, size=14)),
                ],
                spacing=4,
                tight=True,
            ),
            ft.Container(expand=1),
            trailing,
        ],
        vertical_alignment=ft.CrossAxisAlignment.START,
    )


def build_chatbot_page(
    *,
    theme: Mapping[str, Any],
    user_name: str,
    history: list[ChatbotLog],
    is_ollama_available: bool,
    input_field_ref: ft.Ref[ft.TextField],
    messages_column_ref: ft.Ref[ft.Column],
    on_send: Callable[[str], None],
    on_clear: Callable[[ft.ControlEvent], None],
    page: ft.Page | None = None,
    user_avatar_url: str | None = None,
    user_header_title: str | None = None,
) -> ft.Control:
    panel_host_ref: ft.Ref[ft.Container] = ft.Ref()
    chat_lane_ref: ft.Ref[ft.Container] = ft.Ref()
    input_shell_ref: ft.Ref[ft.Container] = ft.Ref()
    chat_split_ref: ft.Ref[ft.Container] = ft.Ref()
    assistant_tips_open: dict[str, bool] = {"v": False}

    def _toggle_assistant(_e: ft.ControlEvent | None = None):
        assistant_tips_open["v"] = not assistant_tips_open["v"]
        open_ = assistant_tips_open["v"]
        host = panel_host_ref.current
        lane = chat_lane_ref.current
        shell = input_shell_ref.current
        if host is not None:
            host.width = _ASSISTANT_PANEL_W if open_ else 0
            host.visible = open_
            host.margin = ft.margin.only(left=_PANEL_GAP if open_ else 0)
        if lane is not None:
            lane.width = _CHAT_LANE_WITH_PANEL_W if open_ else _CHAT_LANE_MAX_W
        if shell is not None:
            shell.width = _INPUT_SHELL_WITH_PANEL_W if open_ else _INPUT_SHELL_WIDE_W
        root = chat_split_ref.current
        if root is not None and root.page:
            root.update()

    glass = dashboard_glass_tokens(theme)
    tips_fg = glass["teal"] if str(theme.get("page_bg", "")).lower() == "#020617" else theme["accent_2"]
    header_actions = ft.Row(
        spacing=Spacing.sm,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.TextButton(
                "Assistant tips",
                on_click=_toggle_assistant,
                style=ft.ButtonStyle(
                    color=tips_fg,
                    bgcolor=ft.colors.with_opacity(0.06, tips_fg),
                    overlay_color=ft.colors.with_opacity(0.08, tips_fg),
                ),
            ),
            secondary_button(
                "Clear conversation",
                on_click=on_clear,
                icon=ft.icons.CLEAR_ALL,
                theme=theme,
                bgcolor=ft.colors.with_opacity(0.45, glass["card_bg"]),
                border_color=glass["card_border"],
                hover_border_color=glass["teal"],
            ),
        ],
    )

    def _submit_chat_input(raw: str) -> None:
        message = (raw or "").strip()
        if not message:
            return
        field = input_field_ref.current
        if field is not None:
            field.value = ""
            if page is not None:
                page.update()
        on_send(message)

    chat_input = input_field(
        "",
        hint="Ask anything — languages, frameworks, SDLC, your last recommendation...",
        icon=ft.icons.CHAT_BUBBLE_OUTLINE,
        on_submit=lambda e: _submit_chat_input(e.control.value or ""),
        theme=theme,
        ref=input_field_ref,
    )
    # Composer field: calm border; cyan focus (matches dashboard glass).
    chat_input.bgcolor = glass["header_bg"]
    chat_input.border_color = glass["card_border"]
    chat_input.focused_border_color = glass["teal"]
    chat_input.focused_bgcolor = ft.colors.with_opacity(0.95, glass["card_bg"])

    send_teal = glass["teal"]
    send_on = "#06111F"
    send_btn = ft.Container(
        content=ft.Row(
            tight=True,
            spacing=Spacing.sm,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.icons.SEND_ROUNDED, color=send_on, size=18),
                ft.Text("Send", size=13, weight=ft.FontWeight.W_600, color=send_on),
            ],
        ),
        bgcolor=send_teal,
        border_radius=Radii.pill,
        padding=ft.padding.symmetric(horizontal=18, vertical=10),
        height=44,
        alignment=ft.alignment.center,
        ink=True,
        on_click=lambda _e: _submit_chat_input(chat_input.value or ""),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=10,
            color=ft.colors.with_opacity(0.22, send_teal),
            offset=ft.Offset(0, 2),
        ),
    )

    composer_row = ft.Row(
        spacing=Spacing.sm,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(content=chat_input, expand=True),
            send_btn,
        ],
    )

    composer_border = glass["card_border"]
    composer_shadow = ft.BoxShadow(
        spread_radius=0,
        blur_radius=14,
        color=ft.colors.with_opacity(0.35, theme["card_shadow_color"]),
        offset=ft.Offset(0, 4),
    )

    initial_controls: list[ft.Control] = []
    if not history:
        initial_controls.append(
            _empty_chat_welcome(theme, user_name, on_send),
        )
    else:
        for log in history:
            initial_controls.append(
                chat_bubble(
                    role=log.role,
                    content=log.content,
                    author_name=user_name,
                    theme=theme,
                    page=page,
                    user_avatar_url=user_avatar_url if log.role == "user" else None,
                    user_header_title=user_header_title,
                )
            )

    messages = ft.Column(
        controls=initial_controls,
        spacing=_MSG_SPACING,
        scroll=ft.ScrollMode.ADAPTIVE,
        auto_scroll=True,
        ref=messages_column_ref,
        expand=True,
    )

    # Centered chat lane: fixed width; narrowed when Assistant Tips drawer is open
    # so user/AI bubbles never extend under the right column.
    chat_lane = ft.Container(
        ref=chat_lane_ref,
        width=_CHAT_LANE_MAX_W,
        padding=ft.padding.only(
            top=_MSG_LIST_TOP_PAD,
            bottom=_CHAT_SCROLL_BOTTOM_PAD,
        ),
        content=messages,
    )

    transcript = ft.Container(
        expand=True,
        padding=ft.padding.symmetric(horizontal=Spacing.sm),
        content=ft.Row(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[chat_lane],
        ),
    )

    input_shell = ft.Container(
        ref=input_shell_ref,
        width=_INPUT_SHELL_WIDE_W,
        padding=ft.padding.symmetric(horizontal=Spacing.md, vertical=Spacing.sm),
        border_radius=Radii.lg,
        bgcolor=ft.colors.with_opacity(0.94, glass["card_bg"]),
        border=ft.border.all(1, composer_border),
        shadow=[composer_shadow],
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=composer_row,
    )

    input_bar = ft.Container(
        padding=ft.padding.symmetric(horizontal=Spacing.sm, vertical=0),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[input_shell],
        ),
    )

    # Transcript fills the stack; composer floats at the bottom center (Copilot-style).
    main_chat_stack = ft.Stack(
        expand=True,
        controls=[
            ft.Container(expand=True, content=transcript),
            ft.Container(
                left=0,
                right=0,
                bottom=12,
                content=input_bar,
            ),
        ],
    )

    assistant_panel = _build_assistant_side_panel(
        theme=theme,
        is_ollama_available=is_ollama_available,
        on_send=on_send,
        input_ref=input_field_ref,
        on_hide_panel=_toggle_assistant,
    )

    # Right column: real drawer width when open, zero width when closed (no overlay on messages).
    panel_host = ft.Container(
        ref=panel_host_ref,
        width=0,
        visible=False,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        padding=ft.padding.only(right=Spacing.sm, bottom=Spacing.xs),
        content=assistant_panel,
    )

    chat_split = ft.Container(
        ref=chat_split_ref,
        expand=True,
        height=_CHAT_BODY_HEIGHT,
        content=ft.Row(
            expand=True,
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                ft.Container(expand=True, content=main_chat_stack),
                panel_host,
            ],
        ),
    )

    return ft.Column(
        spacing=Spacing.md,
        expand=False,
        controls=[
            _chatbot_page_header(
                theme=theme,
                glass=glass,
                subtitle=(
                    "Ollama-powered. Falls back gracefully when offline."
                    if is_ollama_available
                    else "Currently in offline fallback mode (Ollama not detected)."
                ),
                trailing=header_actions,
            ),
            chat_split,
        ],
    )


def _chip_base_style(theme: Mapping[str, Any]) -> dict[str, Any]:
    g = dashboard_glass_tokens(theme)
    return {
        "bgcolor": ft.colors.with_opacity(0.5, g["card_bg"]),
        "border": ft.border.all(1, ft.colors.with_opacity(0.9, g["card_border"])),
        "radius": Radii.pill,
        "pad_h": 8,
        "pad_v": 4,
    }


def _prompt_chip(
    theme: Mapping[str, Any],
    text: str,
    *,
    on_click: Callable[[ft.ControlEvent], None],
) -> ft.Control:
    st = _chip_base_style(theme)
    return ft.Container(
        ink=True,
        on_click=on_click,
        border_radius=st["radius"],
        bgcolor=st["bgcolor"],
        border=st["border"],
        padding=ft.padding.symmetric(horizontal=st["pad_h"], vertical=st["pad_v"]),
        content=ft.Text(
            text,
            size=10,
            color=theme["text_secondary"],
        ),
    )


def _empty_chat_welcome(
    theme: Mapping[str, Any],
    user_name: str,
    on_send: Callable[[str], None],
) -> ft.Control:
    first = user_name.split()[0] if user_name.strip() else "there"
    chips = [
        _prompt_chip(
            theme,
            p,
            on_click=lambda _e, prompt=p: on_send(prompt),
        )
        for p in EMPTY_STATE_PROMPTS
    ]
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=Spacing.md, vertical=Spacing.lg),
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=Spacing.sm,
            tight=True,
            controls=[
                brand_icon(size=48, radius=12),
                ft.Text(
                    f"Hi {first} — I'm StackWise.",
                    style=subheading_style(theme, size=20),
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    "Ask me about programming languages, frameworks, SDLC models, "
                    "or your recommendation results.",
                    style=text_style(theme, size=14),
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Container(height=Spacing.sm),
                ft.Text("Try asking:", style=caption_style(theme)),
                ft.Column(
                    spacing=6,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=chips,
                ),
            ],
        ),
    )


def _build_assistant_side_panel(
    *,
    theme: Mapping[str, Any],
    is_ollama_available: bool,
    on_send: Callable[[str], None],
    input_ref: ft.Ref[ft.TextField],
    on_hide_panel: Callable[[ft.ControlEvent | None], None],
) -> ft.Control:
    g = dashboard_glass_tokens(theme)
    status = "Ollama: on-device replies" if is_ollama_available else "Offline tips mode"

    suggested = [
        _prompt_chip(
            theme,
            q,
            on_click=lambda _e, prompt=q: on_send(prompt),
        )
        for q in SUGGESTED_QUESTIONS
    ]

    topics = [
        _prompt_chip(
            theme,
            t,
            on_click=lambda _e, topic=t: _populate_input(input_ref, topic),
        )
        for t in QUICK_TOPICS
    ]

    help_rows = [
        ft.Row(
            spacing=6,
            tight=True,
            controls=[
                ft.Icon(ft.icons.CHECK_CIRCLE_OUTLINE, color=g["teal"], size=14),
                ft.Text(item, size=11, color=theme["text_secondary"]),
            ],
        )
        for item in HELP_ITEMS
    ]

    panel_header = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Column(
                spacing=2,
                tight=True,
                expand=True,
                controls=[
                    ft.Text(
                        "Assistant",
                        size=14,
                        weight=ft.FontWeight.W_700,
                        color=theme["text"],
                    ),
                    ft.Text(status, size=10, color=theme["text_secondary"]),
                ],
            ),
            ft.IconButton(
                icon=ft.icons.CLOSE_ROUNDED,
                icon_size=16,
                tooltip="Hide panel",
                icon_color=theme["text_muted"],
                on_click=on_hide_panel,
            ),
        ],
    )

    inner = ft.Column(
        spacing=6,
        scroll=ft.ScrollMode.ADAPTIVE,
        expand=True,
        controls=[
            panel_header,
            ft.Divider(height=1, color=g["divider"]),
            ft.Text("Suggested questions", style=caption_style(theme)),
            ft.Column(spacing=3, tight=True, controls=suggested),
            ft.Text("Quick topics", style=caption_style(theme)),
            ft.Column(spacing=3, tight=True, controls=topics),
            ft.Text("What this assistant can help with", style=caption_style(theme)),
            ft.Column(spacing=2, tight=True, controls=help_rows),
        ],
    )

    return ft.Container(
        expand=True,
        bgcolor=g["card_bg"],
        border=ft.border.all(1, g["card_border"]),
        border_radius=Radii.md,
        padding=ft.padding.symmetric(horizontal=12, vertical=10),
        shadow=[
            ft.BoxShadow(
                spread_radius=0,
                blur_radius=12,
                color=ft.colors.with_opacity(0.28, theme["card_shadow_color"]),
                offset=ft.Offset(0, 3),
            ),
            ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.colors.with_opacity(0.1, g["teal"]),
                offset=ft.Offset(0, 0),
            ),
        ],
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=inner,
    )


def _populate_input(ref: ft.Ref[ft.TextField], text: str) -> None:
    if not ref or not ref.current:
        return
    ref.current.value = text
    if ref.current.page:
        ref.current.update()
