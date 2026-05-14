"""AuthController — wires the login/register pages to AuthenticationService."""

from __future__ import annotations

import flet as ft

from app.controllers.base_controller import BaseController
from app.requests.login_request import LoginRequest
from app.requests.register_request import RegisterRequest
from app.utils.constants import Routes
from ui.components.toast import show_toast
from ui.pages.login_page import build_login_page
from ui.pages.register_page import build_register_page
from app.services.google_auth_service import GoogleAuthError
from app.utils.logger import get_logger

log = get_logger(__name__)


class AuthController(BaseController):
    # ---------- pages ----------

    def build_login(self) -> ft.Control:
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
                self.navigation.to_dashboard()
            finally:
                self._set_busy(progress_ref, submit_ref, False)

        def on_google(_e: ft.ControlEvent) -> None:
            try:
                url = self.container.google_auth_service.build_authorization_url()
            except GoogleAuthError as exc:
                show_toast(self.page, str(exc), kind="error")
                return
            # Open browser to Google's consent page
            self.page.launch_url(url)

        def go_register(_e: ft.ControlEvent) -> None:
            self.navigation.to_register()

        return build_login_page(
            on_login=on_login,
            on_google=on_google,
            on_go_register=go_register,
            error_container_ref=error_container_ref,
            error_text_ref=error_text_ref,
            submitting_ref=progress_ref,
            submit_ref=submit_ref,
            fields=fields,
        )

    def build_register(self) -> ft.Control:
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
                self.navigation.to_dashboard()
            finally:
                self._set_busy(progress_ref, submit_ref, False)

        def go_login(_e: ft.ControlEvent) -> None:
            self.navigation.to_login()

        def on_google(_e: ft.ControlEvent) -> None:
            try:
                url = self.container.google_auth_service.build_authorization_url()
            except GoogleAuthError as exc:
                show_toast(self.page, str(exc), kind="error")
                return
            self.page.launch_url(url)

        return build_register_page(
            on_register=on_register,
            on_google=on_google,
            on_go_login=go_login,
            error_container_ref=error_container_ref,
            error_text_ref=error_text_ref,
            submitting_ref=progress_ref,
            submit_ref=submit_ref,
            fields=fields,
        )

    def handle_oauth_callback(self, params: dict) -> None:
        """Handle the redirect from Google with `code` and `state` parameters."""
        code = params.get("code")
        state = params.get("state")
        error = params.get("error")
        returned_state = state or ""

        log.info("Google OAuth callback received")
        log.info("Google OAuth returned state prefix: %s", returned_state[:8])

        if error:
            log.info("Google OAuth callback returned error: %s", error)
            show_toast(self.page, f"Google sign-in failed: {error}", kind="error")
            self.navigation.to_login()
            return

        state_payload = self.container.google_auth_service.validate_oauth_state(state)
        state_found = state_payload is not None
        log.info("Google OAuth state found: %s", state_found)
        if not state_found:
            self._show_oauth_message(
                "Google sign-in session expired",
                "Please close this tab and try signing in again.",
            )
            return

        if not code:
            self._show_oauth_message(
                "Google sign-in did not finish",
                "Google did not return a verification code. Please close this tab and try again.",
            )
            return

        try:
            profile = self.container.google_auth_service.exchange_code_for_profile(code)
        except Exception:
            log.exception("Failed to verify Google account")
            self._show_oauth_message(
                "Google sign-in failed",
                "We could not verify your Google account. Please close this tab and try again.",
            )
            return

        result = self.container.authentication_service.authenticate_google_user(profile)
        if not result.success or result.user is None:
            self._show_oauth_message(
                "Google sign-in failed",
                result.message or "We could not sign you in with Google. Please try again.",
            )
            return

        # Successful — create session and navigate
        self.container.session.login(result.user)
        show_toast(self.page, f"Welcome, {result.user.full_name.split()[0]}!", kind="success")
        redirect_target = str(state_payload.get("redirect_after_login") or Routes.DASHBOARD)
        log.info("Google OAuth final redirect target: %s", redirect_target)
        self.navigation.go(redirect_target)

    # ---------- helpers ----------

    def logout(self) -> None:
        self.container.session.logout()
        self.navigation.to_home()

    def _show_oauth_message(self, title: str, message: str) -> None:
        """Render a friendly OAuth callback message instead of a raw JSON page."""
        self.page.views.clear()
        self.page.views.append(
            ft.View(
                route=Routes.OAUTH_CALLBACK,
                padding=0,
                controls=[
                    ft.Container(
                        expand=True,
                        alignment=ft.alignment.center,
                        bgcolor="#0B1020",
                        content=ft.Container(
                            width=520,
                            padding=32,
                            border_radius=18,
                            bgcolor="#111827",
                            content=ft.Column(
                                tight=True,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Text(title, size=24, weight=ft.FontWeight.BOLD, color="#F9FAFB"),
                                    ft.Text(
                                        message,
                                        size=14,
                                        color="#CBD5E1",
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                ],
                            ),
                        ),
                    )
                ],
            )
        )
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
