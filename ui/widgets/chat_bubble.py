"""ChatBubble — message bubble for the chatbot UI.

Layout: user messages are right-aligned with an identity header (name + avatar)
above the bubble; assistant messages are left-aligned with ``StackWise AI`` +
brand icon. Bubble widths are capped for readability; avatars match 32px chrome.
"""

from __future__ import annotations

from typing import Any, Mapping

import flet as ft

from ui.components.brand_logo import brand_icon
from ui.components.chat_message_parts import (
    build_user_identity_header_row,
    default_user_header_title,
)
from ui.components.dashboard.glass_tokens import dashboard_glass_tokens
from ui.components.toast import show_toast
from ui.themes.app_theme import Colors, Radii, Spacing
from ui.theme import text_style


# Max bubble widths inside chat lane (~760–920px): width-from-content heuristic below.
_USER_BUBBLE_MAX_PX = 500.0
_AI_BUBBLE_MAX_PX = 558.0
_CHAR_EST_PX = 5.85
_HPAD_EST = 32.0

_ACTION_ICON_SIZE = 17


def _muted(theme: Mapping[str, Any] | None) -> str:
    return theme["text_muted"] if theme is not None else Colors.text_muted


def _accent(theme: Mapping[str, Any] | None) -> str:
    return theme["accent"] if theme is not None else Colors.primary


def _copy_to_clipboard(ev: ft.ControlEvent, text: str, success_msg: str) -> None:
    page = ev.page
    if page is None:
        return
    if not hasattr(page, "set_clipboard"):
        show_toast(page, "Copy unavailable in this environment.", kind="warning")
        return
    try:
        page.set_clipboard(text)
        show_toast(page, success_msg, kind="success")
    except Exception:
        show_toast(page, "Copy unavailable.", kind="error")


def _bubble_content_width(content: str, max_px: float, *, min_px: float = 72.0) -> float:
    """Heuristic width so short messages stay narrow; long lines cap at max_px."""
    s = content or ""
    lines = s.splitlines() or [s]
    longest = max((len(line) for line in lines), default=len(s))
    longest = min(longest, int(max_px / _CHAR_EST_PX))
    est = _HPAD_EST + longest * _CHAR_EST_PX
    return max(min_px, min(max_px, est))


def _user_markdown_sheet(theme: Mapping[str, Any]) -> ft.MarkdownStyleSheet:
    fg = theme["text"]
    link = theme["accent_2"]
    body = ft.TextStyle(color=fg, size=14, height=1.45)
    head = ft.TextStyle(color=fg, size=15, height=1.35, weight=ft.FontWeight.W_600)
    return ft.MarkdownStyleSheet(
        p_text_style=body,
        h1_text_style=head,
        h2_text_style=head,
        h3_text_style=head,
        h4_text_style=head,
        h5_text_style=head,
        h6_text_style=head,
        strong_text_style=ft.TextStyle(
            color=fg, size=14, height=1.45, weight=ft.FontWeight.W_700,
        ),
        a_text_style=ft.TextStyle(color=link, size=14, weight=ft.FontWeight.W_600),
        code_text_style=ft.TextStyle(
            color=fg, size=13, font_family="Consolas, monospace",
        ),
    )


