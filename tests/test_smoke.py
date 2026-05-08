"""Smoke tests — exercise the most critical paths against a real MySQL DB.

These tests connect to the same MySQL server the app uses (Laragon by
default) but operate against a separate database name (``stackwise_ai_test``)
so they never touch production data. Tables are wiped between tests.

If MySQL is not reachable, the tests skip cleanly.
"""

from __future__ import annotations

import os
import unittest

from app.config.database_config import (
    FORBIDDEN_DATABASES,
    DatabaseConfig,
    is_forbidden_database,
)
from app.helpers.hash_helper import hash_password, verify_password
from app.repositories.recommendation_repository import RecommendationRepository
from app.repositories.user_repository import UserRepository
from app.requests.login_request import LoginRequest
from app.requests.recommendation_request import RecommendationRequest
from app.requests.register_request import RegisterRequest
from app.services.alternative_recommendation_service import (
    AlternativeRecommendationService,
)
from app.services.authentication_service import AuthenticationService
from app.services.confidence_score_service import ConfidenceScoreService
from app.services.database_service import DatabaseService
from app.services.explanation_service import ExplanationService
from app.services.recommendation_service import RecommendationService


TEST_DB_NAME = os.environ.get("STACKWISE_TEST_DB", "stackwise_ai_test")

# Final paranoid guard: never allow tests to run against a forbidden DB,
# even if someone misconfigures STACKWISE_TEST_DB.
assert not is_forbidden_database(TEST_DB_NAME), (
    f"Refusing to run tests against forbidden database '{TEST_DB_NAME}'."
)
assert "test" in TEST_DB_NAME.lower(), (
    f"Test DB name must contain 'test' (got '{TEST_DB_NAME}')."
)


class _NullChatbotService:
    """Stand-in for ChatbotService in tests."""

    def is_available(self) -> bool:
        return False

    def respond(self, *_a, **_kw):
        raise RuntimeError("not used in tests")

    def stream(self, *_a, **_kw):
        raise RuntimeError("not used in tests")

    def enrich_explanation(self, *_a, **_kw):
        return ""


class StackWiseSmokeTests(unittest.TestCase):
    db: DatabaseService

    @classmethod
    def setUpClass(cls) -> None:
        cfg = DatabaseConfig(
            driver="mysql",
            host=os.environ.get("STACKWISE_DB_HOST", "127.0.0.1"),
            port=int(os.environ.get("STACKWISE_DB_PORT", "3306")),
            user=os.environ.get("STACKWISE_DB_USER", "root"),
            password=os.environ.get("STACKWISE_DB_PASSWORD", ""),
            database=TEST_DB_NAME,
        )
        cls.db = DatabaseService(cfg)
        try:
            cls.db.connect()
        except RuntimeError as exc:
            raise unittest.SkipTest(
                f"MySQL not reachable for tests (expected on '{cfg.host}:{cfg.port}'): {exc}"
            )

    @classmethod
    def tearDownClass(cls) -> None:
        try:
            cls.db.close()
        except Exception:
            pass

    def setUp(self) -> None:
        # Use DELETE FROM (not TRUNCATE) to honor the project rule of
        # avoiding destructive DDL/DML statements. DELETE is logged and
        # FK-aware; we still wrap it with FK checks off to keep ordering
        # forgiving across schema evolution.
        self.db.execute("SET FOREIGN_KEY_CHECKS = 0")
        for table in (
            "chatbot_logs",
            "analytics",
            "recommendation_history",
            "recommendations",
            "users",
        ):
            self.db.execute(f"DELETE FROM {table}")
        self.db.execute("SET FOREIGN_KEY_CHECKS = 1")

    # ---------- tests ----------

    def test_password_hashing(self) -> None:
        h = hash_password("hunter2!")
        self.assertTrue(verify_password("hunter2!", h))
        self.assertFalse(verify_password("nope", h))

    def test_register_and_login(self) -> None:
        repo = UserRepository(self.db)
        auth = AuthenticationService(repo)

        register_request = RegisterRequest(
            full_name="Test Engineer",
            username="tester",
            email="tester@example.com",
            password="enchantress",
            confirm_password="enchantress",
        )
        result = auth.register(register_request)
        self.assertTrue(result.success, msg=result.errors)

        login_request = LoginRequest(identifier="tester", password="enchantress")
        login_result = auth.login(login_request)
        self.assertTrue(login_result.success)
        self.assertIsNotNone(login_result.user)
        self.assertEqual(login_result.user.email, "tester@example.com")  # type: ignore[union-attr]

    def test_duplicate_email_rejected(self) -> None:
        repo = UserRepository(self.db)
        auth = AuthenticationService(repo)

        first = auth.register(RegisterRequest(
            full_name="First",
            username="first_user",
            email="dup@example.com",
            password="password1",
            confirm_password="password1",
        ))
        self.assertTrue(first.success, msg=first.errors)

        second = auth.register(RegisterRequest(
            full_name="Second",
            username="second_user",
            email="dup@example.com",
            password="password2",
            confirm_password="password2",
        ))
        self.assertFalse(second.success)
        self.assertIn("email", second.errors or {})

    def test_recommendation_engine_and_persistence(self) -> None:
        repo = UserRepository(self.db)
        rec_repo = RecommendationRepository(self.db)

        user = repo.create(
            full_name="Test Engineer",
            username="tester2",
            email="tester2@example.com",
            password_hash=hash_password("password"),
        )

        service = RecommendationService(
            recommendation_repository=rec_repo,
            confidence_score_service=ConfidenceScoreService(),
            alternative_service=AlternativeRecommendationService(),
            explanation_service=ExplanationService(),
            chatbot_service=_NullChatbotService(),  # type: ignore[arg-type]
        )

        request = RecommendationRequest(
            project_name="Aurora",
            project_type="Web Application",
            project_goal="Production SaaS Product",
            complexity="Complex",
            team_size="Small (2–4)",
            timeline="3–6 months",
            scalability="High",
            security="Elevated",
            platform="Web",
            experience="Intermediate",
        )
        self.assertTrue(request.is_valid(), msg=request.errors)

        outcome = service.generate(request)
        self.assertTrue(outcome.recommended_language)
        self.assertTrue(outcome.recommended_framework)
        self.assertTrue(outcome.recommended_sdlc)
        self.assertGreaterEqual(outcome.confidence_score, 35)
        self.assertLessEqual(outcome.confidence_score, 99)
        self.assertIn("summary", outcome.explanation)
        self.assertIn("languages", outcome.alternatives)

        saved = service.save(user.id, request, outcome)
        self.assertEqual(saved.user_id, user.id)

        # Verify persistence round-trip.
        loaded = rec_repo.find_by_id(saved.id)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.project_name, "Aurora")  # type: ignore[union-attr]
        self.assertEqual(rec_repo.count_for_user(user.id), 1)

        # Analytics aggregation works with one row.
        avg = rec_repo.average_confidence(user.id)
        self.assertGreater(avg, 0)


if __name__ == "__main__":
    unittest.main()
