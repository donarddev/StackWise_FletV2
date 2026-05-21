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
from app.controllers.recommendation_controller import generate_recommendation_from_request
from app.helpers.date_helper import humanize, now_utc
from app.models.recommendation import Recommendation
from app.utils.constants import (
    Routes,
    SESSION_RECOMMENDATION_INPUT,
    SESSION_RECOMMENDATION_RESULT,
    SESSION_SELECTED_RECOMMENDATION_ID,
    confidence_label,
    recommendation_result_route,
)
from ui.components.input_field import input_field
from ui.components.toast import show_toast
from ui.dialogs.compare_dialog import build_compare_dialog
from ui.pages.history_page import (
    HistoryFilterKey,
    HistoryTabKey,
    apply_compare_button_state,
    build_filters_row,
    build_history_page,
    build_stats_row,
    build_trash_tabs_row,
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
        self._history_tab: HistoryTabKey = "active"
        self._selected_ids: set[int] = set()
        self._body_ref: ft.Ref[ft.Container] = ft.Ref()
        self._compare_btn_ref: ft.Ref[ft.Container] = ft.Ref()
        self._stats_ref: ft.Ref[ft.Container] = ft.Ref()
        self._filters_ref: ft.Ref[ft.Container] = ft.Ref()
        self._tabs_ref: ft.Ref[ft.Container] = ft.Ref()
        self._search_field_ref: ft.Ref[ft.TextField] = ft.Ref()
        self._compare_hint_ref: ft.Ref[ft.Text] = ft.Ref()
        self._load_error: Optional[str] = None
        self._cached_active: list[Recommendation] = []
        self._cached_deleted: list[Recommendation] = []

    def build(self) -> ft.Control:
        user = self.container.session.user
        assert user is not None

        self._reload_history_cache(user.id)
        active_items = self._cached_active
        stats = compute_history_stats(active_items)
        items = self._items_for_current_tab()
        items = self._apply_search(items, self._search)
        items = self._apply_history_filter(items, self._filter)

        theme = get_theme(is_dark_mode(self.page))
        hw = history_workspace_theme(theme)
        search_field = input_field(
            "Search",
            hint="Search by project, language, framework, SDLC...",
            value=self._search,
            icon=ft.icons.SEARCH,
            theme=hw,
            ref=self._search_field_ref,
        )

        body = build_history_page(
            theme=hw,
            items=items,
            selected_ids=self._selected_ids,
            stats=stats,
            active_filter=self._filter,
            history_tab=self._history_tab,
            search_field=search_field,
            on_search_change=self._on_search_change,
            on_filter=self._on_filter_change,
            on_clear_filters=self._on_clear_filters,
            on_tab_change=self._on_tab_change,
            on_view=self._show_detail,
            on_regenerate=self._regenerate,
            on_compare_select=self._set_compare_selected,
            on_delete=self._open_delete_confirm if self._history_tab == "active" else None,
            on_restore=self._open_restore_confirm if self._history_tab == "deleted" else None,
            on_compare=self._open_compare_dialog,
            on_new_recommendation=lambda _e: self.navigation.to_recommendation(),
            body_ref=self._body_ref,
            compare_btn_ref=self._compare_btn_ref,
            stats_ref=self._stats_ref,
            filters_ref=self._filters_ref,
            tabs_ref=self._tabs_ref,
            compare_hint_ref=self._compare_hint_ref,
        )

        return wrap_with_layout(self, current_route=Routes.HISTORY, body=body, theme=theme)

    # ---------- data access (controller API) ----------

    def get_active_recommendations(self, user_id: int) -> list[Recommendation]:
        return self.container.recommendation_history_service.get_active_recommendations(
            user_id, limit=500
        )

    def get_deleted_recommendations(self, user_id: int) -> list[Recommendation]:
        return self.container.recommendation_history_service.get_deleted_recommendations(
            user_id, limit=500
        )

    def delete_recommendation_record(self, user_id: int, recommendation_id: int) -> bool:
        return self.container.recommendation_history_service.soft_delete(
            user_id, recommendation_id
        )

    def restore_recommendation_record(self, user_id: int, recommendation_id: int) -> bool:
        return self.container.recommendation_history_service.restore(
            user_id, recommendation_id
        )

    def _reload_history_cache(self, user_id: int) -> None:
        self._cached_active = self.get_active_recommendations(user_id)
        self._cached_deleted = self.get_deleted_recommendations(user_id)

    def _items_for_current_tab(self) -> list[Recommendation]:
        if self._history_tab == "deleted":
            return list(self._cached_deleted)
        return list(self._cached_active)

    # ---------- handlers ----------

    def _on_tab_change(self, tab: HistoryTabKey) -> None:
        if tab == self._history_tab:
            return
        self._history_tab = tab
        self._selected_ids.clear()
        user = self.container.session.user
        if user is not None:
            self._reload_history_cache(user.id)
        self.refresh_history_list()

    def _on_search_change(self, query: str) -> None:
        self._search = query
        self.refresh_history_list(from_cache_only=True)

    def _on_filter_change(self, key: HistoryFilterKey) -> None:
        self._filter = key
        self.refresh_history_list(from_cache_only=True)

    def _on_clear_filters(self, _e: ft.ControlEvent) -> None:
        self._search = ""
        self._filter = "all"
        sf = self._search_field_ref.current
        if sf is not None:
            sf.value = ""
            if sf.page:
                sf.update()
        self.refresh_history_list(from_cache_only=True)

    def _set_compare_selected(self, rec: Recommendation, checked: bool) -> None:
        if self._history_tab != "active":
            return
        if checked:
            if rec.id in self._selected_ids:
                return
            if len(self._selected_ids) >= 2:
                show_toast(self.page, "Please select exactly two recommendations to compare.", kind="warning")
                self.refresh_history_list(from_cache_only=True)
                return
            self._selected_ids.add(rec.id)
        else:
            self._selected_ids.discard(rec.id)
        self.refresh_history_list(from_cache_only=True)

    def _open_compare_dialog(self, _e: ft.ControlEvent) -> None:
        if self._history_tab != "active":
            return
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
        self.navigation.to_recommendation_result(rec.id)

    def _open_delete_confirm(self, rec: Recommendation) -> None:
        user = self.container.session.user
        if user is None:
            return

        def cancel(_: ft.ControlEvent) -> None:
            self._close_dialog()

        def go(_: ft.ControlEvent) -> None:
            self._close_dialog()
            if not self.delete_recommendation_record(user.id, rec.id):
                show_toast(
                    self.page,
                    "Unable to delete recommendation. Please try again.",
                    kind="warning",
                )
                return
            self._selected_ids.discard(rec.id)
            self._reload_history_cache(user.id)
            show_toast(self.page, "Recommendation moved to Recently Deleted.", kind="success")
            self.refresh_history_list()

        dlg = ft.AlertDialog(
            modal=True,
            bgcolor=Colors.surface_2,
            alignment=ft.alignment.center,
            shape=ft.RoundedRectangleBorder(radius=Radii.lg),
            title=ft.Text("Delete recommendation?", weight=ft.FontWeight.W_600),
            content=ft.Container(
                width=400,
                content=ft.Text(
                    "This recommendation will be moved to Recently Deleted. "
                    "You can restore it later.",
                    style=Typography.body(size=14),
                ),
            ),
            actions=[
                ft.TextButton("Cancel", on_click=cancel),
                ft.TextButton(
                    "Move to Trash",
                    icon=ft.icons.DELETE_OUTLINE,
                    icon_color=Colors.danger,
                    style=ft.ButtonStyle(color=Colors.danger),
                    on_click=go,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self._open_dialog(dlg)

    def _open_restore_confirm(self, rec: Recommendation) -> None:
        user = self.container.session.user
        if user is None:
            return

        def cancel(_: ft.ControlEvent) -> None:
            self._close_dialog()

        def go(_: ft.ControlEvent) -> None:
            self._close_dialog()
            if not self.restore_recommendation_record(user.id, rec.id):
                show_toast(
                    self.page,
                    "Unable to restore recommendation. Please try again.",
                    kind="warning",
                )
                return
            self._reload_history_cache(user.id)
            show_toast(self.page, "Recommendation restored successfully.", kind="success")
            self.refresh_history_list()

        dlg = ft.AlertDialog(
            modal=True,
            bgcolor=Colors.surface_2,
            alignment=ft.alignment.center,
            shape=ft.RoundedRectangleBorder(radius=Radii.lg),
            title=ft.Text("Restore recommendation?", weight=ft.FontWeight.W_600),
            content=ft.Container(
                width=400,
                content=ft.Text(
                    "This recommendation will appear again in History and Dashboard.",
                    style=Typography.body(size=14),
                ),
            ),
            actions=[
                ft.TextButton("Cancel", on_click=cancel),
                ft.TextButton(
                    "Restore",
                    icon=ft.icons.RESTORE_FROM_TRASH_OUTLINED,
                    on_click=go,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self._open_dialog(dlg)

    def _regenerate(self, rec: Recommendation) -> None:
        user = self.container.session.user
        if user is None:
            show_toast(self.page, "Please sign in again.", kind="warning")
            return
        input_data = (
            self.container.recommendation_persistence.input_data_from_recommendation(rec)
        )
        response = generate_recommendation_from_request(input_data)
        if not response.get("success"):
            show_toast(
                self.page,
                response.get("error") or "Regeneration could not be completed.",
                kind="warning",
            )
            return
        try:
            new_rec = self.container.recommendation_persistence.save_engine_result(
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
        self.page.session.set(SESSION_RECOMMENDATION_INPUT, input_data)
        self.page.session.set(SESSION_RECOMMENDATION_RESULT, response["data"])
        self.page.session.set(SESSION_SELECTED_RECOMMENDATION_ID, new_rec.id)
        show_toast(self.page, "Recommendation regenerated.", kind="success")
        self._reload_history_cache(user.id)
        self.refresh_history_list()
        self.page.go(recommendation_result_route(new_rec.id))

    # ---------- in-place refresh ----------

    def refresh_history_list(self, *, from_cache_only: bool = False) -> None:
        """Reload list rows for the current tab, search, and filters without navigating away."""
        user = self.container.session.user
        if user is None:
            return

        sf = self._search_field_ref.current
        if sf is not None:
            self._search = sf.value or ""

        try:
            if not from_cache_only:
                self._reload_history_cache(user.id)
            all_items = self._items_for_current_tab()
            active_items = self._cached_active
            self._load_error = None
        except Exception as exc:
            self._load_error = str(exc) or "Something went wrong while loading history."
            all_items = []
            active_items = []

        stats = compute_history_stats(active_items)
        if self._load_error:
            items: list[Recommendation] = []
        else:
            items = self._apply_search(all_items, self._search)
            items = self._apply_history_filter(items, self._filter)

        th = history_workspace_theme(get_theme(is_dark_mode(self.page)))
        updated_any = False

        body_container = self._body_ref.current
        if body_container is not None:
            body_container.content = render_history_body(
                theme=th,
                items=items,
                selected_ids=self._selected_ids,
                search_query=self._search,
                active_filter=self._filter,
                history_tab=self._history_tab,
                on_view=self._show_detail,
                on_regenerate=self._regenerate,
                on_compare_select=self._set_compare_selected,
                on_delete=self._open_delete_confirm if self._history_tab == "active" else None,
                on_restore=self._open_restore_confirm if self._history_tab == "deleted" else None,
                on_new_recommendation=lambda _e: self.navigation.to_recommendation(),
                error_message=self._load_error,
                on_retry_load=self._retry_history_load,
            )
            if body_container.page:
                body_container.update()
            updated_any = True

        stats_host = self._stats_ref.current
        if stats_host is not None:
            stats_host.content = build_stats_row(stats, th)
            if stats_host.page:
                stats_host.update()
            updated_any = True

        tabs_host = self._tabs_ref.current
        if tabs_host is not None:
            tabs_host.content = build_trash_tabs_row(
                theme=th,
                active=self._history_tab,
                on_tab=self._on_tab_change,
            )
            if tabs_host.page:
                tabs_host.update()
            updated_any = True

        filters_host = self._filters_ref.current
        if filters_host is not None:
            show_clear = bool(self._search.strip()) or self._filter != "all"
            filters_host.content = build_filters_row(
                theme=th,
                active=self._filter,
                on_filter=self._on_filter_change,
                show_clear=show_clear,
                on_clear=self._on_clear_filters,
            )
            if filters_host.page:
                filters_host.update()
            updated_any = True

        compare_btn = self._compare_btn_ref.current
        if compare_btn is not None:
            show_compare = self._history_tab == "active"
            compare_btn.visible = show_compare
            if show_compare:
                apply_compare_button_state(compare_btn, self._selected_ids, self._open_compare_dialog)
            if compare_btn.page:
                compare_btn.update()
            updated_any = True

        self._sync_compare_hint()

        if updated_any and self.page:
            self.page.update()

    def _retry_history_load(self, _e: ft.ControlEvent) -> None:
        self._load_error = None
        self.refresh_history_list()

    def _sync_compare_hint(self) -> None:
        tx = self._compare_hint_ref.current
        if tx is None:
            return
        if self._history_tab != "active":
            tx.value = ""
            tx.visible = False
        else:
            n = len(self._selected_ids)
            tx.value = "" if n == 2 else "Select two records to compare."
            tx.visible = n != 2
        if tx.page:
            tx.update()

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
        out: list[Recommendation] = []
        for r in items:
            label = confidence_label(r.confidence_score).lower()
            created = humanize(r.created_at).lower()
            deleted = humanize(r.deleted_at).lower() if r.deleted_at else ""
            if (
                q in r.project_name.lower()
                or q in r.project_type.lower()
                or q in r.recommended_language.lower()
                or q in r.recommended_framework.lower()
                or q in r.recommended_sdlc.lower()
                or q in label
                or q in created
                or (deleted and q in deleted)
            ):
                out.append(r)
        return out

    # ---------- dialog plumbing ----------

    def _open_dialog(self, dialog: ft.AlertDialog) -> None:
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _close_dialog(self) -> None:
        if self.page.dialog is not None:
            self.page.dialog.open = False
            self.page.update()
