"""Reusable animation primitives.

Use the helpers here to keep motion consistent across the app
(durations, curves, fade-in patterns).
"""

from __future__ import annotations

import flet as ft


class Motion:
    fast = 180
    base = 280
    slow = 520

    @staticmethod
    def fade(duration: int = 280) -> ft.Animation:
        return ft.Animation(duration, ft.AnimationCurve.EASE_OUT)

    @staticmethod
    def smooth(duration: int = 320) -> ft.Animation:
        return ft.Animation(duration, ft.AnimationCurve.EASE_IN_OUT)

    @staticmethod
    def bounce(duration: int = 420) -> ft.Animation:
        return ft.Animation(duration, ft.AnimationCurve.EASE_OUT_BACK)
