"""AuthTextField — auth-focused wrapper around input_field."""

from __future__ import annotations

from typing import Optional

import flet as ft

from ui.components.input_field import input_field


def auth_text_field(
    label: str,
    *,
    icon: Optional[str] = None,
    autofocus: bool = False,
    password: bool = False,
    on_submit=None,
) -> ft.TextField:
    return input_field(
        label,
        icon=icon,
        autofocus=autofocus,
        password=password,
        on_submit=on_submit,
    )

