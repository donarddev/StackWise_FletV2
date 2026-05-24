"""RecommendationResultController — full-page decision report for one recommendation."""

from __future__ import annotations

from typing import Any, Optional
from urllib.parse import urlparse

import flet as ft

from app.controllers._layout_helper import wrap_with_layout
from app.controllers.base_controller import BaseController
from app.controllers.recommendation_controller import generate_recommendation_from_request
from app.models.recommendation import Recommendation
from app.helpers.recommendation_engine_compat import normalize_engine_result_for_ui
from app.services.recommendation_persistence_service import apply_engine_snapshot_to_recommendation
from app.utils.logger import get_logger
from app.utils.constants import (
    Routes,
    SESSION_RECOMMENDATION_INPUT,
    SESSION_RECOMMENDATION_RESULT,
    SESSION_SELECTED_RECOMMENDATION_ID,
    SESSION_SELECTED_RECOMMENDATION_INPUT,
    SESSION_SELECTED_RECOMMENDATION_RESULT,
    recommendation_result_route,
)
from ui.components.toast import show_toast
from ui.dialogs.recommendation_detail_dialog import build_summary_clipboard_text
from ui.components.recommendation_decision_report import build_feedback_card_content
from ui.pages.recommendation_page import recommendation_workspace_theme
from ui.pages.recommendation_result_page import build_recommendation_result_page
from ui.pages.recommendation_session_report_page import (
    build_session_recommendation_report,
    build_session_summary_clipboard_text,
    format_generated_label,
)
from ui.theme import get_theme, is_dark_mode
from ui.themes.app_theme import Colors, Radii, Typography

log = get_logger(__name__)


