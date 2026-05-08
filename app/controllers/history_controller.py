"""HistoryController.

Renders the history page once and then **updates the results body in place**
on every search keystroke or compare-toggle. This keeps the search field
focused with its caret position intact (instead of rebuilding the whole
page on every event).
"""

from __future__ import annotations

import flet as ft

from app.controllers._layout_helper import wrap_with_layout
from app.controllers.base_controller import BaseController
from app.models.recommendation import Recommendation
from app.utils.constants import Routes
from ui.components.input_field import input_field
from ui.components.toast import show_toast
from ui.dialogs.compare_dialog import build_compare_dialog
from ui.dialogs.recommendation_detail_dialog import build_recommendation_detail_dialog
from ui.pages.history_page import build_history_page, render_history_body


class HistoryController(BaseController):
    def __init__(self, page, container) -> None:
        super().__init__(page, container)
        self._search: str = ""
        self._selected_ids: set[int] = set()
        # Refs for in-place updates — they survive page rebuilds.
        self._body_ref: ft.Ref[ft.Container] = ft.Ref()
        self._compare_btn_ref: ft.Ref[ft.ElevatedButton] = ft.Ref()

    def build(self) -> ft.Control:
        user = self.container.session.user
        assert user is not None

        items = self._load_filtered_items(user.id)

        search_field = input_field(
            "Search by project, language, framework, SDLC...",
            value=self._search,
            icon=ft.icons.SEARCH,
        )

        body = build_history_page(
            items=items,
            selected_ids=self._selected_ids,
            search_field=search_field,
            on_search_change=self._on_search_change,
            on_view=self._show_detail,
            on_regenerate=self._regenerate,
            on_compare_toggle=self._toggle_compare,
            on_compare=self._open_compare_dialog,
            on_new_recommendation=lambda _e: self.navigation.to_recommendation(),
            body_ref=self._body_ref,
            compare_btn_ref=self._compare_btn_ref,
        )

        return wrap_with_layout(self, current_route=Routes.HISTORY, body=body)

    # ---------- handlers ----------

    def _on_search_change(self, query: str) -> None:
        self._search = query
        self._refresh_results_inline()

    def _toggle_compare(self, rec: Recommendation) -> None:
        if rec.id in self._selected_ids:
            self._selected_ids.remove(rec.id)
        else:
            if len(self._selected_ids) >= 2:
                show_toast(self.page, "Select exactly two recommendations to compare.", kind="warning")
                return
            self._selected_ids.add(rec.id)
        self._refresh_results_inline()

    def _open_compare_dialog(self, _e: ft.ControlEvent) -> None:
        if len(self._selected_ids) != 2:
            show_toast(self.page, "Select exactly two recommendations to compare.", kind="warning")
            return
        ids = list(self._selected_ids)
        left = self.container.recommendation_repository.find_by_id(ids[0])
        right = self.container.recommendation_repository.find_by_id(ids[1])
        if not left or not right:
            return
        dialog = build_compare_dialog(left, right, on_close=lambda _e: self._close_dialog())
        self._open_dialog(dialog)

    def _show_detail(self, rec: Recommendation) -> None:
        user = self.container.session.user
        if user is not None:
            self.container.recommendation_repository.add_history(user.id, rec.id, "viewed")
        dialog = build_recommendation_detail_dialog(rec, on_close=lambda _e: self._close_dialog())
        self._open_dialog(dialog)

    def _regenerate(self, rec: Recommendation) -> None:
        user = self.container.session.user
        if user is None:
            return
        new_rec = self.container.recommendation_service.regenerate(user.id, rec.id)
        if new_rec is not None:
            show_toast(self.page, "Recommendation regenerated.", kind="success")
            self._refresh_results_inline()

    # ---------- in-place refresh ----------

    def _refresh_results_inline(self) -> None:
        """Replace just the body container's content + the compare button's
        disabled state — without rebuilding the rest of the page."""
        user = self.container.session.user
        if user is None:
            return

        items = self._load_filtered_items(user.id)

        body_container = self._body_ref.current
        if body_container is not None:
            body_container.content = render_history_body(
                items=items,
                selected_ids=self._selected_ids,
                search_query=self._search,
                on_view=self._show_detail,
                on_regenerate=self._regenerate,
                on_compare_toggle=self._toggle_compare,
                on_new_recommendation=lambda _e: self.navigation.to_recommendation(),
            )
            body_container.update()

        compare_btn = self._compare_btn_ref.current
        if compare_btn is not None:
            compare_btn.disabled = len(self._selected_ids) != 2
            compare_btn.update()

    def _load_filtered_items(self, user_id: int) -> list[Recommendation]:
        all_items = self.container.recommendation_repository.list_for_user(user_id, limit=500)
        return self._apply_search(all_items, self._search)

    @staticmethod
    def _apply_search(items: list[Recommendation], query: str) -> list[Recommendation]:
        q = (query or "").strip().lower()
        if not q:
            return items
        return [
            r for r in items
            if q in r.project_name.lower()
            or q in r.recommended_language.lower()
            or q in r.recommended_framework.lower()
            or q in r.recommended_sdlc.lower()
            or q in r.project_type.lower()
        ]

    # ---------- dialog plumbing ----------

    def _open_dialog(self, dialog: ft.AlertDialog) -> None:
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _close_dialog(self) -> None:
        if self.page.dialog is not None:
            self.page.dialog.open = False
            self.page.update()
