"""RecommendationController — UI controller and Phase 1 scoring entry point."""

from __future__ import annotations

from typing import Any

import flet as ft

from app.controllers._layout_helper import wrap_with_layout
from app.controllers.base_controller import BaseController
from app.requests.recommendation_request import PREFERRED_STACK_NONE, RecommendationRequest
from app.services.recommendation_service import RecommendationService
from app.utils.constants import (
    Routes,
    SESSION_RECOMMENDATION_INPUT,
    SESSION_RECOMMENDATION_RESULT,
    SESSION_SELECTED_RECOMMENDATION_ID,
    SESSION_SELECTED_RECOMMENDATION_INPUT,
    SESSION_SELECTED_RECOMMENDATION_RESULT,
    recommendation_result_route,
)
from app.utils.logger import get_logger
from app.services.recommendation_persistence_service import attach_saved_recommendation_id
from ui.pages.recommendation_page import (
    RecommendationFormFields,
    build_recommendation_page,
    recommendation_workspace_theme,
)
from ui.theme import get_theme, is_dark_mode

log = get_logger(__name__)


class RecommendationController(BaseController):
    def build(self) -> ft.Control:
        user = self.container.session.user
        assert user is not None

        theme = get_theme(is_dark_mode(self.page))
        rw = recommendation_workspace_theme(theme)
        fields = RecommendationFormFields(rw)
        error_ref = ft.Ref[ft.Text]()
        progress_ref = ft.Ref[ft.ProgressRing]()

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

                if user is None:
                    self._set_error(error_ref, "Please sign in again.")
                    return

                data = _form_to_engine_data(fields)
                response = generate_recommendation_from_request(data)
                if not response.get("success"):
                    err = response.get("error") or (
                        "Unable to generate recommendation. Please review your "
                        "project profile and try again."
                    )
                    self._set_error(error_ref, err)
                    return

                try:
                    saved = self.container.recommendation_persistence.save_engine_result(
                        user.id,
                        data,
                        response["data"],
                    )
                except Exception as exc:
                    log.exception("Database save failed after successful generation")
                    self._set_error(
                        error_ref,
                        "Your recommendation was generated but could not be saved. "
                        "Check that MySQL is running and try again.",
                    )
                    return

                result = response["data"]
                result = attach_saved_recommendation_id(result, saved.id)
                self._store_recommendation_session(data, result, saved.id)
                self.page.go(recommendation_result_route(saved.id))
            except Exception:
                log.exception("Generate recommendation failed")
                self._set_error(
                    error_ref,
                    "Unable to generate recommendation. Please review your inputs "
                    "and try again.",
                )
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
                if f.page:
                    f.update()
            for f in (
                fields.preferred_language_optional,
                fields.preferred_framework_optional,
                fields.preferred_sdlc_optional,
            ):
                f.value = PREFERRED_STACK_NONE
                if f.page:
                    f.update()
            fields.preferred_stack_reason_optional.value = ""
            if fields.preferred_stack_reason_optional.page:
                fields.preferred_stack_reason_optional.update()
            for cb in fields.feature_checks.values():
                cb.value = False
                if cb.page:
                    cb.update()
            self._set_error(error_ref, "")

        def on_back(_e: ft.ControlEvent) -> None:
            self.navigation.to_dashboard()

        body = build_recommendation_page(
            fields=fields,
            error_text_ref=error_ref,
            submitting_ref=progress_ref,
            on_generate=on_generate,
            on_reset=on_reset,
            on_back=on_back,
            theme=rw,
        )

        return wrap_with_layout(self, current_route=Routes.RECOMMENDATION, body=body, theme=theme)

    def _store_recommendation_session(
        self,
        input_data: dict[str, Any],
        result: dict[str, Any],
        recommendation_id: int,
    ) -> None:
        """Persist full engine payloads for the details page and regenerate flows."""
        self.page.session.set(SESSION_RECOMMENDATION_INPUT, input_data)
        self.page.session.set(SESSION_RECOMMENDATION_RESULT, result)
        self.page.session.set(SESSION_SELECTED_RECOMMENDATION_INPUT, input_data)
        self.page.session.set(SESSION_SELECTED_RECOMMENDATION_RESULT, result)
        self.page.session.set(SESSION_SELECTED_RECOMMENDATION_ID, recommendation_id)

    def _set_error(self, ref: ft.Ref[ft.Text], message: str) -> None:
        text = ref.current
        if text is None:
            return
        text.value = message
        text.visible = bool(message)
        if text.page:
            text.update()

    def _set_busy(self, ref: ft.Ref[ft.ProgressRing], busy: bool) -> None:
        ring = ref.current
        if ring is None:
            return
        ring.visible = busy
        if ring.page:
            ring.update()


