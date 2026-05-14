"""RecommendationController."""

from __future__ import annotations

import flet as ft

from app.controllers._layout_helper import wrap_with_layout
from app.controllers.base_controller import BaseController
from app.requests.recommendation_request import RecommendationRequest
from app.utils.constants import Routes
from ui.components.toast import show_toast
from ui.dialogs.recommendation_detail_dialog import build_recommendation_detail_dialog
from ui.pages.recommendation_page import (
    RecommendationFormFields,
    build_recommendation_page,
    recommendation_workspace_theme,
)
from ui.theme import get_theme, is_dark_mode
from ui.widgets.recommendation_card import recommendation_result_card


class RecommendationController(BaseController):
    def build(self) -> ft.Control:
        user = self.container.session.user
        assert user is not None

        theme = get_theme(is_dark_mode(self.page))
        rw = recommendation_workspace_theme(theme)
        fields = RecommendationFormFields(rw)
        error_ref = ft.Ref[ft.Text]()
        progress_ref = ft.Ref[ft.ProgressRing]()
        result_panel_ref = ft.Ref[ft.Column]()

        def on_generate(_e: ft.ControlEvent) -> None:
            self._set_error(error_ref, "")
            self._set_busy(progress_ref, True)
            try:
                values = fields.values()
                request = RecommendationRequest(**values)
                if not request.is_valid():
                    first = request.first_error() or "Please fill the form."
                    self._set_error(error_ref, first)
                    return

                outcome = self.container.recommendation_service.generate(request)
                rec = self.container.recommendation_service.save(user.id, request, outcome)

                show_toast(self.page, "Recommendation generated successfully.", kind="success")

                panel = result_panel_ref.current
                if panel is not None:
                    th = recommendation_workspace_theme(get_theme(is_dark_mode(self.page)))
                    panel.controls = [
                        recommendation_result_card(
                            rec,
                            theme=th,
                            on_view=lambda _e, r=rec: self._show_detail(r),
                            on_regenerate=lambda _e, r=rec: self._regenerate(r),
                        )
                    ]
                    panel.update()
            finally:
                self._set_busy(progress_ref, False)

        def on_reset(_e: ft.ControlEvent) -> None:
            for f in (
                fields.project_name,
                fields.project_type,
                fields.project_goal,
                fields.team_size,
                fields.complexity,
                fields.timeline,
                fields.requirements_stability,
                fields.stakeholder_involvement,
                fields.preferred_platform,
                fields.development_experience,
                fields.scalability_needs,
                fields.performance_requirements,
                fields.security_requirements,
                fields.budget_constraints,
                fields.maintenance_expectations,
                fields.deployment_preference,
            ):
                f.value = None if isinstance(f, ft.Dropdown) else ""
                f.update()
            for cb in fields.feature_checks.values():
                cb.value = False
                cb.update()
            self._set_error(error_ref, "")

        def on_back(_e: ft.ControlEvent) -> None:
            self.navigation.to_dashboard()

        body = build_recommendation_page(
            fields=fields,
            error_text_ref=error_ref,
            submitting_ref=progress_ref,
            result_panel_ref=result_panel_ref,
            on_generate=on_generate,
            on_reset=on_reset,
            on_back=on_back,
            theme=rw,
        )

        return wrap_with_layout(self, current_route=Routes.RECOMMENDATION, body=body, theme=theme)

    # ---------- helpers ----------

    def _show_detail(self, rec) -> None:
        dialog = build_recommendation_detail_dialog(rec, on_close=lambda _e: self._close_dialog())
        self._open_dialog(dialog)

    def _regenerate(self, rec) -> None:
        user = self.container.session.user
        if user is None:
            return
        new_rec = self.container.recommendation_service.regenerate(user.id, rec.id)
        if new_rec is not None:
            show_toast(self.page, "Recommendation regenerated.", kind="success")
            self.navigation.to_history()

    def _open_dialog(self, dialog: ft.AlertDialog) -> None:
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _close_dialog(self) -> None:
        if self.page.dialog is not None:
            self.page.dialog.open = False
            self.page.update()

    def _set_error(self, ref: ft.Ref[ft.Text], message: str) -> None:
        text = ref.current
        if text is None:
            return
        text.value = message
        text.visible = bool(message)
        text.update()

    def _set_busy(self, ref: ft.Ref[ft.ProgressRing], busy: bool) -> None:
        ring = ref.current
        if ring is None:
            return
        ring.visible = busy
        ring.update()