def _assistant_markdown_sheet(theme: Mapping[str, Any]) -> ft.MarkdownStyleSheet:
    fg = theme["text"]
    sec = theme["text_secondary"]
    link = theme["accent_2"]
    body = ft.TextStyle(color=fg, size=14, height=1.5)
    return ft.MarkdownStyleSheet(
        p_text_style=body,
        h1_text_style=ft.TextStyle(color=fg, size=17, weight=ft.FontWeight.W_700, height=1.35),
        h2_text_style=ft.TextStyle(color=fg, size=16, weight=ft.FontWeight.W_700, height=1.35),
        h3_text_style=ft.TextStyle(color=fg, size=15, weight=ft.FontWeight.W_600, height=1.35),
        h4_text_style=ft.TextStyle(color=fg, size=14, weight=ft.FontWeight.W_600, height=1.35),
        h5_text_style=ft.TextStyle(color=fg, size=14, weight=ft.FontWeight.W_600),
        h6_text_style=ft.TextStyle(color=fg, size=13, weight=ft.FontWeight.W_600),
        strong_text_style=ft.TextStyle(
            color=fg, size=14, weight=ft.FontWeight.W_700, height=1.5,
        ),
        a_text_style=ft.TextStyle(color=link, size=14, weight=ft.FontWeight.W_600),
        code_text_style=ft.TextStyle(
            color=fg, size=13, font_family="Consolas, monospace",
        ),
        list_bullet_text_style=ft.TextStyle(color=sec, size=14, height=1.5),
    )


