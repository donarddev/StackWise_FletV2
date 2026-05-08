"""BaseController — shared infrastructure for all controllers.

Controllers in StackWise have a single job: take dependencies (page, container),
build a *view* using UI builders, and forward user events to services. They
must NOT contain business logic or directly query the database.
"""

from __future__ import annotations

import flet as ft

from app.core.container import Container
from app.services.navigation_service import NavigationService


class BaseController:
    def __init__(self, page: ft.Page, container: Container) -> None:
        self.page = page
        self.container = container
        self.navigation = NavigationService(page)
