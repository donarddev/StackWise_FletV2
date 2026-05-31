"""ChatbotController."""

from __future__ import annotations

import threading
from typing import Any

import flet as ft

from app.controllers._layout_helper import wrap_with_layout
from app.controllers.base_controller import BaseController
from app.models.chatbot_log import ChatbotLog
from app.requests.chat_request import ChatRequest
from app.services.chatbot_service import ChatTurn
from app.utils.constants import Routes
from ui.components.toast import show_toast
from ui.pages.chatbot_page import build_chatbot_page
from ui.theme import get_theme, is_dark_mode
from ui.widgets.chat_bubble import chat_bubble, typing_bubble


def _scroll_chat_to_latest(col: ft.Column | None) -> None:
    """Keep newest messages in view after the transcript updates."""
    if col is None or col.page is None:
        return
    try:
        col.scroll_to(delta=1_000_000_000, duration=200)
    except Exception:
        pass


class ChatbotController(BaseController):
    def build(self) -> ft.Control:
        user = self.container.session.user
        assert user is not None

        history = self.container.chatbot_log_repository.list_for_user(user.id, limit=200)
        is_available = self.container.chatbot_service.is_available()

        input_ref = ft.Ref[ft.TextField]()
        messages_ref = ft.Ref[ft.Column]()

        def on_send(message: str) -> None:
            text = (message or "").strip()
            if not text:
                return

            self._append_message(messages_ref, role="user", content=text, author=user.full_name)
            self._append_typing(messages_ref)
            self.page.update()

            threading.Thread(
                target=self._handle_send,
                args=(user.id, user.full_name, text, messages_ref),
                daemon=True,
            ).start()

        def on_clear(_e: ft.ControlEvent) -> None:
            self.container.chatbot_log_repository.clear_for_user(user.id)
            show_toast(self.page, "Conversation cleared.", kind="success")
            self.navigation.to_chatbot()

        theme = get_theme(is_dark_mode(self.page))
        body = build_chatbot_page(
            theme=theme,
            user_name=user.full_name,
            history=history,
            is_ollama_available=is_available,
            input_field_ref=input_ref,
            messages_column_ref=messages_ref,
            on_send=on_send,
            on_clear=on_clear,
            page=self.page,
            user_avatar_url=user.avatar_url,
        )

        return wrap_with_layout(self, current_route=Routes.CHATBOT, body=body, theme=theme)

    # ---------- send pipeline ----------

    def _handle_send(
        self,
        user_id: int,
        user_name: str,
        message: str,
        messages_ref: ft.Ref[ft.Column],
    ) -> None:
        history = [
            ChatTurn(role=log.role, content=log.content)
            for log in self.container.chatbot_log_repository.list_for_user(user_id, limit=20)
            if log.role in {"user", "assistant"}
        ][:-1]  # drop the just-appended user message we already saved

        request = ChatRequest(message=message)
        response = self.container.chatbot_service.respond(
            user_id=user_id, request=request, history=history,
        )

        self._replace_typing_with_reply(
            messages_ref, content=response.content, author=user_name,
        )

    # ---------- view helpers ----------

    def _append_message(
        self,
        messages_ref: ft.Ref[ft.Column],
        *,
        role: str,
        content: str,
        author: str,
    ) -> None:
        col = messages_ref.current
        if col is None:
            return
        # If the welcome card is the only child, clear it.
        if len(col.controls) == 1 and not isinstance(col.controls[0], ft.Row):
            col.controls.clear()

        th = get_theme(is_dark_mode(self.page))
        u = self.container.session.user
        bubble_kw: dict[str, Any] = {
            "role": role,
            "content": content,
            "author_name": author,
            "theme": th,
            "page": self.page,
        }
        if role == "user" and u is not None:
            bubble_kw["user_avatar_url"] = u.avatar_url
        col.controls.append(chat_bubble(**bubble_kw))
        if col.page:
            col.update()
            _scroll_chat_to_latest(col)

    def _append_typing(self, messages_ref: ft.Ref[ft.Column]) -> None:
        col = messages_ref.current
        if col is None:
            return
        th = get_theme(is_dark_mode(self.page))
        col.controls.append(typing_bubble(th))
        if col.page:
            col.update()
            _scroll_chat_to_latest(col)

    def _replace_typing_with_reply(
        self,
        messages_ref: ft.Ref[ft.Column],
        *,
        content: str,
        author: str,
    ) -> None:
        col = messages_ref.current
        if col is None:
            return
        if col.controls and isinstance(col.controls[-1], ft.Row):
            col.controls.pop()
        th = get_theme(is_dark_mode(self.page))
        col.controls.append(
            chat_bubble(role="assistant", content=content, author_name=author, theme=th, page=self.page)
        )
        if col.page:
            col.update()
            _scroll_chat_to_latest(col)