def chat_bubble(
    *,
    role: str,
    content: str,
    author_name: str = "",
    theme: Mapping[str, Any] | None = None,
    page: ft.Page | None = None,
    user_avatar_url: str | None = None,
    user_header_title: str | None = None,
) -> ft.Control:
    is_user = role == "user"
    glass = dashboard_glass_tokens(theme) if theme is not None else None
    if theme is not None:
        name_color = theme["text_muted"]
        md_theme = theme.get("markdown_code_theme", "atom-one-dark")
        if glass is not None and str(theme.get("page_bg", "")).lower() == "#020617":
            user_bg = glass["card_bg"]
            user_border = ft.colors.with_opacity(0.42, glass["teal"])
            user_shadow_c = ft.colors.with_opacity(0.18, glass["teal"])
            ai_bg = glass["header_bg"]
            ai_border = ft.colors.with_opacity(0.55, glass["card_border"])
            ai_border_glow = ft.colors.with_opacity(0.22, glass["teal"])
        else:
            user_bg = ft.colors.with_opacity(0.88, theme["surface_3"])
            user_border = ft.colors.with_opacity(0.55, theme["accent_2"])
            user_shadow_c = ft.colors.with_opacity(0.14, theme["accent_2"])
            ai_bg = ft.colors.with_opacity(0.92, theme["surface_2"])
            ai_border = ft.colors.with_opacity(0.55, theme["border_strong"])
            ai_border_glow = ft.colors.with_opacity(0.2, theme["accent_2"])
    else:
        name_color = Colors.text_muted
        md_theme = "atom-one-dark"
        user_bg = Colors.surface_3
        user_border = ft.colors.with_opacity(0.45, Colors.accent_cyan)
        user_shadow_c = ft.colors.with_opacity(0.16, Colors.accent_cyan)
        ai_bg = ft.colors.with_opacity(0.92, Colors.surface_2)
        ai_border = ft.colors.with_opacity(0.5, Colors.border_strong)
        ai_border_glow = ft.colors.with_opacity(0.18, Colors.accent_cyan)

    if not is_user:
        avatar = brand_icon(size=32, radius=8)

    max_px = _USER_BUBBLE_MAX_PX if is_user else _AI_BUBBLE_MAX_PX
    md_width = _bubble_content_width(content, max_px)

    if is_user:
        md_sheet = _user_markdown_sheet(theme) if theme is not None else None
        user_shadow = (
            ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=user_shadow_c,
                offset=ft.Offset(0, 2),
            ),
        )
    else:
        md_sheet = _assistant_markdown_sheet(theme) if theme is not None else None
        user_shadow = None

    text = ft.Markdown(
        value=content,
        selectable=True,
        shrink_wrap=True,
        fit_content=True,
        extension_set=ft.MarkdownExtensionSet.GITHUB_FLAVORED,
        code_theme=md_theme,
        md_style_sheet=md_sheet,
        width=md_width,
    )

    if is_user:
        bubble = ft.Container(
            content=text,
            bgcolor=user_bg,
            padding=ft.padding.symmetric(horizontal=Spacing.md, vertical=Spacing.sm),
            border_radius=Radii.md,
            border=ft.border.all(1, user_border),
            shadow=user_shadow,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        )
    else:
        bubble = ft.Container(
            content=text,
            bgcolor=ai_bg,
            padding=ft.padding.symmetric(horizontal=Spacing.md, vertical=Spacing.sm),
            border_radius=Radii.md,
            border=ft.border.all(1, ai_border),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=6,
                color=ai_border_glow,
                offset=ft.Offset(0, 1),
            ),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        )

    subtle = ft.TextStyle(size=9, weight=ft.FontWeight.W_600, color=name_color)

    if is_user:
        header_title = default_user_header_title(author_name, title_override=user_header_title)
        identity_header = build_user_identity_header_row(
            title=header_title,
            author_name=author_name,
            avatar_url=user_avatar_url,
            theme=theme,
            name_style=subtle,
        )
        user_controls: list[ft.Control] = [identity_header, bubble]
        if page is not None:
            user_controls.append(
                ft.Row(
                    tight=True,
                    spacing=0,
                    alignment=ft.MainAxisAlignment.END,
                    controls=[
                        ft.IconButton(
                            icon=ft.icons.CONTENT_COPY_OUTLINED,
                            icon_size=_ACTION_ICON_SIZE,
                            tooltip="Copy message",
                            style=ft.ButtonStyle(
                                color={
                                    ft.ControlState.DEFAULT: _muted(theme),
                                    ft.ControlState.HOVERED: (
                                        theme["accent_2"]
                                        if theme is not None
                                        else Colors.accent_cyan
                                    ),
                                },
                                overlay_color=ft.colors.with_opacity(0.1, _accent(theme)),
                            ),
                            on_click=lambda e: _copy_to_clipboard(e, content, "Message copied"),
                        ),
                    ],
                ),
            )
        stack = ft.Column(
            controls=user_controls,
            spacing=4,
            horizontal_alignment=ft.CrossAxisAlignment.END,
            tight=True,
        )
        return ft.Row(
            expand=True,
            alignment=ft.MainAxisAlignment.END,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[ft.Container(expand=True), stack],
        )

    ai_title = ft.Text("StackWise AI", style=subtle)
    header = ft.Row(
        controls=[avatar, ai_title],
        spacing=6,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        tight=True,
    )
    ai_controls: list[ft.Control] = [header, bubble]
    if page is not None:
        muted = _muted(theme)
        up_ok = theme["success"] if theme is not None else Colors.success
        down_warn = theme["danger"] if theme is not None else Colors.danger
        feedback: dict[str, str | None] = {"v": None}
        up_ref: ft.Ref[ft.IconButton] = ft.Ref()
        dn_ref: ft.Ref[ft.IconButton] = ft.Ref()

        def _sync_thumb_styles() -> None:
            sel = feedback["v"]
            up = up_ref.current
            dn = dn_ref.current
            if up is None or dn is None:
                return
            up.icon_color = up_ok if sel == "up" else muted
            dn.icon_color = down_warn if sel == "down" else muted
            p = up.page
            if p:
                p.update()

        def _on_thumb(ev: ft.ControlEvent, which: str) -> None:
            if feedback["v"] == which:
                feedback["v"] = None
            else:
                feedback["v"] = which
                if ev.page:
                    show_toast(ev.page, "Feedback noted.", kind="info")
            _sync_thumb_styles()

        copy_ai = ft.IconButton(
            icon=ft.icons.CONTENT_COPY_OUTLINED,
            icon_size=_ACTION_ICON_SIZE,
            tooltip="Copy response",
            style=ft.ButtonStyle(
                color={
                    ft.ControlState.DEFAULT: muted,
                    ft.ControlState.HOVERED: (
                        theme["accent_2"] if theme is not None else Colors.accent_cyan
                    ),
                },
                overlay_color=ft.colors.with_opacity(0.1, _accent(theme)),
            ),
            on_click=lambda e: _copy_to_clipboard(e, content, "Response copied"),
        )
        thumb_up = ft.IconButton(
            ref=up_ref,
            icon=ft.icons.THUMB_UP_OUTLINED,
            icon_size=_ACTION_ICON_SIZE,
            icon_color=muted,
            tooltip="Good response",
            style=ft.ButtonStyle(
                color={
                    ft.ControlState.DEFAULT: muted,
                    ft.ControlState.HOVERED: (
                        theme["accent_2"] if theme is not None else Colors.accent_cyan
                    ),
                },
                overlay_color=ft.colors.with_opacity(0.1, _accent(theme)),
            ),
            on_click=lambda e: _on_thumb(e, "up"),
        )
        thumb_dn = ft.IconButton(
            ref=dn_ref,
            icon=ft.icons.THUMB_DOWN_OUTLINED,
            icon_size=_ACTION_ICON_SIZE,
            icon_color=muted,
            tooltip="Bad response",
            style=ft.ButtonStyle(
                color={
                    ft.ControlState.DEFAULT: muted,
                    ft.ControlState.HOVERED: (
                        theme["accent_2"] if theme is not None else Colors.accent_cyan
                    ),
                },
                overlay_color=ft.colors.with_opacity(0.1, _accent(theme)),
            ),
            on_click=lambda e: _on_thumb(e, "down"),
        )
        ai_controls.append(
            ft.Container(
                width=md_width,
                padding=ft.padding.only(top=2),
                content=ft.Row(
                    tight=True,
                    spacing=6,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[copy_ai, thumb_up, thumb_dn],
                ),
            ),
        )

    stack = ft.Column(
        controls=ai_controls,
        spacing=4,
        horizontal_alignment=ft.CrossAxisAlignment.START,
        tight=True,
    )
    return ft.Row(
        expand=True,
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[stack, ft.Container(expand=True)],
    )


