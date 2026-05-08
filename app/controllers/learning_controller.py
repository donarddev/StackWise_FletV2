"""LearningController — renders the Hub once and updates results in place."""

from __future__ import annotations

import flet as ft

from app.controllers._layout_helper import wrap_with_layout
from app.controllers.base_controller import BaseController
from app.models.learning_article import LearningArticle
from app.utils.constants import Routes
from ui.components.input_field import input_field
from ui.dialogs.article_dialog import build_article_dialog
from ui.pages.learning_page import (
    build_learning_page,
    render_category_pills,
    render_learning_body,
)


class LearningController(BaseController):
    def __init__(self, page, container) -> None:
        super().__init__(page, container)
        self._search: str = ""
        self._category: str = "All"
        self._body_ref: ft.Ref[ft.Container] = ft.Ref()
        self._pills_ref: ft.Ref[ft.Container] = ft.Ref()

    def build(self) -> ft.Control:
        repo = self.container.learning_repository
        categories = repo.list_categories()
        articles = self._load_articles()

        search_field = input_field(
            "Search articles...", value=self._search, icon=ft.icons.SEARCH,
        )

        body = build_learning_page(
            articles=articles,
            categories=categories,
            selected_category=self._category,
            search_field=search_field,
            on_search_change=self._on_search_change,
            on_category_change=self._on_category_change,
            on_open_article=self._open_article,
            body_ref=self._body_ref,
            pills_ref=self._pills_ref,
        )
        return wrap_with_layout(self, current_route=Routes.LEARNING, body=body)

    # ---------- handlers ----------

    def _on_search_change(self, query: str) -> None:
        self._search = query
        self._refresh_inline()

    def _on_category_change(self, category: str) -> None:
        self._category = category
        self._search = ""
        self._refresh_inline(refresh_pills=True)

    def _open_article(self, article: LearningArticle) -> None:
        dialog = build_article_dialog(article, on_close=lambda _e: self._close_dialog())
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _close_dialog(self) -> None:
        if self.page.dialog is not None:
            self.page.dialog.open = False
            self.page.update()

    # ---------- in-place refresh ----------

    def _load_articles(self) -> list[LearningArticle]:
        repo = self.container.learning_repository
        if self._search.strip():
            return repo.search(self._search.strip())
        if self._category != "All":
            return repo.list_by_category(self._category)
        return repo.list_all()

    def _refresh_inline(self, *, refresh_pills: bool = False) -> None:
        articles = self._load_articles()
        body_container = self._body_ref.current
        if body_container is not None:
            body_container.content = render_learning_body(
                articles=articles, on_open_article=self._open_article,
            )
            body_container.update()

        if refresh_pills:
            pills_container = self._pills_ref.current
            if pills_container is not None:
                pills_container.content = render_category_pills(
                    categories=self.container.learning_repository.list_categories(),
                    selected_category=self._category,
                    on_category_change=self._on_category_change,
                )
                pills_container.update()