# ---------------------------------------------------------------------------
# Phase 1 — thin scoring API (no Flet / DB)
# ---------------------------------------------------------------------------

_scoring_service = RecommendationService()


def generate_recommendation_from_request(data: dict[str, Any]) -> dict[str, Any]:
    """Validate input, run the weighted scoring engine, return a JSON-safe dict.

    Example::

        from app.controllers.recommendation_controller import (
            generate_recommendation_from_request,
        )
        result = generate_recommendation_from_request({...})
    """
    validation_error = _validate_scoring_payload(data)
    if validation_error:
        return {"success": False, "error": validation_error}

    try:
        outcome = _scoring_service.recommend(data)
        return {"success": True, "data": outcome}
    except Exception as exc:
        log.exception("Recommendation scoring failed")
        return {"success": False, "error": str(exc)}


def _validate_scoring_payload(data: dict[str, Any]) -> str | None:
    if not isinstance(data, dict):
        return "Request body must be a dictionary."

    project_name = str(data.get("project_name", "") or "").strip()
    if not project_name:
        return "project_name must not be empty."

    project_type = str(data.get("project_type", "") or "").strip()
    if not project_type:
        return "project_type must not be empty."

    project_goal = str(data.get("project_goal", "") or "").strip()
    if not project_goal:
        return "project_goal must not be empty."

    features = data.get("selected_features", [])
    if isinstance(features, str):
        features = [f.strip() for f in features.replace("|", ",").split(",") if f.strip()]
    if not isinstance(features, list):
        return "selected_features must be a list."

    return None


def _form_to_engine_data(fields: RecommendationFormFields) -> dict[str, Any]:
    """Map Step 01–04 form controls to the Phase 1 scoring engine request dict."""
    values = fields.values()
    preferred = fields.preferred_stack_values()
    return {
        "project_name": values["project_name"],
        "project_type": values["project_type"],
        "selected_features": fields.selected_features(),
        "team_size": values["team_size"] or "1",
        "complexity": values["complexity"] or "Medium",
        "preferred_platform": values["preferred_platform"] or "Web",
        "development_experience": values["development_experience"] or "Intermediate",
        "timeline": values["timeline"] or "Medium",
        "project_goal": values["project_goal"],
        "scalability_needs": values["scalability_needs"] or "Medium",
        "security_requirements": values["security_requirements"] or "Medium",
        "performance_requirements": values["performance_requirements"] or "Medium",
        "budget_constraints": values["budget_constraints"] or "Medium",
        "maintenance_expectations": values["maintenance_expectations"] or "Medium",
        "deployment_preference": values["deployment_preference"] or "Cloud",
        "requirements_stability": values["requirements_stability"] or "Mostly Stable",
        "stakeholder_involvement": values["stakeholder_involvement"] or "Medium",
        "user_preferred_language": preferred["user_preferred_language"],
        "user_preferred_framework": preferred["user_preferred_framework"],
        "user_preferred_sdlc": preferred["user_preferred_sdlc"],
        "user_preferred_reason": preferred["user_preferred_reason"],
    }