def typing_bubble(theme: Mapping[str, Any] | None = None) -> ft.Control:
    if theme is not None:
        g = dashboard_glass_tokens(theme)
        if str(theme.get("page_bg", "")).lower() == "#020617":
            bg = g["header_bg"]
            bd = ft.colors.with_opacity(0.55, g["card_border"])
            ring = g["teal"]
        else:
            bg = ft.colors.with_opacity(0.92, theme["surface_2"])
            bd = ft.colors.with_opacity(0.55, theme["border_strong"])
            ring = theme["accent_2"]
        body_style = text_style(theme, size=13)
    else:
        bg = ft.colors.with_opacity(0.92, Colors.surface_2)
        bd = ft.colors.with_opacity(0.5, Colors.border_strong)
        ring = Colors.accent_cyan
        body_style = ft.TextStyle(size=13, color=Colors.text_secondary, height=1.5)

    thinking = ft.Container(
        content=ft.Row(
            controls=[
                ft.ProgressRing(width=14, height=14, stroke_width=2, color=ring),
                ft.Text("StackWise AI is thinking...", style=body_style),
            ],
            spacing=10,
            tight=True,
        ),
        bgcolor=bg,
        border=ft.border.all(1, bd),
        border_radius=Radii.md,
        padding=ft.padding.symmetric(horizontal=Spacing.md, vertical=Spacing.sm),
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=6,
            color=ft.colors.with_opacity(0.12, ring),
            offset=ft.Offset(0, 1),
        ),
    )

    ai_title = ft.Text(
        "StackWise AI",
        size=10,
        weight=ft.FontWeight.W_600,
        color=theme["text_muted"] if theme is not None else Colors.text_muted,
    )
    header = ft.Row(
        controls=[brand_icon(size=32, radius=8), ai_title],
        spacing=6,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        tight=True,
    )
    stack = ft.Column(
        controls=[header, thinking],
        spacing=4,
        horizontal_alignment=ft.CrossAxisAlignment.START,
        tight=True,
    )
    return ft.Row(
        expand=True,
        alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.START,
        controls=[stack, ft.Container(expand=True)],
    )