class RecommendationResultController(BaseController):
    def build(self) -> ft.Control:
        user = self.container.session.user
        assert user is not None

        theme = get_theme(is_dark_mode(self.page))
        rec_id = self._resolve_recommendation_id()

        session_result, session_input = self._get_session_engine_payload()
        session_id = self.page.session.get(SESSION_SELECTED_RECOMMENDATION_ID)

        if (
            rec_id is not None
            and session_result
            and session_id is not None
            and int(session_id) == rec_id
        ):
            return self._build_fresh_engine_report(
                theme,
                user.id,
                rec_id,
                session_result,
                session_input,
            )

        if rec_id is not None:
            return self._build_saved_report(theme, user.id, rec_id)

        path = urlparse(self.page.route or "").path
        if path == Routes.RECOMMENDATION_RESULT:
            return self._build_session_fallback(theme)

        return self._build_saved_report(theme, user.id, None)

    def _get_session_engine_payload(
        self,
    ) -> tuple[Optional[dict[str, Any]], Optional[dict[str, Any]]]:
        raw_result = self.page.session.get(SESSION_SELECTED_RECOMMENDATION_RESULT)
        if not raw_result:
            raw_result = self.page.session.get(SESSION_RECOMMENDATION_RESULT)
        raw_input = self.page.session.get(SESSION_SELECTED_RECOMMENDATION_INPUT)
        if not raw_input:
            raw_input = self.page.session.get(SESSION_RECOMMENDATION_INPUT)
        result = normalize_engine_result_for_ui(raw_result) if raw_result else None
        return result, raw_input

    def _build_fresh_engine_report(
        self,
        theme: dict,
        user_id: int,
        rec_id: int,
        session_result: dict[str, Any],
        session_input: Optional[dict[str, Any]],
    ) -> ft.Control:
        """Show the exact engine payload from session right after generation."""
        loaded = self.container.recommendation_repository.find_by_id(rec_id)
        if loaded is not None and loaded.user_id == user_id:
            self.container.recommendation_repository.add_history(user_id, rec_id, "viewed")

        inp = session_input or {}
        if loaded is not None and not inp:
            inp = self.container.recommendation_persistence.input_data_from_recommendation(
                loaded
            )

        def on_copy(_e: ft.ControlEvent) -> None:
            if not session_result or not inp:
                show_toast(self.page, "Nothing to copy yet.", kind="warning")
                return
            self.page.set_clipboard(
                build_session_summary_clipboard_text(session_result, inp)
            )
            show_toast(self.page, "Summary copied to clipboard.", kind="success")

        def on_regenerate(_e: ft.ControlEvent) -> None:
            self._regenerate_from_input(inp)

        body = build_session_recommendation_report(
            result=session_result,
            input_data=inp,
            theme=theme,
            generated_label=format_generated_label(),
            on_back_recommendation=lambda _e: self.navigation.to_recommendation(),
            on_back_history=lambda _e: self.navigation.to_history(),
            on_copy_summary=on_copy,
            on_regenerate=on_regenerate if inp else None,
            on_dashboard=lambda _e: self.navigation.to_dashboard(),
        )
        return wrap_with_layout(
            self,
            current_route=recommendation_result_route(rec_id),
            body=body,
            theme=theme,
        )

    def _resolve_recommendation_id(self) -> Optional[int]:
        rec_id = self._parse_id_from_route()
        if rec_id is not None:
            return rec_id
        raw = self.page.session.get(SESSION_SELECTED_RECOMMENDATION_ID)
        if raw is not None and str(raw).isdigit():
            return int(raw)
        return None

    def _build_saved_report(
        self,
        theme: dict,
        user_id: int,
        rec_id: Optional[int],
    ) -> ft.Control:
        rec: Optional[Recommendation] = None
        not_found = rec_id is None

        feedback_section_ref = ft.Ref[ft.Container]()
        feedback_rating_ref = ft.Ref[ft.RadioGroup]()
        feedback_comment_ref = ft.Ref[ft.TextField]()
        feedback_error_ref = ft.Ref[ft.Text]()
        feedback_success_ref = ft.Ref[ft.Text]()
        feedback_submit_btn_ref = ft.Ref[ft.Container]()
        existing_feedback = None

        if rec_id is not None:
            loaded = self.container.recommendation_repository.find_by_id(rec_id)
            if loaded is None or loaded.user_id != user_id:
                not_found = True
            else:
                rec = apply_engine_snapshot_to_recommendation(loaded)
                self.container.recommendation_repository.add_history(
                    user_id, rec.id, "viewed"
                )
                existing_feedback = self.container.feedback_service.get_for_recommendation(
                    user_id, rec.id
                )

        def on_regenerate(_e: ft.ControlEvent) -> None:
            if rec is not None:
                self._open_regenerate_confirm(rec)

        def on_feedback(_e: ft.ControlEvent) -> None:
            if rec is None:
                return
            self._reveal_feedback_section(
                existing_feedback=existing_feedback,
                section_ref=feedback_section_ref,
                error_ref=feedback_error_ref,
                success_ref=feedback_success_ref,
            )

        def on_submit_feedback(_e: ft.ControlEvent) -> None:
            if rec is None:
                return
            self._submit_feedback(
                theme=theme,
                user_id=user_id,
                recommendation_id=rec.id,
                section_ref=feedback_section_ref,
                rating_ref=feedback_rating_ref,
                comment_ref=feedback_comment_ref,
                error_ref=feedback_error_ref,
                success_ref=feedback_success_ref,
                submit_btn_ref=feedback_submit_btn_ref,
            )

        body = build_recommendation_result_page(
            rec=rec,
            theme=theme,
            not_found=not_found,
            on_back_recommendation=lambda _e: self.navigation.to_recommendation(),
            on_back_history=lambda _e: self.navigation.to_history(),
            on_dashboard=lambda _e: self.navigation.to_dashboard(),
            on_regenerate=on_regenerate if rec is not None else None,
            on_copy_summary=(lambda _e, r=rec: self._copy_summary(r)) if rec is not None else None,
            on_feedback=on_feedback if rec is not None else None,
            on_submit_feedback=on_submit_feedback if rec is not None else None,
            existing_feedback=existing_feedback,
            feedback_section_ref=feedback_section_ref,
            feedback_rating_ref=feedback_rating_ref,
            feedback_comment_ref=feedback_comment_ref,
            feedback_error_ref=feedback_error_ref,
            feedback_success_ref=feedback_success_ref,
            feedback_submit_btn_ref=feedback_submit_btn_ref,
        )

        current = self.page.route or Routes.RECOMMENDATION_RESULT
        if rec is not None:
            current = recommendation_result_route(rec.id)
        return wrap_with_layout(self, current_route=current, body=body, theme=theme)

    def _reveal_feedback_section(
        self,
        *,
        existing_feedback,
        section_ref: ft.Ref[ft.Container],
        error_ref: ft.Ref[ft.Text],
        success_ref: ft.Ref[ft.Text],
    ) -> None:
        """Quick action: reveal or scroll to the feedback card only."""
        if existing_feedback is not None:
            self._scroll_to_feedback(section_ref)
            return

        section = section_ref.current
        if section is None:
            return

        if not section.visible:
            section.visible = True
            if section.page:
                section.update()
        self._clear_feedback_messages(error_ref, success_ref)
        self._scroll_to_feedback(section_ref)

    def _submit_feedback(
        self,
        *,
        theme: dict,
        user_id: int,
        recommendation_id: int,
        section_ref: ft.Ref[ft.Container],
        rating_ref: ft.Ref[ft.RadioGroup],
        comment_ref: ft.Ref[ft.TextField],
        error_ref: ft.Ref[ft.Text],
        success_ref: ft.Ref[ft.Text],
        submit_btn_ref: ft.Ref[ft.Container],
    ) -> None:
        """Validate, save feedback, and refresh the feedback card in place."""
        self._clear_feedback_messages(error_ref, success_ref)

        rating_val = None
        if rating_ref.current is not None:
            rating_val = rating_ref.current.value

        if not rating_val:
            self._set_feedback_message(
                error_ref,
                "Please select a rating before submitting.",
                success_ref=success_ref,
            )
            return

        comment_val = ""
        if comment_ref.current is not None:
            comment_val = comment_ref.current.value or ""

        self._set_submit_button_loading(submit_btn_ref, loading=True)

        result = self.container.feedback_service.submit(
            user_id,
            recommendation_id,
            rating_val,
            comment_val,
        )

        self._set_submit_button_loading(submit_btn_ref, loading=False)

        if not result.success:
            self._set_feedback_message(
                error_ref,
                result.message,
                success_ref=success_ref,
            )
            if result.message != "Please select a rating before submitting.":
                show_toast(self.page, result.message, kind="warning")
            return

        saved = result.feedback
        self._refresh_feedback_section(
            theme=theme,
            section_ref=section_ref,
            saved_feedback=saved,
        )
        show_toast(self.page, "Feedback submitted successfully.", kind="success")

    def _refresh_feedback_section(
        self,
        *,
        theme: dict,
        section_ref: ft.Ref[ft.Container],
        saved_feedback,
    ) -> None:
        """Replace feedback card content after a successful save (no page redirect)."""
        section = section_ref.current
        if section is None:
            return

        rw = recommendation_workspace_theme(theme)
        section.content = build_feedback_card_content(
            rw,
            existing_feedback=saved_feedback,
            can_submit=False,
        )
        if section.page:
            section.update()

    @staticmethod
    def _set_submit_button_loading(
        submit_btn_ref: ft.Ref[ft.Container],
        *,
        loading: bool,
    ) -> None:
        btn = submit_btn_ref.current
        if btn is None:
            return
        stored_click = None
        if isinstance(btn.data, dict):
            stored_click = btn.data.get("on_click")

        if loading:
            btn.on_click = None
            btn.opacity = 0.55
        else:
            btn.on_click = stored_click
            btn.opacity = 1.0

        label = btn.content
        if isinstance(label, ft.Row):
            for ctrl in label.controls:
                if isinstance(ctrl, ft.Text):
                    ctrl.value = "Submitting..." if loading else "Submit Feedback"
                    if ctrl.page:
                        ctrl.update()
                    break
        if btn.page:
            btn.update()

    def _scroll_to_feedback(self, section_ref: ft.Ref[ft.Container]) -> None:
        section = section_ref.current
        if section is None:
            return
        try:
            self.page.scroll_to(section, duration=300)
        except Exception:
            pass

    @staticmethod
    def _set_feedback_message(
        ref: ft.Ref[ft.Text],
        message: str,
        *,
        error_ref: Optional[ft.Ref[ft.Text]] = None,
        success_ref: Optional[ft.Ref[ft.Text]] = None,
    ) -> None:
        text = ref.current
        if text is None:
            return
        text.value = message
        text.visible = bool(message)
        if text.page:
            text.update()
        if error_ref is not None and error_ref is not ref:
            other = error_ref.current
            if other is not None:
                other.visible = False
                if other.page:
                    other.update()
        if success_ref is not None and success_ref is not ref:
            other = success_ref.current
            if other is not None:
                other.visible = False
                if other.page:
                    other.update()

    @staticmethod
    def _clear_feedback_messages(
        error_ref: ft.Ref[ft.Text],
        success_ref: ft.Ref[ft.Text],
    ) -> None:
        for ref in (error_ref, success_ref):
            text = ref.current
            if text is None:
                continue
            text.value = ""
            text.visible = False
            if text.page:
                text.update()

    def _build_session_fallback(self, theme: dict) -> ft.Control:
        """Fallback when route has no ID but session still holds a fresh result."""
        result = normalize_engine_result_for_ui(
            self.page.session.get(SESSION_RECOMMENDATION_RESULT)
            or self.page.session.get(SESSION_SELECTED_RECOMMENDATION_RESULT)
        )
        input_data = (
            self.page.session.get(SESSION_RECOMMENDATION_INPUT)
            or self.page.session.get(SESSION_SELECTED_RECOMMENDATION_INPUT)
        )
        session_id = self.page.session.get(SESSION_SELECTED_RECOMMENDATION_ID)

        if session_id and str(session_id).isdigit() and result:
            user = self.container.session.user
            if user is not None:
                loaded = self.container.recommendation_repository.find_by_id(
                    int(session_id)
                )
                if loaded is not None and loaded.user_id == user.id:
                    self.page.go(recommendation_result_route(loaded.id))
                    return ft.Container()

        def on_copy(_e: ft.ControlEvent) -> None:
            if not result or not input_data:
                show_toast(self.page, "Nothing to copy yet.", kind="warning")
                return
            self.page.set_clipboard(
                build_session_summary_clipboard_text(result, input_data)
            )
            show_toast(self.page, "Summary copied to clipboard.", kind="success")

        def on_regenerate(_e: ft.ControlEvent) -> None:
            self._regenerate_from_input(input_data)

        body = build_session_recommendation_report(
            result=result,
            input_data=input_data,
            theme=theme,
            generated_label=format_generated_label(),
            on_back_recommendation=lambda _e: self.navigation.to_recommendation(),
            on_back_history=lambda _e: self.navigation.to_history(),
            on_copy_summary=on_copy,
            on_regenerate=on_regenerate if input_data else None,
            on_dashboard=lambda _e: self.navigation.to_dashboard(),
        )
        return wrap_with_layout(
            self,
            current_route=Routes.RECOMMENDATION_RESULT,
            body=body,
            theme=theme,
        )

    def _regenerate_from_input(self, input_data: Optional[dict]) -> None:
        user = self.container.session.user
        if user is None:
            show_toast(self.page, "Please sign in again.", kind="warning")
            return
        if not input_data:
            show_toast(
                self.page,
                "Original project profile not found. Return to the form.",
                kind="warning",
            )
            return
        response = generate_recommendation_from_request(input_data)
        if not response.get("success"):
            err = response.get("error") or "Regeneration failed."
            show_toast(self.page, err, kind="warning")
            return
        try:
            saved = self.container.recommendation_persistence.save_engine_result(
                user.id,
                input_data,
                response["data"],
            )
        except Exception:
            show_toast(
                self.page,
                "Regeneration succeeded but could not be saved to the database.",
                kind="warning",
            )
            return
        result = response["data"]
        self.page.session.set(SESSION_RECOMMENDATION_INPUT, input_data)
        self.page.session.set(SESSION_RECOMMENDATION_RESULT, result)
        self.page.session.set(SESSION_SELECTED_RECOMMENDATION_INPUT, input_data)
        self.page.session.set(SESSION_SELECTED_RECOMMENDATION_RESULT, result)
        self.page.session.set(SESSION_SELECTED_RECOMMENDATION_ID, saved.id)
        show_toast(self.page, "Recommendation regenerated.", kind="success")
        self.page.go(recommendation_result_route(saved.id))

    def _parse_id_from_route(self) -> Optional[int]:
        path = urlparse(self.page.route or "").path
        prefix = f"{Routes.RECOMMENDATION_RESULT}/"
        if not path.startswith(prefix):
            return None
        tail = path[len(prefix) :].strip("/").split("/")[0]
        if not tail.isdigit():
            return None
        return int(tail)

    def _copy_summary(self, rec: Optional[Recommendation]) -> None:
        if rec is None:
            return
        self.page.set_clipboard(build_summary_clipboard_text(rec))
        show_toast(self.page, "Summary copied to clipboard.", kind="success")

    def _open_regenerate_confirm(self, rec: Recommendation) -> None:
        def cancel(_: ft.ControlEvent) -> None:
            self._close_dialog()

        def go(_: ft.ControlEvent) -> None:
            self._close_dialog()
            input_data = (
                self.container.recommendation_persistence.input_data_from_recommendation(
                    rec
                )
            )
            self._regenerate_from_input(input_data)

        dlg = ft.AlertDialog(
            modal=True,
            bgcolor=Colors.surface_2,
            alignment=ft.alignment.center,
            shape=ft.RoundedRectangleBorder(radius=Radii.lg),
            title=ft.Text("Regenerate recommendation?", weight=ft.FontWeight.W_600),
            content=ft.Container(
                width=440,
                content=ft.Text(
                    "Regenerate will re-run the recommendation engine using the saved "
                    "project profile. A new recommendation row will be added to your history.",
                    style=Typography.body(size=14),
                ),
            ),
            actions=[
                ft.TextButton("Cancel", on_click=cancel),
                ft.TextButton("Regenerate", icon=ft.icons.REFRESH_ROUNDED, on_click=go),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self._open_dialog(dlg)

    def _open_dialog(self, dialog: ft.AlertDialog) -> None:
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _close_dialog(self) -> None:
        if self.page.dialog is not None:
            self.page.dialog.open = False
            self.page.update()
