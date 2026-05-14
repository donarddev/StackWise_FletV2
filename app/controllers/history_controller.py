"""HistoryController.

Renders the history page once and then **updates sections in place**
(search results, compare CTA, stats, filter chips) so the search field keeps
focus and caret position.
"""

from __future__ import annotations

from datetime import timedelta, timezone
from typing import Optional

import flet as ft

from app.controllers._layout_helper import wrap_with_layout
from app.controllers.base_controller import BaseController
from app.helpers.date_helper import now_utc
from app.models.recommendation import Recommendation
from app.utils.constants import Routes
from ui.components.input_field import input_field
from ui.components.toast import show_toast
from ui.dialogs.compare_dialog import build_compare_dialog
from ui.dialogs.recommendation_detail_dialog import (
    build_recommendation_detail_dialog,
    build_summary_clipboard_text,
)
from ui.pages.history_page import (
    HistoryFilterKey,
    apply_compare_button_state,
    build_filters_row,
    build_history_page,
    build_stats_row,
    compute_history_stats,
    history_workspace_theme,
    render_history_body,
)
from ui.theme import get_theme, is_dark_mode
from ui.themes.app_theme import Colors, Radii, Typography


class HistoryController(BaseController):
    def __init__(self, page, container) -> None:
        super().__init__(page, container)
        self._search: str = ""
        self._filter: HistoryFilterKey = "all"
        self._selected_ids: set[int] = set()
        self._body_ref: ft.Ref[ft.Container] = ft.Ref()
        self._compare_btn_ref: ft.Ref[ft.Container] = ft.Ref()
        self._stats_ref: ft.Ref[ft.Container] = ft.Ref()
        self._filters_ref: ft.Ref[ft.Container] = ft.Ref()
        self._search_field_ref: ft.Ref[ft.TextField] = ft.Ref()
        self._compare_hint_ref: ft.Ref[ft.Text] = ft.Ref()
        self._load_error: Optional[str] = None

    def build(self) -> ft.Control:
        user = self.container.session.user
        assert user is not None

        all_items = self.container.recommendation_repository.list_for_user(user.id, limit=500)
        stats = compute_history_stats(all_items)
        items = self._apply_search(all_items, self._search)
        items = self._apply_history_filter(items, self._filter)

        theme = get_theme(is_dark_mode(self.page))
        hw = history_workspace_theme(theme)
        search_field = input_field(
            "Search",
            hint="Search by project, language, framework, SDLC...",
            value=self._search,
            icon=ft.icons.SEARCH,
            theme=hw,
        )
        search_field.ref = self._search_field_ref

        body = build_history_page(
            theme=hw,
            items=items,
            selected_ids=self._selected_ids,
            stats=stats,
            active_filter=self._filter,
            search_field=search_field,
            on_search_change=self._on_search_change,
            on_filter=self._on_filter_change,
            on_clear_filters=self._on_clear_filters,
            on_view=self._show_detail,
            on_regenerate=self._regenerate,
            on_compare_select=self._set_compare_selected,
            on_delete=self._open_delete_confirm,
            on_compare=self._open_compare_dialog,
            on_new_recommendation=lambda _e: self.navigation.to_recommendation(),
            body_ref=self._body_ref,
            compare_btn_ref=self._compare_btn_ref,
            stats_ref=self._stats_ref,
            filters_ref=self._filters_ref,
            compare_hint_ref=self._compare_hint_ref,
        )

        return wrap_with_layout(self, current_route=Routes.HISTORY, body=body, theme=theme)

    # ---------- handlers ----------

    def _on_search_change(self, query: str) -> None:
        self._search = query
        self._refresh_results_inline()

    def _on_filter_change(self, key: HistoryFilterKey) -> None:
        self._filter = key
        self._refresh_results_inline()

    def _on_clear_filters(self, _e: ft.ControlEvent) -> None:
        self._search = ""
        self._filter = "all"
        sf = self._search_field_ref.current
        if sf is not None:
            sf.value = ""
            if sf.page:
                sf.update()
        self._refresh_results_inline()

    def _set_compare_selected(self, rec: Recommendation, checked: bool) -> None:
        if checked:
            if rec.id in self._selected_ids:
                return
            if len(self._selected_ids) >= 2:
                show_toast(self.page, "Please select exactly two recommendations to compare.", kind="warning")
                self._refresh_results_inline()
                return
            self._selected_ids.add(rec.id)
        else:
            self._selected_ids.discard(rec.id)
        self._refresh_results_inline()

    def _open_compare_dialog(self, _e: ft.ControlEvent) -> None:
        if len(self._selected_ids) != 2:
            show_toast(self.page, "Please select exactly two recommendations to compare.", kind="warning")
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

        def on_close(_: ft.ControlEvent) -> None:
            self._close_dialog()

        def on_copy(_: ft.ControlEvent) -> None:
            text = build_summary_clipboard_text(rec)
            self.page.set_clipboard(text)
            show_toast(self.page, "Summary copied to clipboard.", kind="success")

        def on_regen(_: ft.ControlEvent) -> None:
            self._close_dialog()
            self._open_regenerate_confirm(rec)

        def on_del(_: ft.ControlEvent) -> None:
            self._close_dialog()
            self._open_delete_confirm(rec)

        dialog = build_recommendation_detail_dialog(
            rec,
            on_close=on_close,
            on_regenerate=on_regen,
            on_delete=on_del,
            on_copy_summary=on_copy,
            show_regenerate_hint=True,
        )
        self._open_dialog(dialog)

    def _open_regenerate_confirm(self, rec: Recommendation) -> None:
        def cancel(_: ft.ControlEvent) -> None:
            self._close_dialog()

        def go(_: ft.ControlEvent) -> None:
            self._close_dialog()
            self._regenerate(rec)

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
                    "project profile when available; otherwise stored form fields are used. "
                    "A new recommendation row will be added to your history.",
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

    def _open_delete_confirm(self, rec: Recommendation) -> None:
        user = self.container.session.user
        if user is None:
            return

        def cancel(_: ft.ControlEvent) -> None:
            self._close_dialog()

        def go(_: ft.ControlEvent) -> None:
            self._close_dialog()
            self.container.recommendation_repository.delete(rec.id, user.id)
            self._selected_ids.discard(rec.id)
            show_toast(self.page, "Recommendation deleted.", kind="success")
            self._refresh_results_inline()

        dlg = ft.AlertDialog(
            modal=True,
            bgcolor=Colors.surface_2,
            alignment=ft.alignment.center,
            shape=ft.RoundedRectangleBorder(radius=Radii.lg),
            title=ft.Text("Delete recommendation?", weight=ft.FontWeight.W_600),
            content=ft.Container(
                width=400,
                content=ft.Text(
                    "This will remove this history record from your saved recommendations.",
                    style=Typography.body(size=14),
                ),
            ),
            actions=[
                ft.TextButton("Cancel", on_click=cancel),
                ft.TextButton(
                    "Delete",
                    icon=ft.icons.DELETE_OUTLINE,
                    icon_color=Colors.danger,
                    style=ft.ButtonStyle(color=Colors.danger),
                    on_click=go,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self._open_dialog(dlg)

    def _regenerate(self, rec: Recommendation) -> None:
        user = self.container.session.user
        if user is None:
            return
        new_rec = self.container.recommendation_service.regenerate(user.id, rec.id)
        if new_rec is not None:
            show_toast(self.page, "Recommendation regenerated.", kind="success")
            self._refresh_results_inline()
        else:
            show_toast(self.page, "Regeneration could not be completed.", kind="warning")

    # ---------- in-place refresh ----------

    def _retry_history_load(self, _e: ft.ControlEvent) -> None:
        self._load_error = None
        self._refresh_results_inline()

    def _sync_compare_hint(self) -> None:
        tx = self._compare_hint_ref.current
        if tx is None:
            return
        n = len(self._selected_ids)
        tx.value = "" if n == 2 else "Select two records to compare."
        tx.visible = n != 2
        if tx.page:
            tx.update()

    def _refresh_results_inline(self) -> None:
        """Replace table body, stats, filter chrome, and compare CTA without rebuilding the page."""
        user = self.container.session.user
        if user is None:
            return

        try:
            all_items = self.container.recommendation_repository.list_for_user(user.id, limit=500)
            self._load_error = None
        except Exception as exc:
            self._load_error = str(exc) or "Something went wrong while loading history."
            all_items = []

        stats = compute_history_stats(all_items)
        if self._load_error:
            items: list[Recommendation] = []
        else:
            items = self._apply_search(all_items, self._search)
            items = self._apply_history_filter(items, self._filter)

        th = history_workspace_theme(get_theme(is_dark_mode(self.page)))
        body_container = self._body_ref.current
        if body_container is not None:
            body_container.content = render_history_body(
                theme=th,
                items=items,
                selected_ids=self._selected_ids,
                search_query=self._search,
                active_filter=self._filter,
                on_view=self._show_detail,
                on_regenerate=self._regenerate,
                on_compare_select=self._set_compare_selected,
                on_delete=self._open_delete_confirm,
                on_new_recommendation=lambda _e: self.navigation.to_recommendation(),
                error_message=self._load_error,
                on_retry_load=self._retry_history_load,
            )
            if body_container.page:
                body_container.update()

        stats_host = self._stats_ref.current
        if stats_host is not None:
            stats_host.content = build_stats_row(stats, th)
            if stats_host.page:
                stats_host.update()

        filters_host = self._filters_ref.current
        if filters_host is not None:
            sf = self._search_field_ref.current
            q = (sf.value if sf is not None else self._search) or ""
            show_clear = bool(q.strip()) or self._filter != "all"
            filters_host.content = build_filters_row(
                theme=th,
                active=self._filter,
                on_filter=self._on_filter_change,
                show_clear=show_clear,
                on_clear=self._on_clear_filters,
            )
            if filters_host.page:
                filters_host.update()

        compare_btn = self._compare_btn_ref.current
        if compare_btn is not None:
            apply_compare_button_state(compare_btn, self._selected_ids, self._open_compare_dialog)
            if compare_btn.page:
                compare_btn.update()

        self._sync_compare_hint()

    def _apply_history_filter(self, items: list[Recommendation], key: HistoryFilterKey) -> list[Recommendation]:
        if key == "all":
            return items
        if key == "high":
            return [r for r in items if r.confidence_score >= 80]
        if key == "moderate":
            return [r for r in items if 45 <= r.confidence_score < 80]
        if key == "low":
            return [r for r in items if r.confidence_score < 45]
        if key == "recent":
            cutoff = now_utc() - timedelta(days=7)
            out: list[Recommendation] = []
            for r in items:
                dt = r.created_at
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                else:
                    dt = dt.astimezone(timezone.utc)
                if dt >= cutoff:
                    out.append(r)
            return out
        return items

    @staticmethod
    def _apply_search(items: list[Recommendation], query: str) -> list[Recommendation]:
        q = (query or "").strip().lower()
        if not q:
            return items
        return [
            r
            for r in items
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
