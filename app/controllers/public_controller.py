"""PublicController — landing page + auth modal orchestration."""

from __future__ import annotations

import flet as ft

from app.controllers.base_controller import BaseController
from app.requests.login_request import LoginRequest
from app.requests.register_request import RegisterRequest
from ui.components.auth_modal import auth_modal
from ui.components.toast import show_toast
from ui.pages.login_page import build_login_form
from ui.pages.public_landing_page import build_public_landing_page
from ui.pages.register_page import build_register_form


class PublicController(BaseController):
    def build(self) -> ft.Control:
        return build_public_landing_page(
            on_login=lambda _e: self.open_login_modal(),
            on_register=lambda _e: self.open_register_modal(),
            on_create_account=self._create_account_cta,
            on_start_recommendation=self._start_recommendation,
        )

    def open_login_modal(self) -> None:
        self._show_dialog(self._build_login_dialog())

    def open_register_modal(self) -> None:
        self._show_dialog(self._build_register_dialog())

    def _start_recommendation(self, _e: ft.ControlEvent) -> None:
        if self.container.session.is_authenticated:
            self.navigation.to_recommendation()
            return
        self.open_login_modal()

    def _create_account_cta(self, _e: ft.ControlEvent) -> None:
        if self.container.session.is_authenticated:
            self.navigation.to_recommendation()
            return
        self.open_register_modal()

    def _build_login_dialog(self) -> ft.AlertDialog:
        error_container_ref = ft.Ref[ft.Container]()
        error_text_ref = ft.Ref[ft.Text]()
        progress_ref = ft.Ref[ft.ProgressRing]()
        submit_ref = ft.Ref[ft.Container]()
        fields: dict[str, ft.TextField] = {}

        def on_login(identifier: str, password: str) -> None:
            self._set_error(error_container_ref, error_text_ref, "")
            self._set_busy(progress_ref, submit_ref, True)
            try:
                request = LoginRequest(identifier=identifier, password=password)
                result = self.container.authentication_service.login(request)

                if not result.success:
                    msg = (
                        next(iter(result.errors.values())) if result.errors
                        else (result.message or "Sign-in failed.")
                    )
                    self._set_error(error_container_ref, error_text_ref, msg)
                    return

                assert result.user is not None
                self.container.session.login(result.user)
                show_toast(self.page, f"Welcome back, {result.user.full_name.split()[0]}!", kind="success")
                self._close_dialog()
                self.navigation.to_dashboard()
            finally:
                self._set_busy(progress_ref, submit_ref, False)

        form = build_login_form(
            on_login=on_login,
            on_go_register=lambda _e: self._show_dialog(self._build_register_dialog()),
            error_container_ref=error_container_ref,
            error_text_ref=error_text_ref,
            submitting_ref=progress_ref,
            submit_ref=submit_ref,
            fields=fields,
        )
        return auth_modal(form=form, on_close=lambda _e: self._close_dialog())

    def _build_register_dialog(self) -> ft.AlertDialog:
        error_container_ref = ft.Ref[ft.Container]()
        error_text_ref = ft.Ref[ft.Text]()
        progress_ref = ft.Ref[ft.ProgressRing]()
        submit_ref = ft.Ref[ft.Container]()
        fields: dict[str, ft.TextField] = {}

        def on_register(values: dict[str, str]) -> None:
            self._set_error(error_container_ref, error_text_ref, "")
            self._set_busy(progress_ref, submit_ref, True)
            try:
                request = RegisterRequest(
                    full_name=values.get("full_name", ""),
                    username=values.get("username", ""),
                    email=values.get("email", ""),
                    password=values.get("password", ""),
                    confirm_password=values.get("confirm_password", ""),
                )
                result = self.container.authentication_service.register(request)

                if not result.success:
                    msg = (
                        next(iter(result.errors.values())) if result.errors
                        else (result.message or "Registration failed.")
                    )
                    self._set_error(error_container_ref, error_text_ref, msg)
                    return

                assert result.user is not None
                self.container.session.login(result.user)
                show_toast(
                    self.page,
                    f"Account created — welcome, {result.user.full_name.split()[0]}!",
                    kind="success",
                )
                self._close_dialog()
                self.navigation.to_dashboard()
            finally:
                self._set_busy(progress_ref, submit_ref, False)

        form = build_register_form(
            on_register=on_register,
            on_go_login=lambda _e: self._show_dialog(self._build_login_dialog()),
            error_container_ref=error_container_ref,
            error_text_ref=error_text_ref,
            submitting_ref=progress_ref,
            submit_ref=submit_ref,
            fields=fields,
        )
        return auth_modal(form=form, on_close=lambda _e: self._close_dialog())

    def _show_dialog(self, dialog: ft.AlertDialog) -> None:
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _close_dialog(self) -> None:
        if self.page.dialog is None:
            return
        self.page.dialog.open = False
        self.page.update()

    def _set_error(
        self,
        container_ref: ft.Ref[ft.Container],
        text_ref: ft.Ref[ft.Text],
        message: str,
    ) -> None:
        container = container_ref.current
        text = text_ref.current
        if container is None or text is None:
            return
        text.value = message
        container.visible = bool(message)
        text.update()
        container.update()

    def _set_busy(self, ref: ft.Ref[ft.ProgressRing], submit_ref: ft.Ref[ft.Container], busy: bool) -> None:
        ring = ref.current
        submit = submit_ref.current

        if ring is not None:
            ring.visible = busy
            ring.update()

        if submit is None:
            return

        if busy:
            submit.on_click = None
            submit.opacity = 0.55
        else:
            handler = (submit.data or {}).get("on_click")
            submit.on_click = handler
            submit.opacity = 1.0
        submit.update()
